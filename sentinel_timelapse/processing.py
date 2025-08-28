"""
Image processing utilities for Sentinel-2 asset clipping and manipulation.

This module provides functions for downloading, clipping, and processing
Sentinel-2 satellite imagery assets. It handles coordinate transformations,
raster clipping operations, and file output in various formats.
"""

import planetary_computer
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
from rasterio.coords import BoundingBox
import os
import geopandas as gpd
from shapely.geometry import box
from typing import Dict, Any, Optional

# Flag to track if geospatial environment has been initialized
_geo_initialized = False


def _ensure_geo_initialized() -> None:
    """Ensure the geospatial environment is properly initialized."""
    global _geo_initialized
    if not _geo_initialized:
        try:
            from ._bootstrap_geo import use_rasterio_bundled_data

            use_rasterio_bundled_data(verbose=False)
            _geo_initialized = True
        except ImportError:
            # If bootstrap fails, continue without it
            pass


def clipped_asset(
    item: Any,
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
    input_crs: str = "EPSG:24879",
    bounds_crs: str = "EPSG:32719",
    asset_name: str = "visual",
    prefix: str = "clipped",
    return_data_dic: bool = False,
    save_tiff: bool = False,
    out_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Clip a Sentinel-2 asset to specified geographic bounds.

    This function downloads a specific asset (band or composite) from a Sentinel-2
    STAC item and clips it to the specified bounding box. It handles coordinate
    system transformations and can output the data in various formats including
    in-memory arrays and GeoTIFF files.

    Args:
        item: STAC item object containing metadata and asset references for a
              Sentinel-2 image acquisition
        xmin: Minimum x-coordinate of the clipping bounds in input_crs
        ymin: Minimum y-coordinate of the clipping bounds in input_crs
        xmax: Maximum x-coordinate of the clipping bounds in input_crs
        ymax: Maximum y-coordinate of the clipping bounds in input_crs
        input_crs: Coordinate reference system of the input bounds.
                  Default is 'EPSG:24879' (UTM zone 19S)
        bounds_crs: Target coordinate reference system for the clipping operation.
                   Default is 'EPSG:32719' (UTM zone 19S)
        asset_name: Name of the Sentinel-2 asset to clip. Common options include:
                   - 'visual': True color composite (RGB)
                   - 'B04': Red band (665nm)
                   - 'B03': Green band (560nm)
                   - 'B02': Blue band (490nm)
                   - 'SCL': Scene Classification Layer
                   Default is 'visual'
        prefix: Prefix for output filename when saving to disk
        return_data_dic: If True, return data as a dictionary containing the
                        clipped array, profile metadata, and source href.
                        If False, only save to disk (if save_tiff=True)
        save_tiff: If True, save the clipped data as a GeoTIFF file
        out_path: Output directory path for saved files. If None, uses prefix

    Returns:
        dict or None: If return_data_dic=True, returns a dictionary with:
                     - 'data': numpy array of the clipped image data
                     - 'profile': rasterio profile with updated metadata
                     - 'href': source URL of the asset
                     If return_data_dic=False, returns None

    Raises:
        ValueError: If the specified bounds don't intersect with the image extent
        rasterio.errors.RasterioIOError: If the asset file cannot be accessed
        KeyError: If the specified asset_name is not available in the STAC item
        RuntimeError: If coordinate transformation fails

    Example:
        >>> # Clip visual asset to a mining area
        >>> result = clipped_asset(
        ...     item=stac_item,
        ...     xmin=407500, ymin=7494500, xmax=415200, ymax=7505700,
        ...     input_crs='EPSG:24879',
        ...     asset_name='visual',
        ...     return_data_dic=True
        ... )
        >>> print(f"Clipped data shape: {result['data'].shape}")

        >>> # Save as GeoTIFF
        >>> clipped_asset(
        ...     item=stac_item,
        ...     xmin=407500, ymin=7494500, xmax=415200, ymax=7505700,
        ...     asset_name='B04',
        ...     save_tiff=True,
        ...     out_path='output/'
        ... )
    """
    # Ensure geospatial environment is initialized
    _ensure_geo_initialized()

    # Transform bounds from input CRS to clipping CRS if they differ
    # This ensures the clipping operation uses the correct coordinate system
    if input_crs != bounds_crs:
        # Create a Shapely geometry from the input bounds
        geom = box(xmin, ymin, xmax, ymax)

        # Create a GeoDataFrame for coordinate transformation
        gdf = gpd.GeoDataFrame({"geometry": [geom]}, crs=input_crs)

        # Transform to the target CRS
        gdf_transformed = gdf.to_crs(bounds_crs)

        # Extract the transformed bounds
        bounds_geom = gdf_transformed.geometry.iloc[0]
        xmin, ymin, xmax, ymax = bounds_geom.bounds

    # Sign the STAC item to get authenticated access to the asset
    # Planetary Computer requires signing for data access
    signed_item = planetary_computer.sign(item)

    # Get the specific asset from the signed item
    visual_asset = signed_item.assets[asset_name]
    href = visual_asset.href

    try:
        # Open the raster file using rasterio
        with rasterio.open(href) as src:
            # Get source metadata
            src_crs = src.crs
            src_bounds = src.bounds

            # Transform the clipping bounds to the source image's CRS
            # This ensures we can properly extract the correct window
            transformed_bounds = transform_bounds(
                bounds_crs, src_crs, xmin, ymin, xmax, ymax
            )
            bounds = BoundingBox(*transformed_bounds)

            # Check if the requested bounds intersect with the image extent
            # This prevents errors when trying to clip outside the image area
            if not (
                bounds.left < src_bounds.right
                and bounds.right > src_bounds.left
                and bounds.bottom < src_bounds.top
                and bounds.top > src_bounds.bottom
            ):
                raise ValueError(
                    f"Provided bounds {bounds} do not intersect with\
                          image extent {src_bounds}."
                )

            # Calculate the raster window that corresponds to our geographic bounds
            window = from_bounds(
                left=bounds.left,
                bottom=bounds.bottom,
                right=bounds.right,
                top=bounds.top,
                transform=src.transform,
            )

            # Read the data for the specified window
            data = src.read(window=window)

            # Create an updated profile for the clipped data
            profile = src.profile.copy()
            profile.update(
                {
                    "width": data.shape[2],  # Number of columns in clipped data
                    "height": data.shape[1],  # Number of rows in clipped data
                    "transform": src.window_transform(window),  # Updated geotransform
                    "crs": src_crs,  # Source coordinate reference system
                    "driver": "GTiff",  # Output format
                    "tiled": True,  # Enable tiling for better performance
                    "compress": "deflate",  # Use deflate compression
                    "interleave": "band",  # Band-interleaved format
                }
            )

            # Return data dictionary if requested
            if return_data_dic:
                return {"data": data, "profile": profile, "href": href}

            # Handle file output if save_tiff is enabled
            if not out_path:
                out_path = prefix

            # Create output directory if it doesn't exist
            if not os.path.exists(out_path):
                os.mkdir(out_path)

            # Generate output filename using item ID and asset name
            # Extract timestamp from item ID for unique filenames
            out_file = os.path.join(
                out_path, f'{prefix}_{asset_name}_{item.id.split("_")[2]}.tif'
            )

            # Save as GeoTIFF if requested
            if save_tiff:
                with rasterio.open(out_file, "w", **profile) as dst:
                    # Write the clipped data to the output file
                    dst.write(data)

                    # Add metadata tags to the output file
                    dst.update_tags(
                        description=f"Clipped Sentinel-2 visual {asset_name}\
                              from Planetary Computer",
                        creation_date=item.properties["datetime"],
                        source="Sentinel-2",
                        href=item.assets[asset_name].href,
                    )
                print(out_file, "saved.")

    except rasterio.errors.RasterioIOError as e:
        # Handle file access errors (network issues, missing files, etc.)
        print(f"Rasterio error: {e}")
    except ValueError as e:
        # Handle bounds intersection errors
        print(f"Error: {e}")
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error: {e}")

    return None
