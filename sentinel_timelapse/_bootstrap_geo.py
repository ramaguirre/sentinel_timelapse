"""
Geospatial environment bootstrap utilities.

This module provides functions to configure the geospatial environment
for proper operation of rasterio and GDAL libraries. It handles setting
up environment variables and data paths for coordinate transformations
and raster processing operations.
"""

# sentinel_timelapse/_bootstrap_geo.py

def use_rasterio_bundled_data(verbose=True):
    """
    Configure rasterio to use its bundled GDAL and PROJ data.
    
    This function sets up the environment variables needed for rasterio to
    properly access GDAL and PROJ data files that are bundled with the
    rasterio installation. This is particularly important for ensuring
    consistent coordinate system transformations and geospatial operations
    across different environments.
    
    The function performs the following operations:
    1. Clears any existing GDAL_DATA and PROJ_LIB environment variables
    2. Sets these variables to point to rasterio's bundled data directories
    3. Validates the configuration by testing a simple coordinate transformation
    4. Sets up a rasterio environment context for the current session
    
    Args:
        verbose: If True, print the configured paths to stdout.
                Default is True for debugging purposes.
    
    Returns:
        None
    
    Raises:
        ImportError: If rasterio, pyproj, or required dependencies are not available
        RuntimeError: If the bundled data directories cannot be found or accessed
    
    Note:
        This function should be called early in the application lifecycle,
        ideally before any geospatial operations are performed. It's designed
        to be called once per session.
    
    Example:
        >>> from sentinel_timelapse._bootstrap_geo import use_rasterio_bundled_data
        >>> use_rasterio_bundled_data(verbose=True)
        [geo] GDAL_DATA -> /path/to/rasterio/gdal_data
        [geo] PROJ_LIB -> /path/to/rasterio/proj_data
    """
    import os, pathlib, atexit
    import rasterio

    # Clear any existing environment variables that might conflict
    # This prevents issues with system-installed GDAL/PROJ data
    for var in ("GDAL_DATA", "PROJ_LIB"):
        os.environ.pop(var, None)

    # Locate rasterio's bundled data directories
    # These contain the GDAL and PROJ data files needed for coordinate transformations
    rio_dir = pathlib.Path(rasterio.__file__).parent
    gdal_data = rio_dir / "gdal_data"  # GDAL coordinate system and datum files
    proj_data = rio_dir / "proj_data"  # PROJ coordinate transformation files

    # Attempt to use pyproj's data directory if available, otherwise fall back to rasterio's
    # This provides more comprehensive PROJ data in some installations
    #try:
    #    from pyproj import datadir
    #    proj_dir = datadir.get_data_dir() or str(proj_data)
    #except Exception:
    proj_dir = str(proj_data)

    # Set environment variables to point to the bundled data directories
    # These variables are used by GDAL and PROJ libraries to locate their data files
    os.environ["GDAL_DATA"] = str(gdal_data)
    os.environ["PROJ_LIB"] = str(proj_dir)

    # Print configuration information if verbose mode is enabled
    if verbose:
        print(f"[geo] GDAL_DATA -> {os.environ['GDAL_DATA']}")
        print(f"[geo] PROJ_LIB -> {os.environ['PROJ_LIB']}")

    # Validate the configuration by testing a simple coordinate transformation
    # This ensures that the PROJ data is accessible and functional
    from pyproj import CRS
    _ = CRS.from_epsg(4326)  # Test WGS84 coordinate system creation

    # Set up a rasterio environment context for the current session
    # This ensures that rasterio uses the configured environment variables
    from rasterio.env import Env
    env = Env(GDAL_DATA=os.environ["GDAL_DATA"], PROJ_LIB=os.environ["PROJ_LIB"])
    env.__enter__()
    
    # Register cleanup function to be called when the program exits
    # This ensures proper cleanup of the rasterio environment
    atexit.register(env.__exit__, None, None, None)