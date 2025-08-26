import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from sentinel_timelapse import download_images

# Test parameters
bounds = (407500.0, 7494500.0, 415200.0, 7505700.0)  # Antucoya mine area
#assets = ['visual', 'B04']
#prefix = 'test_output_3'
#start_date = '2023-12-01'
#end_date = '2023-12-31'

assets = ['visual', 'B04']
prefix = 'test_output'
start_date = '2023-01-01'
end_date = '2023-01-31'

# Process images and get statistics
stats = download_images(
    bounds=bounds,
    assets=assets,
    prefix=prefix,
    input_crs=24879,
    start_date=start_date,
    end_date=end_date,
    max_cloud_pct=5
)

print(f"Total images found: {stats['total_images']}")
print(f"Images filtered due to clouds: {stats['cloud_filtered']}")
print(f"Images processed per asset: {stats['asset_counts']}")