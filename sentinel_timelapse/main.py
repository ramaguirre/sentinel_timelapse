"""
Main module for Sentinel timelapse image processing.

This module provides the primary interface for downloading and processing
Sentinel-2 satellite imagery for timelapse creation. It orchestrates the
entire workflow from STAC search to final image clipping and saving.
"""

from datetime import datetime
import os
from typing import Union, List
import geopandas as gpd
from shapely.geometry import box

from .geometry import bounds_to_geom_wgs84
from .stac import search_stac_items, filter_items_by_geometry
from .processing import clipped_asset


def download_images(
    bounds: tuple,
    assets: Union[str, List[str]],
    prefix: str,
    input_crs: Union[int, str] = 24879,
    start_date: str = "2014-08-01",
    end_date: str = None,
    max_cloud_pct: int = 5
) -> dict:
    """
    Download and process Sentinel-2 images for timelapse creation.
    
    This function orchestrates the complete workflow for downloading Sentinel-2
    imagery from Microsoft's Planetary Computer. It searches for available images
    within the specified bounds and date range, filters by cloud coverage, and
    downloads the requested assets clipped to the area of interest.
    
    Args:
        bounds: Tuple of bounding box coordinates (xmin, ymin, xmax, ymax) in the
               specified input_crs coordinate system
        assets: Single asset name (str) or list of asset names to download.
               Common assets include 'visual' (true color), 'B04' (red band),
               'SCL' (scene classification layer), etc.
        prefix: Output directory prefix where downloaded images will be saved.
               Each asset will be saved in a subdirectory named after the asset.
        input_crs: Coordinate reference system of the input bounds. Can be an
                  EPSG code (int) or CRS string. Default is EPSG:24879 (UTM zone 19S, North Chile).
        start_date: Start date for image search in YYYY-MM-DD format.
                   Default is "2014-08-01" (Sentinel-2 launch date).
        end_date: End date for image search in YYYY-MM-DD format.
                 If None, uses today's date.
        max_cloud_pct: Maximum allowed cloud coverage percentage (0-100).
                      Images with higher cloud coverage will be filtered out.
                      Default is 5%.
    
    Returns:
        dict: Processing statistics containing:
            - total_images: Total number of images found in the search area
            - cloud_filtered: Number of images filtered out due to high cloud coverage
            - asset_counts: Dictionary mapping asset names to the number of
                           successfully processed images for each asset
    
    Raises:
        ValueError: If bounds format is invalid or required parameters are missing
        RuntimeError: If STAC search fails or no images are found
        OSError: If output directory cannot be created
    
    Example:
        >>> bounds = (407500.0, 7494500.0, 415200.0, 7505700.0)
        >>> stats = download_images(
        ...     bounds=bounds,
        ...     assets=['visual', 'B04'],
        ...     prefix='mining_area',
        ...     start_date='2023-01-01',
        ...     end_date='2023-01-31',
        ...     max_cloud_pct=10
        ... )
        >>> print(f"Processed {stats['asset_counts']['visual']} visual images")
    """
    # Initialize statistics dictionary to track processing results
    stats = {
        'total_images': 0,
        'cloud_filtered': 0,
        'asset_counts': {}
    }
    
    # Validate and prepare input parameters
    if isinstance(assets, str):
        assets = [assets]  # Convert single asset to list for uniform processing
    
    # Set end_date to today if not provided
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    
    # Extract bounding box coordinates
    xmin, ymin, xmax, ymax = bounds
    
    # Convert input bounds to WGS84 geometry for STAC API search
    # STAC APIs typically expect WGS84 coordinates regardless of input CRS
    bbox_geom = bounds_to_geom_wgs84(xmin, ymin, xmax, ymax, 
                                    input_crs=input_crs, 
                                    output_format='json')
    
    # Search for available Sentinel-2 images in the specified area and date range
    items = search_stac_items(bbox_geom, f"{start_date}/{end_date}")
    
    # Filter items to ensure they actually intersect with our area of interest
    # This step removes items that might be returned by STAC but don't overlap
    filtered_items = filter_items_by_geometry(items, bbox_geom)
    stats['total_images'] = len(filtered_items)
    
    # Create the main output directory if it doesn't exist
    if not os.path.exists(prefix):
        os.makedirs(prefix)
    
    # Initialize asset counters and create asset-specific subdirectories
    for asset in assets:
        stats['asset_counts'][asset] = 0
        # Create subdirectory for each asset type
        asset_path = os.path.join(prefix, asset)
        if not os.path.exists(asset_path):
            os.makedirs(asset_path)
    
    # Process each image item found in the search
    for item in filtered_items:
        # Check cloud coverage if cloud filtering is enabled
        if max_cloud_pct is not None:
            # Download SCL (Scene Classification Layer) to assess cloud coverage
            scl_data = clipped_asset(
                item, xmin, ymin, xmax, ymax,
                bounds_crs=input_crs,
                asset_name='SCL',
                return_data_dic=True
            )
            
            # Calculate cloud coverage percentage if SCL data is available
            if scl_data is not None:
                # SCL values >= 8 represent cloud pixels (medium/high probability)
                # Calculate percentage of cloud pixels relative to valid pixels
                cloud_pct = 100 * (scl_data['data'][0] >= 8).sum() / (scl_data['data'][0] >= 0).sum()
                
                # Skip this image if cloud coverage exceeds the threshold
                if cloud_pct > max_cloud_pct:
                    stats['cloud_filtered'] += 1
                    continue
        
        # Process each requested asset for this image item
        for asset in assets:
            # Download and clip the asset to the specified bounds
            clipped_asset(
                item, xmin, ymin, xmax, ymax,
                bounds_crs=input_crs,
                asset_name=asset,
                prefix=prefix,
                save_tiff=True,
                out_path=os.path.join(prefix, asset)
            )
            # Increment the counter for successfully processed assets
            stats['asset_counts'][asset] += 1
    
    return stats

