# Conda Recipe for sentinel-timelapse

This directory contains the conda recipe for building the `sentinel-timelapse` package.

## Building Locally

To build the conda package locally:

```bash
# Install conda-build
conda install conda-build

# Build the package
conda build conda-recipe/

# Install the built package
conda install --use-local sentinel-timelapse
```

## Publishing to conda-forge

1. Create a feedstock repository on conda-forge:
   - Fork the [conda-forge/staged-recipes](https://github.com/conda-forge/staged-recipes) repository
   - Add your recipe to the `recipes/sentinel-timelapse/` directory
   - Submit a pull request

2. Once the PR is merged, conda-forge will create a feedstock repository at `conda-forge/sentinel-timelapse-feedstock`

3. For future updates, submit PRs to the feedstock repository

## Package Information

- **Package name**: sentinel-timelapse
- **Version**: 0.1.0
- **License**: MIT
- **Python versions**: >=3.8
- **Platforms**: All (noarch: python)

## Dependencies

### Runtime dependencies:
- geopandas >=0.12.0
- shapely >=1.8.0
- rasterio >=1.3.0
- pystac-client >=0.7.0
- planetary-computer >=0.5.0
- pyproj >=3.4.0
- numpy >=1.21.0
- requests >=2.28.0

### Build dependencies:
- python >=3.8
- pip
- setuptools
- wheel
