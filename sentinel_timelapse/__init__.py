"""
Sentinel Timelapse Generator.

A package for creating timelapses from Sentinel-2 imagery using Microsoft's 
Planetary Computer STAC API.

Functions:
    download_images: Main function to download and process Sentinel-2 images
"""

from .geometry import bounds_to_geom_wgs84
from .stac import search_stac_items, filter_items_by_geometry
from .processing import clipped_asset
from .main import download_images

__all__ = ['download_images']