"""
STAC (SpatioTemporal Asset Catalog) utilities for Sentinel-2 data access.

This module provides functions for searching and filtering Sentinel-2 imagery
through Microsoft's Planetary Computer STAC API. It handles the discovery
of available satellite images based on spatial and temporal criteria.
"""

import pystac_client
from shapely.geometry import shape


def search_stac_items(bbox, datetime, collection="sentinel-2-l2a"):
    """
    Search for Sentinel-2 imagery items using the Planetary Computer STAC API.
    
    This function queries Microsoft's Planetary Computer STAC catalog to find
    available Sentinel-2 Level-2A imagery that intersects with the specified
    bounding box and time period. The Planetary Computer provides pre-processed
    Sentinel-2 data with atmospheric correction applied.
    
    Args:
        bbox: Bounding box geometry in GeoJSON format (dict) or Shapely geometry.
              Should be in WGS84 coordinates (EPSG:4326).
        datetime: Time range for the search in ISO 8601 format.
                 Can be a single date "YYYY-MM-DD" or a range "YYYY-MM-DD/YYYY-MM-DD".
        collection: STAC collection identifier. Default is "sentinel-2-l2a" which
                   represents Sentinel-2 Level-2A (atmospherically corrected) data.
                   Other options include "sentinel-2-l1c" for Level-1C data.
    
    Returns:
        list: List of STAC item objects representing available Sentinel-2 images.
              Each item contains metadata about the image including acquisition
              time, cloud coverage, and available assets.
    
    Raises:
        ConnectionError: If unable to connect to the Planetary Computer API
        ValueError: If the bbox or datetime parameters are invalid
        RuntimeError: If the STAC search fails
    
    Example:
        >>> from sentinel_timelapse.geometry import bounds_to_geom_wgs84
        >>> 
        >>> # Convert bounds to WGS84 GeoJSON
        >>> bbox = bounds_to_geom_wgs84(407500, 7494500, 415200, 7505700, 
        ...                             input_crs=24879, output_format='json')
        >>> 
        >>> # Search for images in January 2023
        >>> items = search_stac_items(bbox, "2023-01-01/2023-01-31")
        >>> print(f"Found {len(items)} images")
    """
    # Open connection to Microsoft's Planetary Computer STAC catalog
    # This provides access to a wide range of satellite and environmental data
    catalog = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    
    # Perform the STAC search with the specified criteria
    # The search returns items that intersect with the bounding box and time range
    search = catalog.search(
        collections=[collection],  # Limit to Sentinel-2 Level-2A collection
        intersects=bbox,          # Spatial filter using the bounding box
        datetime=datetime         # Temporal filter using the date range
    )
    
    # Convert the search results to a list of STAC item objects
    # Each item represents a single Sentinel-2 image acquisition
    return list(search.items())


def filter_items_by_geometry(items, bbox_geom):
    """
    Filter STAC items based on geometric intersection with a bounding box.
    
    This function performs additional geometric filtering on STAC search results
    to ensure that the returned items actually contain data within the specified
    area of interest. This is useful when the STAC API's spatial filtering
    might return items that only partially intersect or are near the search area.
    
    Args:
        items: List of STAC item objects from a previous search operation.
               Each item should have a 'geometry' attribute containing GeoJSON.
        bbox_geom: Bounding box geometry to filter against. Can be a GeoJSON
                  dictionary or Shapely geometry object. Should be in WGS84.
    
    Returns:
        list: Filtered list of STAC items that contain data within the specified
              bounding box. Items that don't intersect are excluded.
    
    Note:
        This function uses Shapely's 'contains' method, which requires the
        bounding box to be fully contained within the item's geometry. For
        more flexible intersection testing, consider using 'intersects' instead.
    
    Example:
        >>> # Filter items to ensure they contain our area of interest
        >>> filtered_items = filter_items_by_geometry(items, bbox_geom)
        >>> print(f"After filtering: {len(filtered_items)} items")
    """
    # Filter items based on geometric containment
    # Only keep items whose geometry contains the specified bounding box
    # This ensures we get items that have complete coverage of our area of interest
    return [item for item in items if shape(item.geometry).contains(shape(bbox_geom))]