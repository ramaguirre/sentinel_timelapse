"""
Unit tests for the STAC module.

This module contains comprehensive unit tests for the STAC (SpatioTemporal Asset Catalog)
utilities, including tests for searching STAC items and filtering by geometry.
"""

import unittest
from unittest.mock import patch, Mock
from shapely.geometry import box, mapping

from sentinel_timelapse.stac import search_stac_items, filter_items_by_geometry


class TestSTAC(unittest.TestCase):
    """Test cases for STAC module functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock bounding box for testing
        self.bbox = mapping(box(0, 0, 1, 1))
        self.datetime_range = "2023-01-01/2023-01-31"

    @patch('sentinel_timelapse.stac.pystac_client.Client.open')
    def test_search_stac_items_success(self, mock_client_open):
        """Test successful STAC item search."""
        # Mock the STAC client and search results
        mock_catalog = Mock()
        mock_search = Mock()
        mock_items = [Mock(), Mock(), Mock()]
        mock_search.items.return_value = mock_items
        mock_catalog.search.return_value = mock_search
        mock_client_open.return_value = mock_catalog

        # Execute the function
        result = search_stac_items(self.bbox, self.datetime_range)

        # Verify the results
        self.assertEqual(len(result), 3)
        mock_catalog.search.assert_called_once_with(
            collections=["sentinel-2-l2a"],
            intersects=self.bbox,
            datetime=self.datetime_range
        )

    @patch('sentinel_timelapse.stac.pystac_client.Client.open')
    def test_search_stac_items_custom_collection(self, mock_client_open):
        """Test STAC search with custom collection."""
        # Mock the STAC client and search results
        mock_catalog = Mock()
        mock_search = Mock()
        mock_search.items.return_value = []
        mock_catalog.search.return_value = mock_search
        mock_client_open.return_value = mock_catalog

        # Execute the function with custom collection
        search_stac_items(self.bbox, self.datetime_range, collection="sentinel-2-l1c")

        # Verify the collection parameter was used
        mock_catalog.search.assert_called_once_with(
            collections=["sentinel-2-l1c"],
            intersects=self.bbox,
            datetime=self.datetime_range
        )

    @patch('sentinel_timelapse.stac.pystac_client.Client.open')
    def test_search_stac_items_connection_error(self, mock_client_open):
        """Test STAC search with connection error."""
        # Mock connection error
        mock_client_open.side_effect = Exception("Connection failed")

        # Execute and verify exception is raised
        with self.assertRaises(Exception):
            search_stac_items(self.bbox, self.datetime_range)

    def test_filter_items_by_geometry_success(self):
        """Test successful geometry filtering."""
        # Create mock items with geometries that contain our bbox
        # The bbox is (0,0,1,1), so we need geometries that fully contain this area
        item1 = Mock()
        item1.geometry = mapping(box(-1, -1, 2, 2))  # Large polygon containing our bbox
        item2 = Mock()
        item2.geometry = mapping(box(-0.5, -0.5, 1.5, 1.5))  # Polygon that contains our bbox
        item3 = Mock()
        item3.geometry = mapping(box(2, 2, 3, 3))  # Does not contain our bbox

        items = [item1, item2, item3]

        # Execute the function
        filtered_items = filter_items_by_geometry(items, self.bbox)

        # Verify only items containing the bbox are returned
        self.assertEqual(len(filtered_items), 2)
        self.assertIn(item1, filtered_items)
        self.assertIn(item2, filtered_items)
        self.assertNotIn(item3, filtered_items)

    def test_filter_items_by_geometry_empty_list(self):
        """Test geometry filtering with empty item list."""
        # Execute with empty list
        result = filter_items_by_geometry([], self.bbox)

        # Verify empty list is returned
        self.assertEqual(result, [])

    def test_filter_items_by_geometry_no_intersection(self):
        """Test geometry filtering when no items intersect."""
        # Create mock items that don't contain our bbox
        item1 = Mock()
        item1.geometry = mapping(box(2, 2, 3, 3))
        item2 = Mock()
        item2.geometry = mapping(box(3, 3, 4, 4))

        items = [item1, item2]

        # Execute the function
        filtered_items = filter_items_by_geometry(items, self.bbox)

        # Verify no items are returned
        self.assertEqual(filtered_items, [])

    def test_filter_items_by_geometry_invalid_geometry(self):
        """Test geometry filtering with invalid geometry."""
        # Create mock item with invalid geometry
        item = Mock()
        item.geometry = {"type": "Invalid", "coordinates": []}

        # Execute and verify exception is raised
        with self.assertRaises(Exception):
            filter_items_by_geometry([item], self.bbox)


if __name__ == '__main__':
    unittest.main()
