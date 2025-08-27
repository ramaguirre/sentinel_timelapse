import unittest
from unittest.mock import Mock, patch, MagicMock
from shapely.geometry import box, mapping

from sentinel_timelapse.stac import search_stac_items, filter_items_by_geometry


class TestSTAC(unittest.TestCase):
    """Test cases for STAC module functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Test bounding box in WGS84
        self.test_bbox = mapping(box(-70.5, -24.5, -70.4, -24.4))
        self.test_datetime = "2023-01-01/2023-01-31"

        # Mock STAC item
        self.mock_item = Mock()
        self.mock_item.geometry = mapping(box(-70.5, -24.5, -70.4, -24.4))
        self.mock_item.id = "test_item_1"

        # Mock STAC item outside bounds
        self.mock_item_outside = Mock()
        self.mock_item_outside.geometry = mapping(box(-71.0, -25.0, -70.9, -24.9))
        self.mock_item_outside.id = "test_item_2"

    @patch("sentinel_timelapse.stac.pystac_client.Client.open")
    def test_search_stac_items_success(self, mock_client_open):
        """Test successful STAC item search."""
        # Mock the catalog and search
        mock_catalog = Mock()
        mock_search = Mock()
        mock_search.items.return_value = [self.mock_item]

        mock_catalog.search.return_value = mock_search
        mock_client_open.return_value = mock_catalog

        # Test the function
        result = search_stac_items(self.test_bbox, self.test_datetime)

        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "test_item_1")

        # Verify the search was called with correct parameters
        mock_catalog.search.assert_called_once_with(
            collections=["sentinel-2-l2a"],
            intersects=self.test_bbox,
            datetime=self.test_datetime,
        )

    @patch("sentinel_timelapse.stac.pystac_client.Client.open")
    def test_search_stac_items_custom_collection(self, mock_client_open):
        """Test STAC item search with custom collection."""
        # Mock the catalog and search
        mock_catalog = Mock()
        mock_search = Mock()
        mock_search.items.return_value = [self.mock_item]

        mock_catalog.search.return_value = mock_search
        mock_client_open.return_value = mock_catalog

        # Test with custom collection
        result = search_stac_items(
            self.test_bbox, self.test_datetime, collection="sentinel-2-l1c"
        )

        # Verify the search was called with custom collection
        mock_catalog.search.assert_called_once_with(
            collections=["sentinel-2-l1c"],
            intersects=self.test_bbox,
            datetime=self.test_datetime,
        )

    @patch("sentinel_timelapse.stac.pystac_client.Client.open")
    def test_search_stac_items_empty_result(self, mock_client_open):
        """Test STAC item search with empty result."""
        # Mock the catalog and search
        mock_catalog = Mock()
        mock_search = Mock()
        mock_search.items.return_value = []

        mock_catalog.search.return_value = mock_search
        mock_client_open.return_value = mock_catalog

        # Test the function
        result = search_stac_items(self.test_bbox, self.test_datetime)

        # Verify the result is empty
        self.assertEqual(len(result), 0)

    @patch("sentinel_timelapse.stac.pystac_client.Client.open")
    def test_search_stac_items_connection_error(self, mock_client_open):
        """Test STAC item search with connection error."""
        # Mock connection error
        mock_client_open.side_effect = Exception("Connection failed")

        # Test the function should raise an exception
        with self.assertRaises(Exception):
            search_stac_items(self.test_bbox, self.test_datetime)

    def test_filter_items_by_geometry_success(self):
        """Test filtering items by geometry."""
        items = [self.mock_item, self.mock_item_outside]
        bbox_geom = box(-70.5, -24.5, -70.4, -24.4)

        # Test the function
        result = filter_items_by_geometry(items, bbox_geom)

        # Verify only the item within bounds is returned
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "test_item_1")

    def test_filter_items_by_geometry_empty_input(self):
        """Test filtering items with empty input."""
        items = []
        bbox_geom = box(-70.5, -24.5, -70.4, -24.4)

        # Test the function
        result = filter_items_by_geometry(items, bbox_geom)

        # Verify empty result
        self.assertEqual(len(result), 0)

    def test_filter_items_by_geometry_no_matches(self):
        """Test filtering items with no matches."""
        items = [self.mock_item_outside]  # Item outside bounds
        bbox_geom = box(-70.5, -24.5, -70.4, -24.4)

        # Test the function
        result = filter_items_by_geometry(items, bbox_geom)

        # Verify no matches
        self.assertEqual(len(result), 0)

    def test_filter_items_by_geometry_invalid_geometry(self):
        """Test filtering items with invalid geometry."""
        items = [self.mock_item]

        # Create invalid geometry
        invalid_geom = Mock()
        invalid_geom.contains.side_effect = Exception("Invalid geometry")

        # Test the function should handle the error gracefully
        with self.assertRaises(Exception):
            filter_items_by_geometry(items, invalid_geom)


if __name__ == "__main__":
    unittest.main()
