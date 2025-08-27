"""
Tests for the command line interface (CLI) functionality.

This module tests the CLI argument parsing, validation, and execution
of the sentinel-timelapse command line tool.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, Mock
from io import StringIO
import subprocess

from sentinel_timelapse.cli import parse_bounds, parse_assets, main


class TestCLI(unittest.TestCase):
    """Test cases for CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        
        # Test parameters
        self.test_bounds = ['407500.0', '7494500.0', '415200.0', '7505700.0']
        self.test_assets = ['visual', 'B04']
        self.test_prefix = 'test_output'
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_parse_bounds_valid(self):
        """Test parsing valid bounding box coordinates."""
        result = parse_bounds(self.test_bounds)
        expected = (407500.0, 7494500.0, 415200.0, 7505700.0)
        self.assertEqual(result, expected)
    
    def test_parse_bounds_invalid_count(self):
        """Test parsing bounds with wrong number of values."""
        invalid_bounds = ['407500.0', '7494500.0', '415200.0']  # Only 3 values
        
        with self.assertRaises(ValueError) as context:
            parse_bounds(invalid_bounds)
        
        self.assertIn("exactly 4 values", str(context.exception))
    
    def test_parse_bounds_invalid_type(self):
        """Test parsing bounds with non-numeric values."""
        invalid_bounds = ['407500.0', 'invalid', '415200.0', '7505700.0']
        
        with self.assertRaises(ValueError) as context:
            parse_bounds(invalid_bounds)
        
        self.assertIn("numeric", str(context.exception))
    
    def test_parse_bounds_mixed_types(self):
        """Test parsing bounds with mixed valid and invalid values."""
        mixed_bounds = ['407500.0', '7494500.0', '415200.0', 'not_a_number']
        
        with self.assertRaises(ValueError) as context:
            parse_bounds(mixed_bounds)
        
        self.assertIn("numeric", str(context.exception))
    
    def test_parse_assets_valid(self):
        """Test parsing valid asset names."""
        result = parse_assets(self.test_assets)
        self.assertEqual(result, self.test_assets)
    
    def test_parse_assets_single(self):
        """Test parsing single asset name."""
        single_asset = ['visual']
        result = parse_assets(single_asset)
        self.assertEqual(result, single_asset)
    
    def test_parse_assets_empty(self):
        """Test parsing empty asset list."""
        empty_assets = []
        result = parse_assets(empty_assets)
        self.assertEqual(result, empty_assets)
    
    def test_parse_assets_special_characters(self):
        """Test parsing asset names with special characters."""
        special_assets = ['visual', 'B04', 'SCL', 'TCI']
        result = parse_assets(special_assets)
        self.assertEqual(result, special_assets)
    
    @patch('sentinel_timelapse.cli.download_images')
    def test_main_success(self, mock_download):
        """Test successful CLI execution."""
        # Mock the download_images function
        mock_download.return_value = {
            'total_images': 2,
            'cloud_filtered': 0,
            'asset_counts': {'visual': 2, 'B04': 2}
        }
        
        # Capture stdout to check output
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            with patch('sys.argv', [
                'sentinel-timelapse',
                '--bounds', '407500.0', '7494500.0', '415200.0', '7505700.0',
                '--assets', 'visual', 'B04',
                '--prefix', self.test_prefix
            ]):
                main()
        
        # Check that download_images was called with correct parameters
        mock_download.assert_called_once()
        call_args = mock_download.call_args[1]  # Keyword arguments
        self.assertEqual(call_args['bounds'], (407500.0, 7494500.0, 415200.0, 7505700.0))
        self.assertEqual(call_args['assets'], ['visual', 'B04'])
        self.assertEqual(call_args['prefix'], self.test_prefix)
        self.assertEqual(call_args['input_crs'], 24879)  # Default value
        self.assertEqual(call_args['start_date'], '2014-08-01')  # Default value
        self.assertEqual(call_args['max_cloud_pct'], 5)  # Default value
        
        # Check output contains expected information
        output = mock_stdout.getvalue()
        self.assertIn("Processing complete!", output)
        self.assertIn("Total images found: 2", output)
        self.assertIn("Images filtered due to clouds: 0", output)
    
    @patch('sentinel_timelapse.cli.download_images')
    def test_main_with_all_parameters(self, mock_download):
        """Test CLI execution with all parameters specified."""
        mock_download.return_value = {
            'total_images': 1,
            'cloud_filtered': 0,
            'asset_counts': {'visual': 1}
        }
        
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            with patch('sys.argv', [
                'sentinel-timelapse',
                '--bounds', '-70.5', '-24.5', '-70.4', '-24.4',
                '--assets', 'visual',
                '--prefix', self.test_prefix,
                '--input-crs', '4326',
                '--start-date', '2023-01-01',
                '--end-date', '2023-01-31',
                '--max-cloud-pct', '10',
                '--verbose'
            ]):
                main()
        
        # Check that download_images was called with all specified parameters
        call_args = mock_download.call_args[1]
        self.assertEqual(call_args['bounds'], (-70.5, -24.5, -70.4, -24.4))
        self.assertEqual(call_args['assets'], ['visual'])
        self.assertEqual(call_args['input_crs'], 4326)
        self.assertEqual(call_args['start_date'], '2023-01-01')
        self.assertEqual(call_args['end_date'], '2023-01-31')
        self.assertEqual(call_args['max_cloud_pct'], 10)
        
        # Check verbose output
        output = mock_stdout.getvalue()
        self.assertIn("Processing bounds:", output)
        self.assertIn("Assets:", output)
        self.assertIn("Input CRS:", output)
    
    @patch('sentinel_timelapse.cli.download_images')
    def test_main_verbose_output(self, mock_download):
        """Test CLI verbose output mode."""
        mock_download.return_value = {
            'total_images': 1,
            'cloud_filtered': 0,
            'asset_counts': {'visual': 1}
        }
        
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            with patch('sys.argv', [
                'sentinel-timelapse',
                '--bounds', '407500.0', '7494500.0', '415200.0', '7505700.0',
                '--assets', 'visual',
                '--prefix', self.test_prefix,
                '-v'
            ]):
                main()
        
        output = mock_stdout.getvalue()
        # Check verbose output contains all parameter information
        self.assertIn("Processing bounds:", output)
        self.assertIn("Assets:", output)
        self.assertIn("Input CRS:", output)
        self.assertIn("Date range:", output)
        self.assertIn("Max cloud coverage:", output)
        self.assertIn("Output prefix:", output)
    
    def test_main_invalid_bounds(self):
        """Test CLI with invalid bounds."""
        with patch('sys.stderr', new=StringIO()) as mock_stderr:
            with patch('sys.argv', [
                'sentinel-timelapse',
                '--bounds', '407500.0', 'invalid', '415200.0', '7505700.0',
                '--assets', 'visual',
                '--prefix', self.test_prefix
            ]):
                with self.assertRaises(SystemExit):
                    main()
        
        error_output = mock_stderr.getvalue()
        self.assertIn("Error:", error_output)
        self.assertIn("numeric", error_output)
    
    def test_main_missing_required_arguments(self):
        """Test CLI with missing required arguments."""
        with patch('sys.stderr', new=StringIO()) as mock_stderr:
            with patch('sys.argv', [
                'sentinel-timelapse',
                '--bounds', '407500.0', '7494500.0', '415200.0', '7505700.0'
                # Missing --assets and --prefix
            ]):
                with self.assertRaises(SystemExit):
                    main()
        
        error_output = mock_stderr.getvalue()
        self.assertIn("error:", error_output.lower())
    
    @patch('sentinel_timelapse.cli.download_images')
    def test_main_keyboard_interrupt(self, mock_download):
        """Test CLI handling of keyboard interrupt."""
        mock_download.side_effect = KeyboardInterrupt()
        
        with patch('sys.stderr', new=StringIO()) as mock_stderr:
            with patch('sys.argv', [
                'sentinel-timelapse',
                '--bounds', '407500.0', '7494500.0', '415200.0', '7505700.0',
                '--assets', 'visual',
                '--prefix', self.test_prefix
            ]):
                with self.assertRaises(SystemExit):
                    main()
        
        error_output = mock_stderr.getvalue()
        self.assertIn("cancelled by user", error_output)
    
    @patch('sentinel_timelapse.cli.download_images')
    def test_main_unexpected_error(self, mock_download):
        """Test CLI handling of unexpected errors."""
        mock_download.side_effect = Exception("Test error")
        
        with patch('sys.stderr', new=StringIO()) as mock_stderr:
            with patch('sys.argv', [
                'sentinel-timelapse',
                '--bounds', '407500.0', '7494500.0', '415200.0', '7505700.0',
                '--assets', 'visual',
                '--prefix', self.test_prefix
            ]):
                with self.assertRaises(SystemExit):
                    main()
        
        error_output = mock_stderr.getvalue()
        self.assertIn("Unexpected error:", error_output)
        self.assertIn("Test error", error_output)
    
    def test_main_string_crs_conversion(self):
        """Test CLI conversion of string CRS to integer."""
        with patch('sentinel_timelapse.cli.download_images') as mock_download:
            mock_download.return_value = {
                'total_images': 1,
                'cloud_filtered': 0,
                'asset_counts': {'visual': 1}
            }
            
            with patch('sys.argv', [
                'sentinel-timelapse',
                '--bounds', '407500.0', '7494500.0', '415200.0', '7505700.0',
                '--assets', 'visual',
                '--prefix', self.test_prefix,
                '--input-crs', '4326'  # String that should be converted to int
            ]):
                main()
            
            call_args = mock_download.call_args[1]
            self.assertEqual(call_args['input_crs'], 4326)  # Should be int, not string
    
    def test_main_non_numeric_string_crs(self):
        """Test CLI with non-numeric string CRS."""
        with patch('sentinel_timelapse.cli.download_images') as mock_download:
            mock_download.return_value = {
                'total_images': 1,
                'cloud_filtered': 0,
                'asset_counts': {'visual': 1}
            }
            
            with patch('sys.argv', [
                'sentinel-timelapse',
                '--bounds', '407500.0', '7494500.0', '415200.0', '7505700.0',
                '--assets', 'visual',
                '--prefix', self.test_prefix,
                '--input-crs', 'EPSG:4326'  # Non-numeric string
            ]):
                main()
            
            call_args = mock_download.call_args[1]
            self.assertEqual(call_args['input_crs'], 'EPSG:4326')  # Should remain string


class TestCLIHelp(unittest.TestCase):
    """Test CLI help functionality."""
    
    def test_cli_help(self):
        """Test that CLI help is displayed correctly."""
        try:
            # Try to run the CLI with --help
            result = subprocess.run([
                sys.executable, '-m', 'sentinel_timelapse.cli', '--help'
            ], capture_output=True, text=True, timeout=10)
            
            # Check that help was displayed
            self.assertIn("Download and process Sentinel-2 imagery", result.stdout)
            self.assertIn("--bounds", result.stdout)
            self.assertIn("--assets", result.stdout)
            self.assertIn("--prefix", result.stdout)
            self.assertIn("Examples:", result.stdout)
            
        except (subprocess.TimeoutExpired, FileNotFoundError, ImportError):
            # Skip test if CLI is not available or times out
            self.skipTest("CLI not available for testing")


if __name__ == '__main__':
    unittest.main()
