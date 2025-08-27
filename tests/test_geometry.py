import unittest
import numpy as np
from shapely.geometry import box
import geopandas as gpd

from sentinel_timelapse.geometry import bounds_to_geom_wgs84


class TestGeometry(unittest.TestCase):
    """Test cases for geometry module functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Test bounds in UTM zone 19S (EPSG:24879)
        self.test_bounds_utm = (407500.0, 7494500.0, 415200.0, 7505700.0)
        # Expected WGS84 bounds (approximate)
        self.expected_wgs84_bounds = (-70.5, -24.5, -70.4, -24.4)
    
    def test_bounds_to_geom_wgs84_shapely_format(self):
        """Test bounds conversion to WGS84 in shapely format."""
        result = bounds_to_geom_wgs84(*self.test_bounds_utm, input_crs=24879, output_format='shapely')
        
        # Check that result is a shapely geometry
        self.assertTrue(hasattr(result, 'bounds'))
        self.assertTrue(hasattr(result, 'area'))
        
        # Check that coordinates are in WGS84 range
        bounds = result.bounds
        self.assertTrue(-180 <= bounds[0] <= 180)  # minx
        self.assertTrue(-180 <= bounds[2] <= 180)  # maxx
        self.assertTrue(-90 <= bounds[1] <= 90)    # miny
        self.assertTrue(-90 <= bounds[3] <= 90)    # maxy
    
    def test_bounds_to_geom_wgs84_json_format(self):
        """Test bounds conversion to WGS84 in JSON format."""
        result = bounds_to_geom_wgs84(*self.test_bounds_utm, input_crs=24879, output_format='json')
        
        # Check that result is a dictionary (GeoJSON)
        self.assertIsInstance(result, dict)
        self.assertIn('type', result)
        self.assertIn('coordinates', result)
        self.assertEqual(result['type'], 'Polygon')
    
    def test_bounds_to_geom_wgs84_different_crs(self):
        """Test bounds conversion with different input CRS."""
        # Test with WGS84 input (should return same coordinates)
        wgs84_bounds = (-70.5, -24.5, -70.4, -24.4)
        result = bounds_to_geom_wgs84(*wgs84_bounds, input_crs=4326, output_format='shapely')
        
        # Should be very close to input bounds
        result_bounds = result.bounds
        np.testing.assert_array_almost_equal(result_bounds, wgs84_bounds, decimal=6)
    
    def test_bounds_to_geom_wgs84_string_crs(self):
        """Test bounds conversion with string CRS input."""
        result = bounds_to_geom_wgs84(*self.test_bounds_utm, input_crs='EPSG:24879', output_format='shapely')
        
        # Check that result is a valid geometry
        self.assertTrue(hasattr(result, 'bounds'))
        bounds = result.bounds
        self.assertTrue(-180 <= bounds[0] <= 180)
        self.assertTrue(-180 <= bounds[2] <= 180)
        self.assertTrue(-90 <= bounds[1] <= 90)
        self.assertTrue(-90 <= bounds[3] <= 90)
    
    def test_bounds_to_geom_wgs84_invalid_crs(self):
        """Test bounds conversion with invalid CRS."""
        with self.assertRaises(Exception):
            bounds_to_geom_wgs84(*self.test_bounds_utm, input_crs=999999, output_format='shapely')
    
    def test_bounds_to_geom_wgs84_invalid_format(self):
        """Test bounds conversion with invalid output format."""
        # The function doesn't validate output_format, so it should still work
        # but return a shapely geometry instead of the expected format
        result = bounds_to_geom_wgs84(*self.test_bounds_utm, input_crs=24879, output_format='invalid_format')
        
        # Should still return a shapely geometry (default behavior)
        # The function uses mapping() for non-shapely formats, which returns a dict
        self.assertIsInstance(result, dict)
        self.assertIn('type', result)
        self.assertIn('coordinates', result)


if __name__ == '__main__':
    unittest.main()
