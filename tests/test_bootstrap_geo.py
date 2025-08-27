import unittest
import os
from unittest.mock import patch, Mock

from sentinel_timelapse._bootstrap_geo import use_rasterio_bundled_data


class TestBootstrapGeo(unittest.TestCase):
    """Test cases for bootstrap_geo module functions."""
    
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
    
    def test_use_rasterio_bundled_data_basic(self):
        """Test basic rasterio bundled data configuration."""
        # This test will only run if the required dependencies are available
        try:
            use_rasterio_bundled_data(verbose=False)
            
            # Verify environment variables were set
            self.assertIn('GDAL_DATA', os.environ)
            self.assertIn('PROJ_LIB', os.environ)
            
        except ImportError:
            # Skip test if dependencies are not available
            self.skipTest("Required dependencies not available")
    
    def test_use_rasterio_bundled_data_verbose(self):
        """Test rasterio bundled data configuration with verbose output."""
        try:
            with patch('builtins.print') as mock_print:
                use_rasterio_bundled_data(verbose=True)
                
                # Verify print was called for verbose output
                self.assertGreaterEqual(mock_print.call_count, 2)
                
        except ImportError:
            # Skip test if dependencies are not available
            self.skipTest("Required dependencies not available")
    
    def test_use_rasterio_bundled_data_clears_existing_env_vars(self):
        """Test that existing environment variables are cleared."""
        # Set existing environment variables
        os.environ['GDAL_DATA'] = '/old/gdal/data'
        os.environ['PROJ_LIB'] = '/old/proj/lib'
        
        try:
            use_rasterio_bundled_data(verbose=False)
            
            # Verify old values were replaced
            self.assertNotEqual(os.environ['GDAL_DATA'], '/old/gdal/data')
            self.assertNotEqual(os.environ['PROJ_LIB'], '/old/proj/lib')
            
        except ImportError:
            # Skip test if dependencies are not available
            self.skipTest("Required dependencies not available")


if __name__ == '__main__':
    unittest.main()

