# Sentinel Timelapse Generator

Create timelapses from Sentinel-2 imagery using Microsoft's Planetary Computer.

## Features
- Access Sentinel-2 imagery via STAC API
- Process and combine images into timelapses
- Filter by cloud coverage and date range

## Installation

```bash
pip install sentinel_timelapse
```

## Usage

```python
from sentinel_timelapse import download_images

# Define area of interest (in UTM coordinates)
bounds = (407500.0, 7494500.0, 415200.0, 7505700.0)  # Example: Mining area

# Download and process images
stats = download_images(
    bounds=bounds,           # Coordinates in input_crs (minx, miny, maxx, maxy)
    assets=['visual', 'B04'], # Bands to download
    prefix='output_folder',   # Output directory prefix
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

## Data Sources and Licensing

### Sentinel-2 Imagery
This package uses Sentinel-2 satellite imagery accessed through Microsoft's Planetary Computer. The imagery is provided by the European Space Agency (ESA) under the following terms:

- Copernicus Sentinel data [year] is licensed under CC BY 4.0
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