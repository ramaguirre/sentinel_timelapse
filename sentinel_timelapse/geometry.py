import geopandas as gpd
from shapely.geometry import box, mapping

def bounds_to_geom_wgs84(minx, miny, maxx, maxy, input_crs=24879, output_format='shapely'):
    """
    Convert bounding box in any CRS to WGS84 geometry.
    """
    geom_utm = box(minx, miny, maxx, maxy)
    crs_str = f"EPSG:{input_crs}" if isinstance(input_crs, int) else input_crs
    aoi_gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[geom_utm], crs=crs_str)
    aoi_gdf_wgs = aoi_gdf.to_crs(4326)
    if output_format == 'shapely':
        return aoi_gdf_wgs.geometry.iloc[0]
    else:
        return mapping(aoi_gdf_wgs.geometry.iloc[0])