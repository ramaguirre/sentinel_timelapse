import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from sentinel_timelapse.main import download_images


class TestMain(unittest.TestCase):
    """Test cases for main module functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Test parameters
        self.bounds = (407500.0, 7494500.0, 415200.0, 7505700.0)
        self.assets = ['visual', 'B04']
        self.prefix = 'test_output'
        self.start_date = '2023-01-01'
        self.end_date = '2023-01-31'
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock STAC items
        self.mock_item1 = Mock()
        self.mock_item1.id = "test_item_1"
        self.mock_item1.properties = {'datetime': '2023-01-15T10:00:00Z'}
        
        self.mock_item2 = Mock()
        self.mock_item2.id = "test_item_2"
        self.mock_item2.properties = {'datetime': '2023-01-20T10:00:00Z'}
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('sentinel_timelapse.main.clipped_asset')
    @patch('sentinel_timelapse.main.filter_items_by_geometry')
    @patch('sentinel_timelapse.main.search_stac_items')
    @patch('sentinel_timelapse.main.bounds_to_geom_wgs84')
    def test_download_images_success(self, mock_bounds_to_geom, mock_search, mock_filter, mock_clip):
        """Test successful image download process."""
        # Mock geometry conversion
        mock_bbox_geom = Mock()
        mock_bounds_to_geom.return_value = mock_bbox_geom
        
        # Mock STAC search
        mock_search.return_value = [self.mock_item1, self.mock_item2]
        
        # Mock filtering
        mock_filter.return_value = [self.mock_item1, self.mock_item2]
        
        # Mock asset clipping with proper cloud data
        def mock_clip_side_effect(*args, **kwargs):
            if kwargs.get('asset_name') == 'SCL' and kwargs.get('return_data_dic'):
                # Return mock cloud data (low cloud coverage)
                import numpy as np
                cloud_data = np.random.randint(0, 8, (1, 100, 100))  # Low cloud values
                return {'data': [cloud_data]}
            return None
        
        mock_clip.side_effect = mock_clip_side_effect
        
        # Test the function
        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.temp_dir,
            start_date=self.start_date,
            end_date=self.end_date,
            max_cloud_pct=5
        )
        
        # Verify the statistics
        self.assertEqual(stats['total_images'], 2)
        self.assertEqual(stats['cloud_filtered'], 0)
        self.assertEqual(stats['asset_counts']['visual'], 2)
        self.assertEqual(stats['asset_counts']['B04'], 2)
        
        # Verify function calls
        mock_bounds_to_geom.assert_called_once()
        mock_search.assert_called_once_with(mock_bbox_geom, f"{self.start_date}/{self.end_date}")
        mock_filter.assert_called_once()
        self.assertEqual(mock_clip.call_count, 6)  # 2 items × 3 calls (SCL + 2 assets)
    
    @patch('sentinel_timelapse.main.clipped_asset')
    @patch('sentinel_timelapse.main.filter_items_by_geometry')
    @patch('sentinel_timelapse.main.search_stac_items')
    @patch('sentinel_timelapse.main.bounds_to_geom_wgs84')
    def test_download_images_single_asset(self, mock_bounds_to_geom, mock_search, mock_filter, mock_clip):
        """Test image download with single asset."""
        # Mock geometry conversion
        mock_bbox_geom = Mock()
        mock_bounds_to_geom.return_value = mock_bbox_geom
        
        # Mock STAC search
        mock_search.return_value = [self.mock_item1]
        
        # Mock filtering
        mock_filter.return_value = [self.mock_item1]
        
        # Mock asset clipping with proper cloud data
        def mock_clip_side_effect(*args, **kwargs):
            if kwargs.get('asset_name') == 'SCL' and kwargs.get('return_data_dic'):
                # Return mock cloud data (low cloud coverage)
                import numpy as np
                cloud_data = np.random.randint(0, 8, (1, 100, 100))  # Low cloud values
                return {'data': [cloud_data]}
            return None
        
        mock_clip.side_effect = mock_clip_side_effect
        
        # Test with single asset
        stats = download_images(
            bounds=self.bounds,
            assets='visual',  # Single asset as string
            prefix=self.temp_dir,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # Verify the statistics
        self.assertEqual(stats['total_images'], 1)
        self.assertEqual(stats['asset_counts']['visual'], 1)
        
        # Verify function calls
        self.assertEqual(mock_clip.call_count, 2)  # 1 item × 2 calls (SCL + 1 asset)
    
    @patch('sentinel_timelapse.main.clipped_asset')
    @patch('sentinel_timelapse.main.filter_items_by_geometry')
    @patch('sentinel_timelapse.main.search_stac_items')
    @patch('sentinel_timelapse.main.bounds_to_geom_wgs84')
    def test_download_images_cloud_filtering(self, mock_bounds_to_geom, mock_search, mock_filter, mock_clip):
        """Test image download with cloud filtering."""
        # Mock geometry conversion
        mock_bbox_geom = Mock()
        mock_bounds_to_geom.return_value = mock_bbox_geom
        
        # Mock STAC search
        mock_search.return_value = [self.mock_item1, self.mock_item2]
        
        # Mock filtering
        mock_filter.return_value = [self.mock_item1, self.mock_item2]
        
        # Mock asset clipping with cloud data (high cloud coverage)
        def mock_clip_side_effect(*args, **kwargs):
            if kwargs.get('asset_name') == 'SCL' and kwargs.get('return_data_dic'):
                # Return mock cloud data (high cloud coverage)
                import numpy as np
                cloud_data = np.random.randint(8, 11, (1, 100, 100))  # High cloud values
                return {'data': [cloud_data]}
            return None
        
        mock_clip.side_effect = mock_clip_side_effect
        
        # Test with cloud filtering
        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.temp_dir,
            start_date=self.start_date,
            end_date=self.end_date,
            max_cloud_pct=5  # Low threshold
        )
        
        # Verify cloud filtering
        self.assertEqual(stats['total_images'], 2)
        self.assertEqual(stats['cloud_filtered'], 2)  # Both items should be filtered
        self.assertEqual(stats['asset_counts']['visual'], 0)  # No items processed
        self.assertEqual(stats['asset_counts']['B04'], 0)
    
    @patch('sentinel_timelapse.main.clipped_asset')
    @patch('sentinel_timelapse.main.filter_items_by_geometry')
    @patch('sentinel_timelapse.main.search_stac_items')
    @patch('sentinel_timelapse.main.bounds_to_geom_wgs84')
    def test_download_images_no_cloud_filtering(self, mock_bounds_to_geom, mock_search, mock_filter, mock_clip):
        """Test image download without cloud filtering."""
        # Mock geometry conversion
        mock_bbox_geom = Mock()
        mock_bounds_to_geom.return_value = mock_bbox_geom
        
        # Mock STAC search
        mock_search.return_value = [self.mock_item1]
        
        # Mock filtering
        mock_filter.return_value = [self.mock_item1]
        
        # Mock asset clipping
        mock_clip.return_value = None
        
        # Test without cloud filtering
        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.temp_dir,
            start_date=self.start_date,
            end_date=self.end_date,
            max_cloud_pct=None  # No cloud filtering
        )
        
        # Verify no cloud filtering
        self.assertEqual(stats['total_images'], 1)
        self.assertEqual(stats['cloud_filtered'], 0)
        self.assertEqual(stats['asset_counts']['visual'], 1)
        self.assertEqual(stats['asset_counts']['B04'], 1)
    
    @patch('sentinel_timelapse.main.clipped_asset')
    @patch('sentinel_timelapse.main.filter_items_by_geometry')
    @patch('sentinel_timelapse.main.search_stac_items')
    @patch('sentinel_timelapse.main.bounds_to_geom_wgs84')
    def test_download_images_empty_results(self, mock_bounds_to_geom, mock_search, mock_filter, mock_clip):
        """Test image download with empty search results."""
        # Mock geometry conversion
        mock_bbox_geom = Mock()
        mock_bounds_to_geom.return_value = mock_bbox_geom
        
        # Mock STAC search with empty results
        mock_search.return_value = []
        
        # Mock filtering
        mock_filter.return_value = []
        
        # Test with empty results
        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.temp_dir,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # Verify empty results
        self.assertEqual(stats['total_images'], 0)
        self.assertEqual(stats['cloud_filtered'], 0)
        self.assertEqual(stats['asset_counts']['visual'], 0)
        self.assertEqual(stats['asset_counts']['B04'], 0)
        
        # Verify no clipping calls
        mock_clip.assert_not_called()
    
    @patch('sentinel_timelapse.main.clipped_asset')
    @patch('sentinel_timelapse.main.filter_items_by_geometry')
    @patch('sentinel_timelapse.main.search_stac_items')
    @patch('sentinel_timelapse.main.bounds_to_geom_wgs84')
    def test_download_images_default_end_date(self, mock_bounds_to_geom, mock_search, mock_filter, mock_clip):
        """Test image download with default end date."""
        # Mock geometry conversion
        mock_bbox_geom = Mock()
        mock_bounds_to_geom.return_value = mock_bbox_geom
        
        # Mock STAC search
        mock_search.return_value = []
        
        # Mock filtering
        mock_filter.return_value = []
        
        # Test without end_date (should use today's date)
        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.temp_dir,
            start_date=self.start_date,
            end_date=None  # Should default to today
        )
        
        # Verify that search was called with today's date
        expected_date_range = f"{self.start_date}/{datetime.today().strftime('%Y-%m-%d')}"
        mock_search.assert_called_once_with(mock_bbox_geom, expected_date_range)
    
    @patch('sentinel_timelapse.main.clipped_asset')
    @patch('sentinel_timelapse.main.filter_items_by_geometry')
    @patch('sentinel_timelapse.main.search_stac_items')
    @patch('sentinel_timelapse.main.bounds_to_geom_wgs84')
    def test_download_images_different_crs(self, mock_bounds_to_geom, mock_search, mock_filter, mock_clip):
        """Test image download with different CRS."""
        # Mock geometry conversion
        mock_bbox_geom = Mock()
        mock_bounds_to_geom.return_value = mock_bbox_geom
        
        # Mock STAC search
        mock_search.return_value = [self.mock_item1]
        
        # Mock filtering
        mock_filter.return_value = [self.mock_item1]
        
        # Mock asset clipping with proper cloud data
        def mock_clip_side_effect(*args, **kwargs):
            if kwargs.get('asset_name') == 'SCL' and kwargs.get('return_data_dic'):
                # Return mock cloud data (low cloud coverage)
                import numpy as np
                cloud_data = np.random.randint(0, 8, (1, 100, 100))  # Low cloud values
                return {'data': [cloud_data]}
            return None
        
        mock_clip.side_effect = mock_clip_side_effect
        
        # Test with different CRS
        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.temp_dir,
            input_crs=4326,  # WGS84
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # Verify that bounds conversion was called with correct CRS
        mock_bounds_to_geom.assert_called_once_with(
            *self.bounds, input_crs=4326, output_format='json'
        )
    
    @patch('sentinel_timelapse.main.clipped_asset')
    @patch('sentinel_timelapse.main.filter_items_by_geometry')
    @patch('sentinel_timelapse.main.search_stac_items')
    @patch('sentinel_timelapse.main.bounds_to_geom_wgs84')
    def test_download_images_directory_creation(self, mock_bounds_to_geom, mock_search, mock_filter, mock_clip):
        """Test that output directories are created."""
        # Mock geometry conversion
        mock_bbox_geom = Mock()
        mock_bounds_to_geom.return_value = mock_bbox_geom
        
        # Mock STAC search
        mock_search.return_value = [self.mock_item1]
        
        # Mock filtering
        mock_filter.return_value = [self.mock_item1]
        
        # Mock asset clipping with proper cloud data
        def mock_clip_side_effect(*args, **kwargs):
            if kwargs.get('asset_name') == 'SCL' and kwargs.get('return_data_dic'):
                # Return mock cloud data (low cloud coverage)
                import numpy as np
                cloud_data = np.random.randint(0, 8, (1, 100, 100))  # Low cloud values
                return {'data': [cloud_data]}
            return None
        
        mock_clip.side_effect = mock_clip_side_effect
        
        # Test with non-existent directory
        new_prefix = os.path.join(self.temp_dir, 'new_test_output')
        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=new_prefix,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # Verify that directories were created
        self.assertTrue(os.path.exists(new_prefix))
        self.assertTrue(os.path.exists(os.path.join(new_prefix, 'visual')))
        self.assertTrue(os.path.exists(os.path.join(new_prefix, 'B04')))


if __name__ == '__main__':
    unittest.main()

