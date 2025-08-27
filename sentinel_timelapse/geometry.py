"""
Geometry utilities for coordinate system transformations.

This module provides functions for converting between different coordinate
reference systems (CRS) and geometry formats, specifically focused on
transforming bounding boxes to WGS84 for use with STAC APIs.
"""

import geopandas as gpd
from shapely.geometry import box, mapping

# Flag to track if geospatial environment has been initialized
_geo_initialized = False


def _ensure_geo_initialized():
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


def bounds_to_geom_wgs84(
    minx, miny, maxx, maxy, input_crs=24879, output_format="shapely"
):
    """
    Convert a bounding box from any coordinate reference system to WGS84 geometry.

    This function takes bounding box coordinates in any CRS and transforms them
    to WGS84 (EPSG:4326), which is the standard coordinate system used by most
    geospatial APIs including STAC. The function supports both Shapely geometry
    objects and GeoJSON dictionary formats as output.

    Args:
        minx: Minimum x-coordinate (left boundary) of the bounding box
        miny: Minimum y-coordinate (bottom boundary) of the bounding box
        maxx: Maximum x-coordinate (right boundary) of the bounding box
        maxy: Maximum y-coordinate (top boundary) of the bounding box
        input_crs: Coordinate reference system of the input coordinates.
                  Can be an EPSG code (int) or CRS string. Default is 24879
                  (UTM zone 19S, commonly used in Chile).
        output_format: Format of the output geometry. Options are:
                      - 'shapely': Returns a Shapely geometry object
                      - 'json': Returns a GeoJSON dictionary
                      - Any other value: Returns a GeoJSON dictionary

    Returns:
        Union[shapely.geometry.Polygon, dict]: The transformed geometry in WGS84.
        Returns either a Shapely Polygon object or a GeoJSON dictionary depending
        on the output_format parameter.

    Raises:
        ValueError: If the input CRS is invalid or transformation fails
        RuntimeError: If the coordinate transformation cannot be performed

    Example:
        >>> # Convert UTM coordinates to WGS84
        >>> geom = bounds_to_geom_wgs84(407500, 7494500, 415200, 7505700, input_crs=24879)
        >>> print(f"WGS84 bounds: {geom.bounds}")

        >>> # Get GeoJSON format for STAC API
        >>> geojson = bounds_to_geom_wgs84(407500, 7494500, 415200, 7505700,
        ...                                input_crs=24879, output_format='json')
        >>> print(f"GeoJSON: {geojson['type']}")
    """
    # Ensure geospatial environment is initialized
    _ensure_geo_initialized()

    # Create a Shapely box geometry from the input bounding box coordinates
    geom_utm = box(minx, miny, maxx, maxy)

    # Format the CRS string for GeoPandas
    # If input_crs is an integer, convert to EPSG string format
    # Otherwise, use the string as-is (allows for custom CRS strings)
    crs_str = f"EPSG:{input_crs}" if isinstance(input_crs, int) else input_crs

    # Create a GeoDataFrame with the input geometry and CRS
    # This enables coordinate transformation capabilities
    aoi_gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[geom_utm], crs=crs_str)

    # Transform the geometry from input CRS to WGS84 (EPSG:4326)
    # WGS84 is the standard coordinate system for most geospatial APIs
    aoi_gdf_wgs = aoi_gdf.to_crs(4326)

    # Return the geometry in the requested format
    if output_format == "shapely":
        # Return as Shapely geometry object for further geometric operations
        return aoi_gdf_wgs.geometry.iloc[0]
    else:
        # Return as GeoJSON dictionary for API compatibility
        # This format is commonly used by STAC APIs and web services
        return mapping(aoi_gdf_wgs.geometry.iloc[0])
