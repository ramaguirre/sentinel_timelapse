import planetary_computer
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
from rasterio.coords import BoundingBox
import os
import geopandas as gpd
from shapely.geometry import box

def clipped_asset(item, xmin, ymin, xmax, ymax, input_crs='EPSG:24879', bounds_crs='EPSG:32719', 
                 asset_name='visual', prefix='clipped', return_data_dic=False, 
                 save_tiff=False, out_path=None):
    """
    Clip a Sentinel asset to specified bounds.
    
    Args:
        item: STAC item
        xmin, ymin, xmax, ymax: Bounds in input_crs coordinates
        input_crs: CRS of input bounds (default: EPSG:24879)
        bounds_crs: Target CRS for clipping (default: EPSG:32719)
        asset_name: Name of asset to clip (default: 'visual')
        prefix: Prefix for output filename
        return_data_dic: Whether to return data dictionary
        save_tiff: Whether to save as GeoTIFF
        out_path: Output directory path
    """
    # Convert bounds from input CRS to clipping CRS
    if input_crs != bounds_crs:
        geom = box(xmin, ymin, xmax, ymax)
        gdf = gpd.GeoDataFrame({'geometry':[geom]}, crs=input_crs)
        gdf_transformed = gdf.to_crs(bounds_crs)
        bounds_geom = gdf_transformed.geometry.iloc[0]
        xmin, ymin, xmax, ymax = bounds_geom.bounds

    signed_item = planetary_computer.sign(item)
    visual_asset = signed_item.assets[asset_name]
    href = visual_asset.href
    
    try:
        with rasterio.open(href) as src:
            src_crs = src.crs
            src_bounds = src.bounds
            transformed_bounds = transform_bounds(
                bounds_crs, src_crs, xmin, ymin, xmax, ymax
            )
            bounds = BoundingBox(*transformed_bounds)
            if not (bounds.left < src_bounds.right and bounds.right > src_bounds.left and
                    bounds.bottom < src_bounds.top and bounds.top > src_bounds.bottom):
                raise ValueError(f"Provided bounds {bounds} do not intersect with image extent {src_bounds}.")
            window = from_bounds(
                left=bounds.left, bottom=bounds.bottom,
                right=bounds.right, top=bounds.top,
                transform=src.transform
            )
            data = src.read(window=window)
            profile = src.profile.copy()
            profile.update({
                'width': data.shape[2],
                'height': data.shape[1],
                'transform': src.window_transform(window),
                'crs': src_crs,
                'driver': 'GTiff',
                'tiled': True,
                'compress': 'deflate',
                'interleave': 'band'
            })
            if return_data_dic:
                return {'data': data, 'profile': profile, 'href': href}
            if not out_path:
                out_path = prefix
            if not os.path.exists(out_path):
                os.mkdir(out_path)
            out_file = os.path.join(out_path, f'{prefix}_{asset_name}_{item.id.split("_")[2]}.tif')
            if save_tiff:
                with rasterio.open(out_file, 'w', **profile) as dst:
                    dst.write(data)
                    dst.update_tags(
                        description='Clipped Sentinel-2 visual asset from Planetary Computer',
                        creation_date=item.properties['datetime'],
                        source='Sentinel-2',
                        href=item.assets[asset_name].href
                    )
    except rasterio.errors.RasterioIOError as e:
        print(f"Rasterio error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")