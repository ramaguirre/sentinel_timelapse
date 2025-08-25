# Sentinel Timelapse Generator

Create timelapses from Sentinel-2 imagery using Microsoft's Planetary Computer.

## Features
- Access Sentinel-2 imagery via STAC API
- Process and combine images into timelapses
- Filter by cloud coverage and date range

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from sentinel_timelapse import TimeLapseGenerator
tlg = TimeLapseGenerator(bbox=[...])
tlg.create_timelapse()
```

## Data Source
This package relies on Microsoft's Planetary Computer for accessing Sentinel-2 imagery.
Visit https://planetarycomputer.microsoft.com/ for more information.

## License
MIT License - See LICENSE file