from ._bootstrap_geo import use_rasterio_bundled_data

# run it before importing anything geospatial
use_rasterio_bundled_data(verbose=True)



from .geometry import bounds_to_geom_wgs84
from .stac import search_stac_items, filter_items_by_geometry
from .processing import clipped_asset
from .main import download_images

__all__ = ['download_images']