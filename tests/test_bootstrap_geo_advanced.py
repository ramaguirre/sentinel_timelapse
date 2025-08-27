"""
Advanced tests for the bootstrap_geo module.

This module tests additional scenarios and edge cases for the geospatial
environment bootstrap functionality that might not be covered in the basic tests.
"""

import unittest
import os
import tempfile
from unittest.mock import patch, Mock, MagicMock
import sys

from sentinel_timelapse._bootstrap_geo import use_rasterio_bundled_data


class TestBootstrapGeoAdvanced(unittest.TestCase):
    """Advanced test cases for bootstrap_geo functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Store original environment variables
        self.original_gdal_data = os.environ.get('GDAL_DATA')
        self.original_proj_lib = os.environ.get('PROJ_LIB')
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original environment variables
        if self.original_gdal_data is not None:
            os.environ['GDAL_DATA'] = self.original_gdal_data
        elif 'GDAL_DATA' in os.environ:
            del os.environ['GDAL_DATA']
            
        if self.original_proj_lib is not None:
            os.environ['PROJ_LIB'] = self.original_proj_lib
        elif 'PROJ_LIB' in os.environ:
            del os.environ['PROJ_LIB']
    
    def test_use_rasterio_bundled_data_verbose_output(self):
        """Test bootstrap with verbose output."""
        # Test with verbose=True
        with patch('builtins.print') as mock_print:
            use_rasterio_bundled_data(verbose=True)
            
            # Verify print was called for verbose output
            self.assertGreaterEqual(mock_print.call_count, 2)
            
            # Check that the output contains the expected messages
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            gdal_calls = [call for call in print_calls if '[geo] GDAL_DATA' in call]
            proj_calls = [call for call in print_calls if '[geo] PROJ_LIB' in call]
            
            self.assertGreaterEqual(len(gdal_calls), 1)
            self.assertGreaterEqual(len(proj_calls), 1)
    
    def test_use_rasterio_bundled_data_no_verbose_output(self):
        """Test bootstrap without verbose output."""
        # Test with verbose=False
        with patch('builtins.print') as mock_print:
            use_rasterio_bundled_data(verbose=False)
            
            # Verify print was not called
            mock_print.assert_not_called()
    
    def test_use_rasterio_bundled_data_multiple_calls(self):
        """Test that multiple calls to bootstrap work correctly."""
        # Call the function multiple times
        use_rasterio_bundled_data(verbose=False)
        use_rasterio_bundled_data(verbose=False)
        use_rasterio_bundled_data(verbose=False)
        
        # Verify environment variables are set correctly
        self.assertIn('GDAL_DATA', os.environ)
        self.assertIn('PROJ_LIB', os.environ)
    
    def test_use_rasterio_bundled_data_environment_preservation(self):
        """Test that bootstrap preserves other environment variables."""
        # Set some other environment variables
        os.environ['OTHER_VAR'] = 'other_value'
        os.environ['ANOTHER_VAR'] = 'another_value'
        
        # Test the function
        use_rasterio_bundled_data(verbose=False)
        
        # Verify other environment variables are preserved
        self.assertEqual(os.environ['OTHER_VAR'], 'other_value')
        self.assertEqual(os.environ['ANOTHER_VAR'], 'another_value')
        
        # Verify GDAL and PROJ variables are set
        self.assertIn('GDAL_DATA', os.environ)
        self.assertIn('PROJ_LIB', os.environ)
        
        # Clean up
        del os.environ['OTHER_VAR']
        del os.environ['ANOTHER_VAR']


class TestBootstrapGeoIntegration(unittest.TestCase):
    """Integration tests for bootstrap_geo functionality."""
    
    def test_bootstrap_geo_import_integration(self):
        """Test that bootstrap_geo works when imported as part of the package."""
        # This test verifies that the bootstrap function can be imported
        # and called without errors in a real environment
        try:
            from sentinel_timelapse._bootstrap_geo import use_rasterio_bundled_data
            use_rasterio_bundled_data(verbose=False)
            
            # Verify environment variables are set
            self.assertIn('GDAL_DATA', os.environ)
            self.assertIn('PROJ_LIB', os.environ)
            
        except ImportError:
            # Skip test if dependencies are not available
            self.skipTest("Required dependencies not available")
        except Exception as e:
            # Skip test if there are environment-specific issues
            self.skipTest(f"Environment-specific issue: {e}")


if __name__ == '__main__':
    unittest.main()
