# Release Checklist for PyPI

## Pre-Release Tasks

### 1. Update Version
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `CHANGELOG.md`
- [ ] Update version in `sentinel_timelapse/__init__.py` if needed

### 2. Update Documentation
- [ ] Update README.md if needed
- [ ] Update any docstrings
- [ ] Check that all examples work

### 3. Test Everything
- [ ] Run all tests: `pytest tests/ -v`
- [ ] Run linting: `flake8 sentinel_timelapse tests`
- [ ] Run type checking: `mypy sentinel_timelapse`
- [ ] Test CLI: `python -m sentinel_timelapse.cli --help`
- [ ] Test installation: `pip install -e .`

### 4. Build and Test Package
- [ ] Clean previous builds: `rm -rf dist/ build/ *.egg-info/`
- [ ] Build package: `python -m build`
- [ ] Check package: `twine check dist/*`
- [ ] Test upload to TestPyPI: `twine upload --repository testpypi dist/*`

## Release Tasks

### 1. Create GitHub Release
- [ ] Create a new release on GitHub
- [ ] Tag with version (e.g., `v0.1.0`)
- [ ] Add release notes
- [ ] Publish the release

### 2. PyPI Upload
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Verify package appears on PyPI
- [ ] Test installation: `pip install sentinel-timelapse`

### 3. Post-Release Tasks
- [ ] Update any documentation that references the version
- [ ] Announce the release (if applicable)
- [ ] Monitor for any issues

## Manual Release Commands

```bash
# Clean and build
rm -rf dist/ build/ *.egg-info/
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (for release)
twine upload dist/*

# Test installation
pip install sentinel-timelapse
```

## Automated Release (Recommended)

1. Update version in `pyproject.toml`
2. Commit and push changes
3. Create a GitHub release
4. The GitHub Action will automatically build and upload to PyPI

## Troubleshooting

### Common Issues
- **Package name conflict**: Check if `sentinel-timelapse` is available on PyPI
- **Build errors**: Ensure all dependencies are correctly specified
- **Upload errors**: Check PyPI credentials and package format

### PyPI Account Setup
1. Create account on https://pypi.org/
2. Create API token
3. Add token to GitHub secrets as `PYPI_API_TOKEN`
