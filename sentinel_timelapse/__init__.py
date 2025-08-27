"""
Sentinel Timelapse - A Python package for downloading and processing Sentinel-2 imagery.

This package provides tools for downloading, processing, and analyzing Sentinel-2
satellite imagery for timelapse creation. It leverages Microsoft's Planetary Computer
STAC API to access pre-processed Sentinel-2 Level-2A data with atmospheric correction.

Key Features:
- Automated Sentinel-2 image discovery and download
- Cloud coverage filtering and quality assessment
- Coordinate system transformations and geometric clipping
- Support for multiple spectral bands and composites
- Command-line interface for batch processing
- Integration with Microsoft Planetary Computer

Example Usage:
    >>> from sentinel_timelapse import download_images
    >>> 
    >>> # Download visual and red band imagery for a mining area
    >>> stats = download_images(
    ...     bounds=(407500.0, 7494500.0, 415200.0, 7505700.0),
    ...     assets=['visual', 'B04'],
    ...     prefix='mining_area',
    ...     start_date='2023-01-01',
    ...     end_date='2023-01-31',
    ...     max_cloud_pct=10
    ... )
    >>> print(f"Processed {stats['asset_counts']['visual']} visual images")

For more information, visit: https://github.com/yourusername/sentinel-timelapse
"""

# Import the main functionality modules
# Note: The geospatial environment bootstrap is handled automatically
# when needed by the individual modules to avoid circular import issues
from .geometry import bounds_to_geom_wgs84
from .stac import search_stac_items, filter_items_by_geometry
from .processing import clipped_asset
from .main import download_images

# Define the public API for the package
# Only the main download_images function is exposed as the primary interface
# Other functions can be imported directly if needed for advanced usage
__all__ = ["download_images"]
