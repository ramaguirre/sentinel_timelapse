import unittest
import tempfile
import os
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from shapely.geometry import box, mapping

from sentinel_timelapse import download_images
from sentinel_timelapse.geometry import bounds_to_geom_wgs84
from sentinel_timelapse.stac import search_stac_items, filter_items_by_geometry
from sentinel_timelapse.processing import clipped_asset


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete sentinel_timelapse workflow."""

    def setUp(self):
        """Set up test fixtures."""
        # Test parameters
        self.bounds = (407500.0, 7494500.0, 415200.0, 7505700.0)
        self.assets = ["visual", "B04"]
        self.start_date = "2023-01-01"
        self.end_date = "2023-01-31"

        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()

        # Mock STAC items
        self.mock_item1 = Mock()
        self.mock_item1.id = (
            "S2A_MSIL2A_20230115T100000_N0509_R122_T19HFA_20230115T120000"
        )
        self.mock_item1.properties = {"datetime": "2023-01-15T10:00:00Z"}

        self.mock_item2 = Mock()
        self.mock_item2.id = (
            "S2A_MSIL2A_20230120T100000_N0509_R122_T19HFA_20230120T120000"
        )
        self.mock_item2.properties = {"datetime": "2023-01-20T10:00:00Z"}

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_complete_workflow_success(self):
        """Test the complete workflow from bounds to final output."""
        # Mock the complete download workflow
        with patch("sentinel_timelapse.main.clipped_asset") as mock_clip:
            with patch(
                "sentinel_timelapse.main.filter_items_by_geometry"
            ) as mock_filter:
                with patch("sentinel_timelapse.main.search_stac_items") as mock_search:
                    with patch(
                        "sentinel_timelapse.main.bounds_to_geom_wgs84"
                    ) as mock_bounds:
                        # Setup mocks
                        mock_bounds.return_value = {
                            "type": "Polygon",
                            "coordinates": [],
                        }
                        mock_search.return_value = [self.mock_item1, self.mock_item2]
                        mock_filter.return_value = [self.mock_item1, self.mock_item2]

                        # Mock asset clipping with proper cloud data
                        def mock_clip_side_effect(*args, **kwargs):
                            if kwargs.get("asset_name") == "SCL" and kwargs.get(
                                "return_data_dic"
                            ):
                                # Return mock cloud data (low cloud coverage)
                                cloud_data = np.random.randint(
                                    0, 8, (1, 100, 100)
                                )  # Low cloud values
                                return {"data": [cloud_data]}
                            return None

                        mock_clip.side_effect = mock_clip_side_effect

                        # Test complete download workflow
                        stats = download_images(
                            bounds=self.bounds,
                            assets=self.assets,
                            prefix=self.temp_dir,
                            start_date=self.start_date,
                            end_date=self.end_date,
                            max_cloud_pct=5,
                        )

                        # Verify results
                        self.assertEqual(stats["total_images"], 2)
                        self.assertEqual(stats["cloud_filtered"], 0)
                        self.assertEqual(stats["asset_counts"]["visual"], 2)
                        self.assertEqual(stats["asset_counts"]["B04"], 2)

                        # Verify directories were created
                        self.assertTrue(os.path.exists(self.temp_dir))
                        self.assertTrue(
                            os.path.exists(os.path.join(self.temp_dir, "visual"))
                        )
                        self.assertTrue(
                            os.path.exists(os.path.join(self.temp_dir, "B04"))
                        )

    def test_workflow_with_cloud_filtering(self):
        """Test the complete workflow with cloud filtering."""
        # Mock the complete workflow with cloud filtering
        with patch("sentinel_timelapse.main.clipped_asset") as mock_clip:
            with patch(
                "sentinel_timelapse.main.filter_items_by_geometry"
            ) as mock_filter:
                with patch("sentinel_timelapse.main.search_stac_items") as mock_search:
                    with patch(
                        "sentinel_timelapse.main.bounds_to_geom_wgs84"
                    ) as mock_bounds:
                        # Setup mocks
                        mock_bounds.return_value = {
                            "type": "Polygon",
                            "coordinates": [],
                        }
                        mock_search.return_value = [self.mock_item1, self.mock_item2]
                        mock_filter.return_value = [self.mock_item1, self.mock_item2]

                        # Mock cloud data (high cloud coverage)
                        def mock_clip_side_effect(*args, **kwargs):
                            if kwargs.get("asset_name") == "SCL" and kwargs.get(
                                "return_data_dic"
                            ):
                                # Return high cloud coverage data
                                cloud_data = np.random.randint(8, 11, (1, 100, 100))
                                return {"data": [cloud_data]}
                            return None

                        mock_clip.side_effect = mock_clip_side_effect

                        # Test with cloud filtering
                        stats = download_images(
                            bounds=self.bounds,
                            assets=self.assets,
                            prefix=self.temp_dir,
                            start_date=self.start_date,
                            end_date=self.end_date,
                            max_cloud_pct=5,  # Low threshold
                        )

                        # Verify cloud filtering worked
                        self.assertEqual(stats["total_images"], 2)
                        self.assertEqual(stats["cloud_filtered"], 2)
                        self.assertEqual(stats["asset_counts"]["visual"], 0)
                        self.assertEqual(stats["asset_counts"]["B04"], 0)

    def test_workflow_with_different_crs(self):
        """Test the complete workflow with different CRS."""
        # Test with WGS84 bounds
        wgs84_bounds = (-70.5, -24.5, -70.4, -24.4)

        with patch("sentinel_timelapse.main.clipped_asset") as mock_clip:
            with patch(
                "sentinel_timelapse.main.filter_items_by_geometry"
            ) as mock_filter:
                with patch("sentinel_timelapse.main.search_stac_items") as mock_search:
                    with patch(
                        "sentinel_timelapse.main.bounds_to_geom_wgs84"
                    ) as mock_bounds:
                        # Setup mocks
                        mock_bounds.return_value = {
                            "type": "Polygon",
                            "coordinates": [],
                        }
                        mock_search.return_value = [self.mock_item1]
                        mock_filter.return_value = [self.mock_item1]

                        # Mock asset clipping with proper cloud data
                        def mock_clip_side_effect(*args, **kwargs):
                            if kwargs.get("asset_name") == "SCL" and kwargs.get(
                                "return_data_dic"
                            ):
                                # Return mock cloud data (low cloud coverage)
                                cloud_data = np.random.randint(
                                    0, 8, (1, 100, 100)
                                )  # Low cloud values
                                return {"data": [cloud_data]}
                            return None

                        mock_clip.side_effect = mock_clip_side_effect

                        # Test with WGS84 CRS
                        stats = download_images(
                            bounds=wgs84_bounds,
                            assets=self.assets,
                            prefix=self.temp_dir,
                            input_crs=4326,  # WGS84
                            start_date=self.start_date,
                            end_date=self.end_date,
                        )

                        # Verify CRS conversion was called correctly
                        mock_bounds.assert_called_once_with(
                            *wgs84_bounds, input_crs=4326, output_format="json"
                        )

                        # Verify results
                        self.assertEqual(stats["total_images"], 1)
                        self.assertEqual(stats["asset_counts"]["visual"], 1)
                        self.assertEqual(stats["asset_counts"]["B04"], 1)

    def test_workflow_error_handling(self):
        """Test error handling in the complete workflow."""
        # Test with invalid bounds
        invalid_bounds = (0, 0, 0, 0)  # Invalid bounds

        with patch("sentinel_timelapse.main.bounds_to_geom_wgs84") as mock_bounds:
            mock_bounds.side_effect = Exception("Invalid CRS")

            # Test that errors are handled gracefully
            with self.assertRaises(Exception):
                download_images(
                    bounds=invalid_bounds,
                    assets=self.assets,
                    prefix=self.temp_dir,
                    input_crs=999999,  # Invalid CRS
                    start_date=self.start_date,
                    end_date=self.end_date,
                )

    def test_workflow_empty_results(self):
        """Test workflow with empty search results."""
        with patch("sentinel_timelapse.main.clipped_asset") as mock_clip:
            with patch(
                "sentinel_timelapse.main.filter_items_by_geometry"
            ) as mock_filter:
                with patch("sentinel_timelapse.main.search_stac_items") as mock_search:
                    with patch(
                        "sentinel_timelapse.main.bounds_to_geom_wgs84"
                    ) as mock_bounds:
                        # Setup mocks for empty results
                        mock_bounds.return_value = {
                            "type": "Polygon",
                            "coordinates": [],
                        }
                        mock_search.return_value = []
                        mock_filter.return_value = []

                        # Test with empty results
                        stats = download_images(
                            bounds=self.bounds,
                            assets=self.assets,
                            prefix=self.temp_dir,
                            start_date=self.start_date,
                            end_date=self.end_date,
                        )

                        # Verify empty results are handled correctly
                        self.assertEqual(stats["total_images"], 0)
                        self.assertEqual(stats["cloud_filtered"], 0)
                        self.assertEqual(stats["asset_counts"]["visual"], 0)
                        self.assertEqual(stats["asset_counts"]["B04"], 0)

                        # Verify no clipping was attempted
                        mock_clip.assert_not_called()


if __name__ == "__main__":
    unittest.main()
