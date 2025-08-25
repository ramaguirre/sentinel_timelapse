"""
Geometry utilities for handling coordinate transformations and spatial operations.

This module provides functions to convert between different coordinate systems
and create geometry objects compatible with the STAC API.
"""

import geopandas as gpd
from shapely.geometry import box, mapping
from pyproj import CRS, Transformer

def bounds_to_geom_wgs84(bounds: tuple, input_crs: int) -> dict:
    """
    Convert bounds from input CRS to WGS84 geometry.

    Args:
        bounds (tuple): Input bounds as (minx, miny, maxx, maxy)
        input_crs (int): EPSG code of input coordinate system

    Returns:
        dict: GeoJSON-like dictionary with WGS84 geometry

    Example:
        >>> bounds = (407500.0, 7494500.0, 415200.0, 7505700.0)
        >>> geom = bounds_to_geom_wgs84(bounds, 24879)
    """
    minx, miny, maxx, maxy = bounds
    geom_utm = box(minx, miny, maxx, maxy)
    crs_str = f"EPSG:{input_crs}" if isinstance(input_crs, int) else input_crs
    aoi_gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[geom_utm], crs=crs_str)
    aoi_gdf_wgs = aoi_gdf.to_crs(4326)
    return mapping(aoi_gdf_wgs.geometry.iloc[0])