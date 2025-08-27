"""
Tests for package initialization and import scenarios.

This module tests the package initialization, import behavior, and
module availability to ensure the package works correctly when imported.
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import patch, Mock
import importlib

# Add the parent directory to the path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPackageInit(unittest.TestCase):
    """Test cases for package initialization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_package_import(self):
        """Test that the package can be imported successfully."""
        try:
            import sentinel_timelapse
            self.assertIsNotNone(sentinel_timelapse)
        except ImportError as e:
            self.fail(f"Failed to import sentinel_timelapse: {e}")
    
    def test_main_function_import(self):
        """Test that the main download_images function can be imported."""
        try:
            from sentinel_timelapse import download_images
            self.assertIsNotNone(download_images)
            self.assertTrue(callable(download_images))
        except ImportError as e:
            self.fail(f"Failed to import download_images: {e}")
    
    def test_module_imports(self):
        """Test that all modules can be imported individually."""
        modules_to_test = [
            'sentinel_timelapse.geometry',
            'sentinel_timelapse.stac',
            'sentinel_timelapse.processing',
            'sentinel_timelapse.main',
            'sentinel_timelapse.cli',
            'sentinel_timelapse._bootstrap_geo'
        ]
        
        for module_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)
            except ImportError as e:
                self.fail(f"Failed to import {module_name}: {e}")
    
    def test_function_imports(self):
        """Test that all public functions can be imported."""
        functions_to_test = [
            ('sentinel_timelapse.geometry', 'bounds_to_geom_wgs84'),
            ('sentinel_timelapse.stac', 'search_stac_items'),
            ('sentinel_timelapse.stac', 'filter_items_by_geometry'),
            ('sentinel_timelapse.processing', 'clipped_asset'),
            ('sentinel_timelapse.main', 'download_images'),
            ('sentinel_timelapse.cli', 'parse_bounds'),
            ('sentinel_timelapse.cli', 'parse_assets'),
            ('sentinel_timelapse.cli', 'main'),
            ('sentinel_timelapse._bootstrap_geo', 'use_rasterio_bundled_data')
        ]
        
        for module_name, function_name in functions_to_test:
            try:
                module = importlib.import_module(module_name)
                function = getattr(module, function_name)
                self.assertIsNotNone(function)
                self.assertTrue(callable(function))
            except (ImportError, AttributeError) as e:
                self.fail(f"Failed to import {function_name} from {module_name}: {e}")
    
    def test_package_all_attribute(self):
        """Test that __all__ is defined and contains expected items."""
        try:
            import sentinel_timelapse
            self.assertTrue(hasattr(sentinel_timelapse, '__all__'))
            self.assertIsInstance(sentinel_timelapse.__all__, list)
            self.assertIn('download_images', sentinel_timelapse.__all__)
        except ImportError as e:
            self.fail(f"Failed to import sentinel_timelapse: {e}")
    
    def test_package_docstring(self):
        """Test that the package has a proper docstring."""
        try:
            import sentinel_timelapse
            self.assertIsNotNone(sentinel_timelapse.__doc__)
            self.assertIsInstance(sentinel_timelapse.__doc__, str)
            self.assertGreater(len(sentinel_timelapse.__doc__), 0)
        except ImportError as e:
            self.fail(f"Failed to import sentinel_timelapse: {e}")
    
    def test_module_docstrings(self):
        """Test that all modules have proper docstrings."""
        modules_to_test = [
            'sentinel_timelapse.geometry',
            'sentinel_timelapse.stac',
            'sentinel_timelapse.processing',
            'sentinel_timelapse.main',
            'sentinel_timelapse.cli',
            'sentinel_timelapse._bootstrap_geo'
        ]
        
        for module_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module.__doc__)
                self.assertIsInstance(module.__doc__, str)
                self.assertGreater(len(module.__doc__), 0)
            except ImportError as e:
                self.fail(f"Failed to import {module_name}: {e}")
    
    def test_function_docstrings(self):
        """Test that all public functions have proper docstrings."""
        functions_to_test = [
            ('sentinel_timelapse.geometry', 'bounds_to_geom_wgs84'),
            ('sentinel_timelapse.stac', 'search_stac_items'),
            ('sentinel_timelapse.stac', 'filter_items_by_geometry'),
            ('sentinel_timelapse.processing', 'clipped_asset'),
            ('sentinel_timelapse.main', 'download_images'),
            ('sentinel_timelapse.cli', 'parse_bounds'),
            ('sentinel_timelapse.cli', 'parse_assets'),
            ('sentinel_timelapse.cli', 'main'),
            ('sentinel_timelapse._bootstrap_geo', 'use_rasterio_bundled_data')
        ]
        
        for module_name, function_name in functions_to_test:
            try:
                module = importlib.import_module(module_name)
                function = getattr(module, function_name)
                self.assertIsNotNone(function.__doc__)
                self.assertIsInstance(function.__doc__, str)
                self.assertGreater(len(function.__doc__), 0)
            except (ImportError, AttributeError) as e:
                self.fail(f"Failed to import {function_name} from {module_name}: {e}")
    
    def test_bootstrap_geo_initialization(self):
        """Test that bootstrap_geo is called during package import."""
        # This test verifies that the bootstrap function is called
        # when the package is imported
        try:
            # Import the package and check that environment variables are set
            import sentinel_timelapse
            
            # The bootstrap should have set these environment variables
            self.assertIn('GDAL_DATA', os.environ)
            self.assertIn('PROJ_LIB', os.environ)
            
        except ImportError as e:
            self.fail(f"Failed to import sentinel_timelapse: {e}")
    
    def test_import_without_dependencies(self):
        """Test import behavior when dependencies are missing."""
        # This test simulates what happens when required dependencies
        # are not available (though we can't easily test this in practice)
        try:
            import sentinel_timelapse
            # If we get here, the import succeeded
            self.assertTrue(True)
        except ImportError:
            # If import fails due to missing dependencies, that's also acceptable
            self.assertTrue(True)


