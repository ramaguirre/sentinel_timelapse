import pystac_client
from shapely.geometry import shape

"""
STAC API interaction module for Sentinel-2 data.

This module handles all interactions with Microsoft's Planetary Computer
STAC API, including:
- Searching for Sentinel-2 items
- Filtering by geometry and cloud cover
- Managing STAC collections and items
"""

def search_stac_items(geom: dict, 
                     start_date: str, 
                     end_date: str) -> list:
    """
    Search for Sentinel-2 items using STAC API.

    Args:
        geom (dict): GeoJSON-like geometry dictionary
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format

    Returns:
        list: STAC items matching search criteria

    Example:
        >>> items = search_stac_items(geometry, '2023-12-01', '2023-12-31')
    """
    catalog = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        intersects=geom,
        datetime=f"{start_date}/{end_date}"
    )
    return list(search.items())

def filter_items_by_geometry(items, bbox_geom):
    return [item for item in items if shape(item.geometry).contains(shape(bbox_geom))]