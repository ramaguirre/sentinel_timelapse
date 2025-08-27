#!/usr/bin/env python3
"""
Test runner for sentinel_timelapse package.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py geometry           # Run only geometry tests
    python run_tests.py stac               # Run only STAC tests
    python run_tests.py processing         # Run only processing tests
    python run_tests.py main               # Run only main tests
    python run_tests.py integration        # Run only integration tests
    python run_tests.py bootstrap          # Run only bootstrap tests
"""

import sys
import unittest
import os

# Add parent directory to path to import sentinel_timelapse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Run all test modules."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_tests(module_name):
    """Run tests for a specific module."""
    test_modules = {
        'geometry': 'tests.test_geometry',
        'stac': 'tests.test_stac',
        'processing': 'tests.test_processing',
        'main': 'tests.test_main',
        'integration': 'tests.test_integration',
        'bootstrap': 'tests.test_bootstrap_geo'
    }
    
    if module_name not in test_modules:
        print(f"Unknown module: {module_name}")
        print(f"Available modules: {', '.join(test_modules.keys())}")
        return False
    
    # Import and run specific test module
    try:
        module = __import__(test_modules[module_name], fromlist=['*'])
        suite = unittest.TestLoader().loadTestsFromModule(module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Error importing test module: {e}")
        return False


def main():
    """Main function to run tests."""
    if len(sys.argv) > 1:
        module_name = sys.argv[1].lower()
        success = run_specific_tests(module_name)
    else:
        print("Running all tests...")
        success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
