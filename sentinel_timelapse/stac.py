import pystac_client
from shapely.geometry import shape

def search_stac_items(bbox, datetime, collection="sentinel-2-l2a"):
    catalog = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    search = catalog.search(
        collections=[collection],
        intersects=bbox,
        datetime=datetime
    )
    return list(search.items())

def filter_items_by_geometry(items, bbox_geom):
    return [item for item in items if shape(item.geometry).contains(shape(bbox_geom))]