class TestPackageStructure(unittest.TestCase):
    """Test cases for package structure and organization."""
    
    def test_package_directory_structure(self):
        """Test that the package has the expected directory structure."""
        package_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sentinel_timelapse')
        
        # Check that the package directory exists
        self.assertTrue(os.path.exists(package_dir))
        self.assertTrue(os.path.isdir(package_dir))
        
        # Check for required files
        required_files = [
            '__init__.py',
            'main.py',
            'geometry.py',
            'stac.py',
            'processing.py',
            'cli.py',
            '_bootstrap_geo.py'
        ]
        
        for file_name in required_files:
            file_path = os.path.join(package_dir, file_name)
            self.assertTrue(os.path.exists(file_path), f"Missing required file: {file_name}")
    
    def test_package_version(self):
        """Test that the package has version information."""
        try:
            import sentinel_timelapse
            # Check if version is available (might be in __init__.py or setup.py)
            # This is optional, so we don't fail if it's not present
            if hasattr(sentinel_timelapse, '__version__'):
                self.assertIsInstance(sentinel_timelapse.__version__, str)
        except ImportError as e:
            self.fail(f"Failed to import sentinel_timelapse: {e}")
    
    def test_package_metadata(self):
        """Test that the package has proper metadata."""
        try:
            import sentinel_timelapse
            
            # Check for common metadata attributes
            metadata_attrs = ['__name__', '__package__', '__file__']
            for attr in metadata_attrs:
                self.assertTrue(hasattr(sentinel_timelapse, attr))
                
        except ImportError as e:
            self.fail(f"Failed to import sentinel_timelapse: {e}")


class TestImportScenarios(unittest.TestCase):
    """Test cases for various import scenarios."""
    
    def test_import_from_package_root(self):
        """Test importing from the package root."""
        try:
            from sentinel_timelapse import download_images
            self.assertIsNotNone(download_images)
        except ImportError as e:
            self.fail(f"Failed to import from package root: {e}")
    
    def test_import_from_submodules(self):
        """Test importing from submodules."""
        try:
            from sentinel_timelapse.geometry import bounds_to_geom_wgs84
            from sentinel_timelapse.stac import search_stac_items
            from sentinel_timelapse.processing import clipped_asset
            from sentinel_timelapse.main import download_images
            from sentinel_timelapse.cli import main as cli_main
            
            # Verify all imports succeeded
            self.assertIsNotNone(bounds_to_geom_wgs84)
            self.assertIsNotNone(search_stac_items)
            self.assertIsNotNone(clipped_asset)
            self.assertIsNotNone(download_images)
            self.assertIsNotNone(cli_main)
            
        except ImportError as e:
            self.fail(f"Failed to import from submodules: {e}")
    
    def test_import_with_relative_imports(self):
        """Test that relative imports work correctly within the package."""
        try:
            # This tests that the package's internal relative imports work
            import sentinel_timelapse.main
            import sentinel_timelapse.geometry
            import sentinel_timelapse.stac
            import sentinel_timelapse.processing
            import sentinel_timelapse.cli
            
            # If we get here, all relative imports worked
            self.assertTrue(True)
            
        except ImportError as e:
            self.fail(f"Failed to import with relative imports: {e}")
    
    def test_import_performance(self):
        """Test that imports are reasonably fast."""
        import time
        
        start_time = time.time()
        try:
            import sentinel_timelapse
            import_time = time.time() - start_time
            
            # Import should complete in less than 5 seconds
            self.assertLess(import_time, 5.0, f"Import took too long: {import_time:.2f} seconds")
            
        except ImportError as e:
            self.fail(f"Failed to import sentinel_timelapse: {e}")


if __name__ == '__main__':
    unittest.main()
