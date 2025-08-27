"""
Tests for edge cases and error scenarios.

This module tests various edge cases, error conditions, and boundary scenarios
that might not be covered by the standard functionality tests.
"""

import unittest
import tempfile
import os
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from shapely.geometry import box, mapping

from sentinel_timelapse.geometry import bounds_to_geom_wgs84
from sentinel_timelapse.stac import search_stac_items, filter_items_by_geometry
from sentinel_timelapse.processing import clipped_asset
from sentinel_timelapse.main import download_images


class TestEdgeCases(unittest.TestCase):
    """Test cases for edge cases and error scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Test parameters
        self.bounds = (407500.0, 7494500.0, 415200.0, 7505700.0)
        self.assets = ["visual", "B04"]
        self.start_date = "2023-01-01"
        self.end_date = "2023-01-31"

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_bounds_to_geom_wgs84_zero_bounds(self):
        """Test geometry conversion with zero-size bounds."""
        # Test with bounds that have zero width or height
        zero_width_bounds = (100.0, 100.0, 100.0, 200.0)  # Zero width
        zero_height_bounds = (100.0, 100.0, 200.0, 100.0)  # Zero height

        # These should still work and produce valid geometries
        geom1 = bounds_to_geom_wgs84(*zero_width_bounds, input_crs=4326)
        geom2 = bounds_to_geom_wgs84(*zero_height_bounds, input_crs=4326)

        self.assertIsNotNone(geom1)
        self.assertIsNotNone(geom2)

    def test_bounds_to_geom_wgs84_negative_bounds(self):
        """Test geometry conversion with negative coordinates."""
        # Test with negative coordinates (common in WGS84)
        negative_bounds = (-70.5, -24.5, -70.4, -24.4)

        geom = bounds_to_geom_wgs84(*negative_bounds, input_crs=4326)
        self.assertIsNotNone(geom)

        # Check that the geometry has the expected bounds
        if hasattr(geom, "bounds"):
            self.assertLess(geom.bounds[0], geom.bounds[2])  # xmin < xmax
            self.assertLess(geom.bounds[1], geom.bounds[3])  # ymin < ymax

    def test_bounds_to_geom_wgs84_large_numbers(self):
        """Test geometry conversion with very large coordinates."""
        # Test with very large UTM coordinates
        large_bounds = (5000000.0, 9000000.0, 5010000.0, 9010000.0)

        geom = bounds_to_geom_wgs84(*large_bounds, input_crs=32719)
        self.assertIsNotNone(geom)

    def test_bounds_to_geom_wgs84_invalid_crs(self):
        """Test geometry conversion with invalid CRS."""
        # Test with an invalid CRS code
        with self.assertRaises(Exception):
            bounds_to_geom_wgs84(*self.bounds, input_crs=999999)

    def test_bounds_to_geom_wgs84_string_crs(self):
        """Test geometry conversion with string CRS."""
        # Test with string CRS format
        geom = bounds_to_geom_wgs84(*self.bounds, input_crs="EPSG:24879")
        self.assertIsNotNone(geom)

        # Test with different string format
        geom2 = bounds_to_geom_wgs84(
            *self.bounds, input_crs="+proj=utm +zone=19 +south"
        )
        self.assertIsNotNone(geom2)

    def test_bounds_to_geom_wgs84_output_formats(self):
        """Test geometry conversion with different output formats."""
        # Test all output format options
        shapely_geom = bounds_to_geom_wgs84(*self.bounds, output_format="shapely")
        json_geom = bounds_to_geom_wgs84(*self.bounds, output_format="json")
        default_geom = bounds_to_geom_wgs84(*self.bounds, output_format="invalid")

        # Check that shapely format returns a shapely geometry
        self.assertTrue(hasattr(shapely_geom, "bounds"))

        # Check that json and invalid formats return dictionaries
        self.assertIsInstance(json_geom, dict)
        self.assertIsInstance(default_geom, dict)
        self.assertIn("type", json_geom)
        self.assertIn("coordinates", json_geom)

    @patch("sentinel_timelapse.stac.pystac_client.Client.open")
    def test_search_stac_items_empty_collection(self, mock_client_open):
        """Test STAC search with empty collection."""
        # Mock empty collection
        mock_catalog = Mock()
        mock_search = Mock()
        mock_search.items.return_value = []
        mock_catalog.search.return_value = mock_search
        mock_client_open.return_value = mock_catalog

        bbox = bounds_to_geom_wgs84(*self.bounds, output_format="json")
        items = search_stac_items(bbox, f"{self.start_date}/{self.end_date}")

        self.assertEqual(len(items), 0)

    @patch("sentinel_timelapse.stac.pystac_client.Client.open")
    def test_search_stac_items_connection_error(self, mock_client_open):
        """Test STAC search with connection error."""
        # Mock connection error
        mock_client_open.side_effect = Exception("Connection failed")

        bbox = bounds_to_geom_wgs84(*self.bounds, output_format="json")

        with self.assertRaises(Exception):
            search_stac_items(bbox, f"{self.start_date}/{self.end_date}")

    def test_filter_items_by_geometry_empty_items(self):
        """Test geometry filtering with empty items list."""
        bbox_geom = bounds_to_geom_wgs84(*self.bounds, output_format="shapely")
        filtered = filter_items_by_geometry([], bbox_geom)

        self.assertEqual(len(filtered), 0)

    def test_filter_items_by_geometry_no_intersection(self):
        """Test geometry filtering with no intersecting items."""
        # Create mock items that don't intersect with our bounds
        mock_item1 = Mock()
        mock_item1.geometry = mapping(box(0, 0, 1, 1))  # Far from our bounds

        mock_item2 = Mock()
        mock_item2.geometry = mapping(
            box(1000000, 1000000, 1000001, 1000001)
        )  # Very far

        bbox_geom = bounds_to_geom_wgs84(*self.bounds, output_format="shapely")
        filtered = filter_items_by_geometry([mock_item1, mock_item2], bbox_geom)

        self.assertEqual(len(filtered), 0)

    @patch("sentinel_timelapse.processing.planetary_computer.sign")
    @patch("sentinel_timelapse.processing.rasterio.open")
    def test_clipped_asset_bounds_completely_outside(
        self, mock_rasterio_open, mock_sign
    ):
        """Test asset clipping with bounds completely outside image."""
        # Mock signed item
        mock_signed_item = Mock()
        mock_asset = Mock()
        mock_asset.href = "https://example.com/test.tif"
        mock_signed_item.assets = {"visual": mock_asset}
        mock_sign.return_value = mock_signed_item

        # Mock raster with bounds that don't intersect at all
        mock_dataset = Mock()
        mock_dataset.crs = Mock()
        mock_dataset.crs.to_epsg.return_value = 32719
        mock_dataset.bounds = Mock()
        mock_dataset.bounds.left = 0
        mock_dataset.bounds.right = 1000
        mock_dataset.bounds.bottom = 0
        mock_dataset.bounds.top = 1000

        mock_rasterio_open.return_value.__enter__.return_value = mock_dataset

        # Test with bounds completely outside the image
        result = clipped_asset(
            Mock(), 100000, 100000, 101000, 101000, asset_name="visual"  # Far outside
        )

        # Should handle the error gracefully
        self.assertIsNone(result)

    @patch("sentinel_timelapse.processing.planetary_computer.sign")
    def test_clipped_asset_missing_asset_keyerror(self, mock_sign):
        """Test asset clipping with missing asset (KeyError)."""
        # Mock signed item with missing asset
        mock_signed_item = Mock()
        mock_signed_item.assets = {}  # No assets
        mock_sign.return_value = mock_signed_item

        # Test with missing asset
        with self.assertRaises(KeyError):
            clipped_asset(Mock(), *self.bounds, asset_name="missing_asset")

    @patch("sentinel_timelapse.processing.planetary_computer.sign")
    @patch("sentinel_timelapse.processing.rasterio.open")
    def test_clipped_asset_rasterio_ioerror(self, mock_rasterio_open, mock_sign):
        """Test asset clipping with rasterio IO error."""
        # Mock signed item
        mock_signed_item = Mock()
        mock_asset = Mock()
        mock_asset.href = "https://example.com/test.tif"
        mock_signed_item.assets = {"visual": mock_asset}
        mock_sign.return_value = mock_signed_item

        # Mock rasterio error
        mock_rasterio_open.side_effect = Exception("File not found")

        # Test with IO error
        result = clipped_asset(Mock(), *self.bounds, asset_name="visual")

        # Should handle the error gracefully
        self.assertIsNone(result)

    @patch("sentinel_timelapse.main.search_stac_items")
    @patch("sentinel_timelapse.main.filter_items_by_geometry")
    @patch("sentinel_timelapse.main.clipped_asset")
    def test_download_images_no_items_found(self, mock_clip, mock_filter, mock_search):
        """Test download_images with no items found."""
        # Mock empty search results
        mock_search.return_value = []
        mock_filter.return_value = []

        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.temp_dir,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        self.assertEqual(stats["total_images"], 0)
        self.assertEqual(stats["cloud_filtered"], 0)
        self.assertEqual(stats["asset_counts"]["visual"], 0)
        self.assertEqual(stats["asset_counts"]["B04"], 0)

        # Should not call clipped_asset when no items
        mock_clip.assert_not_called()

    @patch("sentinel_timelapse.main.search_stac_items")
    @patch("sentinel_timelapse.main.filter_items_by_geometry")
    @patch("sentinel_timelapse.main.clipped_asset")
    def test_download_images_all_cloudy(self, mock_clip, mock_filter, mock_search):
        """Test download_images with all images filtered by clouds."""
        # Mock items
        mock_item1 = Mock()
        mock_item1.id = "test_item_1"
        mock_item2 = Mock()
        mock_item2.id = "test_item_2"

        mock_search.return_value = [mock_item1, mock_item2]
        mock_filter.return_value = [mock_item1, mock_item2]

        # Mock high cloud coverage for all items
        def mock_clip_side_effect(*args, **kwargs):
            if kwargs.get("asset_name") == "SCL" and kwargs.get("return_data_dic"):
                # Return high cloud coverage data
                cloud_data = np.random.randint(8, 11, (1, 100, 100))
                return {"data": [cloud_data]}
            return None

        mock_clip.side_effect = mock_clip_side_effect

        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.temp_dir,
            start_date=self.start_date,
            end_date=self.end_date,
            max_cloud_pct=5,  # Low threshold
        )

        self.assertEqual(stats["total_images"], 2)
        self.assertEqual(stats["cloud_filtered"], 2)
        self.assertEqual(stats["asset_counts"]["visual"], 0)
        self.assertEqual(stats["asset_counts"]["B04"], 0)

    @patch("sentinel_timelapse.main.search_stac_items")
    @patch("sentinel_timelapse.main.filter_items_by_geometry")
    @patch("sentinel_timelapse.main.clipped_asset")
    def test_download_images_scl_none(self, mock_clip, mock_filter, mock_search):
        """Test download_images when SCL data is None."""
        # Mock items
        mock_item = Mock()
        mock_item.id = "test_item"

        mock_search.return_value = [mock_item]
        mock_filter.return_value = [mock_item]

        # Mock SCL returning None
        def mock_clip_side_effect(*args, **kwargs):
            if kwargs.get("asset_name") == "SCL" and kwargs.get("return_data_dic"):
                return None  # SCL data unavailable
            return None

        mock_clip.side_effect = mock_clip_side_effect

        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.temp_dir,
            start_date=self.start_date,
            end_date=self.end_date,
            max_cloud_pct=5,
        )

        # Should process the item even if SCL is None
        self.assertEqual(stats["total_images"], 1)
        self.assertEqual(stats["cloud_filtered"], 0)
        self.assertEqual(stats["asset_counts"]["visual"], 1)
        self.assertEqual(stats["asset_counts"]["B04"], 1)

    @patch("sentinel_timelapse.main.search_stac_items")
    @patch("sentinel_timelapse.main.filter_items_by_geometry")
    @patch("sentinel_timelapse.main.clipped_asset")
    def test_download_images_no_cloud_filtering(
        self, mock_clip, mock_filter, mock_search
    ):
        """Test download_images with cloud filtering disabled."""
        # Mock items
        mock_item = Mock()
        mock_item.id = "test_item"

        mock_search.return_value = [mock_item]
        mock_filter.return_value = [mock_item]

        # Mock asset clipping
        def mock_clip_side_effect(*args, **kwargs):
            return None

        mock_clip.side_effect = mock_clip_side_effect

        stats = download_images(
            bounds=self.bounds,
            assets=self.assets,
            prefix=self.temp_dir,
            start_date=self.start_date,
            end_date=self.end_date,
            max_cloud_pct=None,  # Disable cloud filtering
        )

        # Should process all items without cloud filtering
        self.assertEqual(stats["total_images"], 1)
        self.assertEqual(stats["cloud_filtered"], 0)
        self.assertEqual(stats["asset_counts"]["visual"], 1)
        self.assertEqual(stats["asset_counts"]["B04"], 1)

        # Should not call clipped_asset for SCL when cloud filtering is disabled
        scl_calls = [
            call
            for call in mock_clip.call_args_list
            if call[1].get("asset_name") == "SCL"
        ]
        self.assertEqual(len(scl_calls), 0)

    def test_download_images_single_asset_string(self):
        """Test download_images with single asset as string."""
        with patch("sentinel_timelapse.main.search_stac_items") as mock_search:
            with patch(
                "sentinel_timelapse.main.filter_items_by_geometry"
            ) as mock_filter:
                with patch("sentinel_timelapse.main.clipped_asset") as mock_clip:
                    # Mock empty results
                    mock_search.return_value = []
                    mock_filter.return_value = []

                    stats = download_images(
                        bounds=self.bounds,
                        assets="visual",  # Single asset as string
                        prefix=self.temp_dir,
                        start_date=self.start_date,
                        end_date=self.end_date,
                    )

                    self.assertEqual(stats["asset_counts"]["visual"], 0)

    def test_download_images_invalid_bounds(self):
        """Test download_images with invalid bounds."""
        # Test with bounds that have xmin > xmax
        invalid_bounds = (415200.0, 7494500.0, 407500.0, 7505700.0)  # xmin > xmax

        with patch("sentinel_timelapse.main.bounds_to_geom_wgs84") as mock_bounds:
            mock_bounds.side_effect = Exception("Invalid bounds")

            with self.assertRaises(Exception):
                download_images(
                    bounds=invalid_bounds,
                    assets=self.assets,
                    prefix=self.temp_dir,
                    start_date=self.start_date,
                    end_date=self.end_date,
                )


class TestBoundaryConditions(unittest.TestCase):
    """Test cases for boundary conditions and limits."""

    def test_bounds_to_geom_wgs84_extreme_coordinates(self):
        """Test geometry conversion with extreme coordinate values."""
        # Test with very large coordinates
        extreme_bounds = (1e6, 1e6, 1e6 + 1000, 1e6 + 1000)

        geom = bounds_to_geom_wgs84(*extreme_bounds, input_crs=32719)
        self.assertIsNotNone(geom)

    def test_bounds_to_geom_wgs84_small_coordinates(self):
        """Test geometry conversion with very small coordinate differences."""
        # Test with very small bounding box
        small_bounds = (100.0, 100.0, 100.0001, 100.0001)

        geom = bounds_to_geom_wgs84(*small_bounds, input_crs=4326)
        self.assertIsNotNone(geom)

    def test_bounds_to_geom_wgs84_negative_crs(self):
        """Test geometry conversion with negative CRS codes."""
        # Test with negative CRS (should fail)
        with self.assertRaises(Exception):
            bounds_to_geom_wgs84(100, 100, 200, 200, input_crs=-1)


if __name__ == "__main__":
    unittest.main()
