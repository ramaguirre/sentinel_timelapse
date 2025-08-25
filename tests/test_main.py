import pytest
from sentinel_timelapse import process_sentinel_images

def test_process_sentinel_images():
    bounds = (407500.0, 7494500.0, 415200.0, 7505700.0)
    result = process_sentinel_images(
        bounds=bounds,
        assets=['visual'],
        prefix='test_output',
        start_date='2023-01-01',
        end_date='2023-01-31'
    )
    
    assert isinstance(result, dict)
    assert 'total_images' in result
    assert 'cloud_filtered' in result
    assert 'asset_counts' in result