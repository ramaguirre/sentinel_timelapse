# Sentinel Timelapse Test Suite

This directory contains comprehensive unit tests and integration tests for the `sentinel_timelapse` package.

## Test Structure

### Unit Tests

- **`test_geometry.py`** - Tests for the geometry module
  - CRS conversion functionality
  - Bounding box transformations
  - Output format validation
  - Error handling for invalid inputs

- **`test_stac.py`** - Tests for the STAC module
  - STAC item search functionality
  - Geometry-based filtering
  - Connection error handling
  - Empty result handling

- **`test_processing.py`** - Tests for the processing module
  - Asset clipping functionality
  - TIFF file saving
  - CRS transformations
  - Error handling for missing assets
  - Bounds validation

- **`test_main.py`** - Tests for the main module
  - Complete download workflow
  - Cloud filtering
  - Asset processing
  - Directory creation
  - Statistics generation

- **`test_bootstrap_geo.py`** - Tests for the bootstrap module
  - Rasterio bundled data configuration
  - Environment variable management
  - CRS validation
  - Error handling

### Integration Tests

- **`test_integration.py`** - End-to-end workflow tests
  - Complete pipeline from bounds to output
  - Cloud filtering integration
  - Different CRS handling
  - Error scenarios
  - Empty result handling

### Test Utilities

- **`conftest.py`** - Pytest configuration and common fixtures
- **`run_tests.py`** - Test runner script
- **`test_usage.py`** - Original usage example (legacy)

## Running Tests

### Using the Test Runner

```bash
# Run all tests
python tests/run_tests.py

# Run specific module tests
python tests/run_tests.py geometry
python tests/run_tests.py stac
python tests/run_tests.py processing
python tests/run_tests.py main
python tests/run_tests.py integration
python tests/run_tests.py bootstrap
```

### Using Pytest

```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/test_geometry.py
pytest tests/test_stac.py
pytest tests/test_processing.py
pytest tests/test_main.py
pytest tests/test_integration.py
pytest tests/test_bootstrap_geo.py

# Run with markers
pytest -m unit
pytest -m integration
pytest -m geometry
pytest -m stac
pytest -m processing
pytest -m main
pytest -m bootstrap

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=sentinel_timelapse
```

### Using unittest

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_geometry
python -m unittest tests.test_stac
python -m unittest tests.test_processing
python -m unittest tests.test_main
python -m unittest tests.test_integration
python -m unittest tests.test_bootstrap_geo
```

## Test Coverage

The test suite covers:

### Functionality Testing
- ✅ CRS conversion and validation
- ✅ STAC item search and filtering
- ✅ Asset clipping and processing
- ✅ Cloud coverage filtering
- ✅ File output and directory creation
- ✅ Error handling and edge cases

### Input Validation
- ✅ Invalid CRS codes
- ✅ Missing assets
- ✅ Out-of-bounds coordinates
- ✅ Invalid date ranges
- ✅ Empty search results

### Integration Scenarios
- ✅ Complete workflow from bounds to output
- ✅ Multiple asset processing
- ✅ Cloud filtering integration
- ✅ Different coordinate systems
- ✅ Error recovery

## Mocking Strategy

The tests use extensive mocking to avoid:
- Network calls to STAC servers
- File system operations
- External dependencies

### Key Mocked Components
- `pystac_client.Client` - STAC API calls
- `planetary_computer.sign` - Asset signing
- `rasterio.open` - Raster file operations
- File system operations
- Environment variables

## Test Data

### Sample Bounds
- **UTM Zone 19S (EPSG:24879)**: `(407500.0, 7494500.0, 415200.0, 7505700.0)`
- **WGS84**: `(-70.5, -24.5, -70.4, -24.4)`

### Sample Assets
- `visual` - RGB composite
- `B04` - Red band
- `SCL` - Scene Classification Layer

### Sample Date Ranges
- Start: `2023-01-01`
- End: `2023-01-31`

## Continuous Integration

The test suite is designed to run in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    python -m pip install pytest pytest-cov
    pytest --cov=sentinel_timelapse --cov-report=xml
```

## Adding New Tests

When adding new functionality:

1. **Create unit tests** for individual functions
2. **Add integration tests** for complete workflows
3. **Update fixtures** in `conftest.py` if needed
4. **Add appropriate markers** for test categorization
5. **Ensure proper mocking** to avoid external dependencies

### Test Naming Convention
- Test classes: `Test<ModuleName>`
- Test methods: `test_<functionality>_<scenario>`

### Example Test Structure
```python
class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_new_feature_success(self):
        """Test successful execution of new feature."""
        pass
    
    def test_new_feature_error_handling(self):
        """Test error handling in new feature."""
        pass
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the parent directory is in the Python path
2. **Mock Issues**: Check that all external dependencies are properly mocked
3. **File System Errors**: Use temporary directories for file operations
4. **Network Errors**: Ensure all network calls are mocked

### Debug Mode

Run tests with increased verbosity:
```bash
pytest -v -s --tb=long
```

### Test Isolation

Each test should be independent and not rely on the state of other tests. Use `setUp()` and `tearDown()` methods for proper cleanup.
