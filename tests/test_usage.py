"""
Usage examples and integration tests for sentinel-timelapse.

This module provides practical examples of how to use the sentinel-timelapse
package and serves as integration tests to ensure the complete workflow
functions correctly.
"""

import unittest
import numpy as np
from unittest.mock import patch, Mock
from sentinel_timelapse import download_images


class TestUsageExamples(unittest.TestCase):
    """Test cases demonstrating usage examples."""

    def setUp(self):
        """Set up test fixtures."""
        # Define test parameters
        self.bounds = (407500.0, 7494500.0, 415200.0, 7505700.0)
        self.assets = ["visual", "B04"]
        self.prefix = "test_output"

    @patch("sentinel_timelapse.main.search_stac_items")
    @patch("sentinel_timelapse.main.filter_items_by_geometry")
    @patch("sentinel_timelapse.main.clipped_asset")
    def test_basic_usage_example(self, mock_clip, mock_filter, mock_search):
        """Test basic usage example from documentation."""
        # Mock STAC search results
        mock_item1 = Mock()
        mock_item1.id = "S2A_MSIL2A_20230101T123456_N0500_R123_T19HFA_20230101T123456"
        mock_item1.geometry = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        }
        mock_item1.properties = {"datetime": "2023-01-01T12:34:56Z"}
        mock_item1.assets = {"visual": Mock(), "B04": Mock(), "SCL": Mock()}

        mock_item2 = Mock()
        mock_item2.id = "S2A_MSIL2A_20230102T123456_N0500_R123_T19HFA_20230102T123456"
        mock_item2.geometry = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        }
        mock_item2.properties = {"datetime": "2023-01-02T12:34:56Z"}
        mock_item2.assets = {"visual": Mock(), "B04": Mock(), "SCL": Mock()}

        mock_search.return_value = [mock_item1, mock_item2]
        mock_filter.return_value = [mock_item1, mock_item2]

        # Mock clipped_asset to return cloud data for SCL
        def mock_clip_side_effect(*args, **kwargs):
            if kwargs.get("asset_name") == "SCL" and kwargs.get("return_data_dic"):
                # Return proper numpy array structure for SCL data
                scl_data = np.array(
                    [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
                )  # Low cloud coverage
                return {"data": scl_data}
            return None

        mock_clip.side_effect = mock_clip_side_effect

        # Execute the main function
        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.prefix,
            start_date="2023-01-01",
            end_date="2023-01-31",
            max_cloud_pct=10,
        )

        # Verify the results
        self.assertEqual(stats["total_images"], 2)
        self.assertEqual(stats["cloud_filtered"], 0)
        self.assertEqual(stats["asset_counts"]["visual"], 2)
        self.assertEqual(stats["asset_counts"]["B04"], 2)

    @patch("sentinel_timelapse.main.search_stac_items")
    @patch("sentinel_timelapse.main.filter_items_by_geometry")
    @patch("sentinel_timelapse.main.clipped_asset")
    def test_single_asset_usage(self, mock_clip, mock_filter, mock_search):
        """Test usage with a single asset."""
        # Mock STAC search results
        mock_item = Mock()
        mock_item.id = "S2A_MSIL2A_20230101T123456_N0500_R123_T19HFA_20230101T123456"
        mock_item.geometry = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        }
        mock_item.properties = {"datetime": "2023-01-01T12:34:56Z"}
        mock_item.assets = {"visual": Mock(), "SCL": Mock()}

        mock_search.return_value = [mock_item]
        mock_filter.return_value = [mock_item]

        # Mock clipped_asset
        def mock_clip_side_effect(*args, **kwargs):
            if kwargs.get("asset_name") == "SCL" and kwargs.get("return_data_dic"):
                # Return proper numpy array structure for SCL data
                scl_data = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
                return {"data": scl_data}
            return None

        mock_clip.side_effect = mock_clip_side_effect

        # Execute with single asset (string)
        stats = download_images(
            bounds=self.bounds,
            assets="visual",
            prefix=self.prefix,
            start_date="2023-01-01",
            end_date="2023-01-31",
        )

        # Verify the results
        self.assertEqual(stats["total_images"], 1)
        self.assertEqual(stats["asset_counts"]["visual"], 1)

    @patch("sentinel_timelapse.main.search_stac_items")
    @patch("sentinel_timelapse.main.filter_items_by_geometry")
    @patch("sentinel_timelapse.main.clipped_asset")
    def test_no_cloud_filtering(self, mock_clip, mock_filter, mock_search):
        """Test usage without cloud filtering."""
        # Mock STAC search results
        mock_item = Mock()
        mock_item.id = "S2A_MSIL2A_20230101T123456_N0500_R123_T19HFA_20230101T123456"
        mock_item.geometry = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        }
        mock_item.properties = {"datetime": "2023-01-01T12:34:56Z"}
        mock_item.assets = {"visual": Mock()}

        mock_search.return_value = [mock_item]
        mock_filter.return_value = [mock_item]

        # Mock clipped_asset
        mock_clip.return_value = None

        # Execute without cloud filtering
        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.prefix,
            start_date="2023-01-01",
            end_date="2023-01-31",
            max_cloud_pct=None,  # No cloud filtering
        )

        # Verify the results
        self.assertEqual(stats["total_images"], 1)
        self.assertEqual(stats["cloud_filtered"], 0)
        self.assertEqual(stats["asset_counts"]["visual"], 1)
        self.assertEqual(stats["asset_counts"]["B04"], 1)


if __name__ == "__main__":
    unittest.main()
