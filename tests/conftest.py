"""
Pytest configuration and common fixtures for sentinel_timelapse tests.
"""

import pytest
import tempfile
import os
import numpy as np
from unittest.mock import Mock
from shapely.geometry import box, mapping


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def test_bounds():
    """Test bounds in UTM zone 19S (EPSG:24879)."""
    return (407500.0, 7494500.0, 415200.0, 7505700.0)


@pytest.fixture
def test_wgs84_bounds():
    """Test bounds in WGS84."""
    return (-70.5, -24.5, -70.4, -24.4)


@pytest.fixture
def test_assets():
    """Test assets."""
    return ['visual', 'B04']


@pytest.fixture
def test_dates():
    """Test date range."""
    return {
        'start_date': '2023-01-01',
        'end_date': '2023-01-31'
    }


@pytest.fixture
def mock_stac_item():
    """Mock STAC item for testing."""
    item = Mock()
    item.id = "S2A_MSIL2A_20230115T100000_N0509_R122_T19HFA_20230115T120000"
    item.properties = {'datetime': '2023-01-15T10:00:00Z'}
    item.geometry = mapping(box(-70.5, -24.5, -70.4, -24.4))
    return item


@pytest.fixture
def mock_stac_items():
    """Multiple mock STAC items for testing."""
    items = []
    for i in range(3):
        item = Mock()
        item.id = f"S2A_MSIL2A_2023011{i}T100000_N0509_R122_T19HFA_2023011{i}T120000"
        item.properties = {'datetime': f'2023-01-1{i}T10:00:00Z'}
        item.geometry = mapping(box(-70.5, -24.5, -70.4, -24.4))
        items.append(item)
    return items


@pytest.fixture
def mock_signed_item():
    """Mock signed STAC item for testing."""
    signed_item = Mock()
    mock_asset = Mock()
    mock_asset.href = "https://example.com/test.tif"
    signed_item.assets = {
        'visual': mock_asset,
        'B04': mock_asset,
        'SCL': mock_asset
    }
    return signed_item


@pytest.fixture
def mock_rasterio_dataset():
    """Mock rasterio dataset for testing."""
    dataset = Mock()
    dataset.crs = Mock()
    dataset.crs.to_epsg.return_value = 32719
    dataset.bounds = Mock()
    dataset.bounds.left = 400000
    dataset.bounds.right = 420000
    dataset.bounds.bottom = 7490000
    dataset.bounds.top = 7510000
    dataset.transform = Mock()
    dataset.profile = {
        'driver': 'GTiff',
        'dtype': 'uint8',
        'count': 3,
        'width': 2000,
        'height': 2000
    }
    dataset.read.return_value = np.random.randint(0, 255, (3, 100, 100), dtype=np.uint8)
    dataset.window_transform.return_value = Mock()
    return dataset


@pytest.fixture
def mock_cloud_data():
    """Mock cloud data for testing."""
    # Low cloud coverage data
    low_cloud = np.random.randint(0, 8, (1, 100, 100))
    # High cloud coverage data
    high_cloud = np.random.randint(8, 11, (1, 100, 100))
    return {
        'low': low_cloud,
        'high': high_cloud
    }
