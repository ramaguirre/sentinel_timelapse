from datetime import datetime
import os
from typing import Union, List
import geopandas as gpd
from shapely.geometry import box

from .geometry import bounds_to_geom_wgs84
from .stac import search_stac_items, filter_items_by_geometry
from .processing import clipped_asset

"""
Main module for downloading and processing Sentinel-2 imagery.

This module provides the main interface for downloading Sentinel-2 images
from Microsoft's Planetary Computer using the STAC API.
"""

def download_images(
    bounds: tuple,
    assets: list,
    prefix: str,
    input_crs: int,
    start_date: str,
    end_date: str,
    max_cloud_pct: float = 20
) -> dict:
    """
    Download and process Sentinel-2 images for a given area and time period.

    Args:
        bounds (tuple): Area of interest as (minx, miny, maxx, maxy)
        assets (list): List of Sentinel-2 assets to download (e.g., ['visual', 'B04'])
        prefix (str): Output directory prefix for saved files
        input_crs (int): EPSG code of input coordinates
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        max_cloud_pct (float, optional): Maximum cloud coverage percentage. Defaults to 20.

    Returns:
        dict: Processing statistics including:
            - total_images: Number of images found
            - cloud_filtered: Number of images filtered due to clouds
            - asset_counts: Number of images processed per asset

    Example:
        >>> bounds = (407500.0, 7494500.0, 415200.0, 7505700.0)
        >>> stats = download_images(bounds, ['visual'], 'output', 24879,
                                  '2023-12-01', '2023-12-31')
    """
    stats = {
        'total_images': 0,
        'cloud_filtered': 0,
        'asset_counts': {}
    }
    
    # Validate and prepare inputs
    if isinstance(assets, str):
        assets = [assets]
    
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    
    xmin, ymin, xmax, ymax = bounds
    
    # Convert bounds to WGS84 for STAC search
    bbox_geom = bounds_to_geom_wgs84(xmin, ymin, xmax, ymax, 
                                    input_crs=input_crs, 
                                    output_format='json')
    
    # Search and filter items
    items = search_stac_items(bbox_geom, f"{start_date}/{end_date}")
    filtered_items = filter_items_by_geometry(items, bbox_geom)
    stats['total_images'] = len(filtered_items)
    
    # Create main output directory
    if not os.path.exists(prefix):
        os.makedirs(prefix)
    
    # Process each asset
    for asset in assets:
        stats['asset_counts'][asset] = 0
        # Create asset-specific subfolder
        asset_path = os.path.join(prefix, asset)
        if not os.path.exists(asset_path):
            os.makedirs(asset_path)
        
        # Process items for current asset
        for item in filtered_items:
            # Check cloud coverage if SCL asset is available
            if max_cloud_pct is not None:
                scl_data = clipped_asset(
                    item, xmin, ymin, xmax, ymax,
                    bounds_crs=input_crs,
                    asset_name='SCL',
                    return_data_dic=True
                )
                cloud_pct = 100 * (scl_data['data'][0] >= 8).sum() / (scl_data['data'][0] >= 0).sum()
                if cloud_pct > max_cloud_pct:
                    stats['cloud_filtered'] += 1
                    continue
            
            # Process and save current asset
            clipped_asset(
                item, xmin, ymin, xmax, ymax,
                bounds_crs=input_crs,
                asset_name=asset,
                prefix=asset,
                save_tiff=True,
                out_path=asset_path
            )
            stats['asset_counts'][asset] += 1
    
    return stats

