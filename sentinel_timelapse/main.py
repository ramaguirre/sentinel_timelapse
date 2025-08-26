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
    Process Sentinel images for given bounds and assets.
    
    Args:
        bounds: Tuple of (xmin, ymin, xmax, ymax)
        assets: Asset name or list of asset names (e.g., 'visual', 'SCL')
        prefix: Output directory prefix
        input_crs: CRS of input bounds (default: 24879)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format (default: today)
        max_cloud_pct: Maximum cloud coverage percentage (default: 5)
    
    Returns:
        dict: Processing statistics including:
            - total_images: number of images processed
            - cloud_filtered: number of images filtered by cloud coverage
            - asset_counts: dictionary with count of images per asset
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
        for asset in assets:
            asset_path = os.path.join(prefix, asset)
            if not os.path.exists(asset_path):
                os.makedirs(asset_path)
            # Process and save current asset
            clipped_asset(
                item, xmin, ymin, xmax, ymax,
                bounds_crs=input_crs,
                asset_name=asset,
                prefix=prefix,
                save_tiff=True,
                out_path=asset_path
            )
        stats['asset_counts'][asset] += 1
    
    return stats

