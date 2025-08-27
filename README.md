# Sentinel Timelapse Generator

[![PyPI version](https://badge.fury.io/py/sentinel-timelapse.svg)](https://badge.fury.io/py/sentinel-timelapse)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/ramaguirre/sentinel_timelapse/workflows/Tests/badge.svg)](https://github.com/ramaguirre/sentinel_timelapse/actions)

Automatic time series download of Sentinel-2 imagery using Microsoft's Planetary Computer.

## Features
- Access Sentinel-2 imagery via STAC API
- Filter by cloud coverage, date range and area of interest (AOI)
- Download available images clipped to AOI
- Multiple bands/assets
- Cloud coverage filtering
- Support for different coordinate reference systems (CRS)

## Installation

### From PyPI (Recommended)
```bash
pip install sentinel-timelapse
```

### From GitHub
```bash
pip install git+https://github.com/ramaguirre/sentinel_timelapse.git 
```

### Development Installation
```bash
git clone https://github.com/ramaguirre/sentinel_timelapse.git
cd sentinel_timelapse
pip install -e .
```

## Quick Start

```python
from sentinel_timelapse import download_images

# Define area of interest (in UTM coordinates)
bounds = (407500.0, 7494500.0, 415200.0, 7505700.0)  # Example: Mining area

# Download and process images
stats = download_images(
    bounds=bounds,           # Coordinates in input_crs (minx, miny, maxx, maxy)
    assets=['visual', 'B04'], # Bands to download
    prefix='output',         # Output directory prefix
    input_crs=24879,         # Input CRS (EPSG code)
    start_date='2023-12-01', # Start date for image search
    end_date='2023-12-31',   # End date for image search
    max_cloud_pct=5          # Maximum cloud coverage percentage
)

# Check processing statistics
print(f"Total images found: {stats['total_images']}")
print(f"Images filtered due to clouds: {stats['cloud_filtered']}")
print(f"Images processed per asset: {stats['asset_counts']}")
```

## Command Line Usage

You can also use the package from the command line:

```bash
sentinel-timelapse --bounds 407500.0 7494500.0 415200.0 7505700.0 \
                   --assets visual B04 \
                   --prefix output \
                   --input-crs 24879 \
                   --start-date 2023-12-01 \
                   --end-date 2023-12-31 \
                   --max-cloud-pct 5
```

## Available Assets

### Common Assets
- `visual`: True color composite (RGB) - 10m
- `B02`: Blue band (490nm) - 10m
- `B03`: Green band (560nm) - 10m
- `B04`: Red band (665nm) - 10m
- `B08`: NIR band (842nm) - 10m

### Specialized Assets
- `SCL`: Scene Classification Layer - 20m
  - 0: NO_DATA
  - 1: SATURATED_OR_DEFECTIVE
  - 2: DARK_AREA_PIXELS
  - 3: CLOUD_SHADOWS
  - 4: VEGETATION
  - 5: NOT_VEGETATED
  - 6: WATER
  - 7: UNCLASSIFIED
  - 8: CLOUD_MEDIUM_PROBABILITY
  - 9: CLOUD_HIGH_PROBABILITY
  - 10: THIN_CIRRUS
  - 11: SNOW
- `AOT`: Aerosol Optical Thickness - 10m
- `WVP`: Water Vapor - 10m

### Additional Bands
- `B01`: Coastal aerosol (443nm) - 60m
- `B05`: Vegetation Red Edge 1 (705nm) - 20m
- `B06`: Vegetation Red Edge 2 (740nm) - 20m
- `B07`: Vegetation Red Edge 3 (783nm) - 20m
- `B09`: Water vapor (945nm) - 60m
- `B11`: SWIR 1 (1614nm) - 20m
- `B12`: SWIR 2 (2202nm) - 20m
- `B8A`: Vegetation Red Edge 4 (865nm) - 20m

## Documentation

For detailed documentation, visit: https://sentinel-timelapse.readthedocs.io/

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/ramaguirre/sentinel_timelapse.git`
3. Install in development mode: `pip install -e ".[dev]"`
4. Run tests: `pytest tests/`

## Data Sources and Licensing

### Sentinel-2 Imagery
This package uses Sentinel-2 satellite imagery accessed through Microsoft's Planetary Computer. The imagery is provided by the European Space Agency (ESA) under the following terms:

- Copernicus Sentinel data 2015-present is licensed under CC BY 4.0
- Source: European Space Agency (ESA)
- More information: [Copernicus Open Access Hub](https://scihub.copernicus.eu/)

### Microsoft Planetary Computer
Access to Sentinel-2 data is provided through:
- Platform: Microsoft Planetary Computer
- Website: https://planetarycomputer.microsoft.com/
- Terms of use: https://planetarycomputer.microsoft.com/terms

### References
When using this tool in research or publications, please cite:

```bibtex
@misc{sentinel2,
    title = {Sentinel-2 MSI: MultiSpectral Instrument, Level-2A},
    author = {European Space Agency},
    year = {2015--present},
    note = {Retrieved from Microsoft Planetary Computer}
}
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

### Third-Party Licenses
- Sentinel-2 data: CC BY 4.0
- Planetary Computer: See [terms of use](https://planetarycomputer.microsoft.com/terms)
