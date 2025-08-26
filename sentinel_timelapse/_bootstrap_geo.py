# sentinel_timelapse/_bootstrap_geo.py

def use_rasterio_bundled_data(verbose=True):
    import os, pathlib, atexit
    import rasterio

    # clear conflicting env vars
    for var in ("GDAL_DATA", "PROJ_LIB"):
        os.environ.pop(var, None)

    # bundled data dirs
    rio_dir = pathlib.Path(rasterio.__file__).parent
    gdal_data = rio_dir / "gdal_data"
    proj_data = rio_dir / "proj_data"

    #try:
    #    from pyproj import datadir
    #    proj_dir = datadir.get_data_dir() or str(proj_data)
    #except Exception:
    proj_dir = str(proj_data)

    os.environ["GDAL_DATA"] = str(gdal_data)
    os.environ["PROJ_LIB"] = str(proj_dir)

    if verbose:
        print(f"[geo] GDAL_DATA -> {os.environ['GDAL_DATA']}")
        print(f"[geo] PROJ_LIB -> {os.environ['PROJ_LIB']}")

    # validate quickly
    from pyproj import CRS
    _ = CRS.from_epsg(4326)

    from rasterio.env import Env
    env = Env(GDAL_DATA=os.environ["GDAL_DATA"], PROJ_LIB=os.environ["PROJ_LIB"])
    env.__enter__()
    atexit.register(env.__exit__, None, None, None)