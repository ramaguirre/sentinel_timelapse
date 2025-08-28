# Conda Publishing Guide for sentinel-timelapse

## What We've Accomplished

✅ **Conda Recipe Created**: `conda-recipe/meta.yaml` with proper dependencies
✅ **Local Build Successful**: Package builds and installs correctly
✅ **CLI Working**: Command-line interface functions properly
✅ **GitHub Actions**: CI/CD workflow for conda builds
✅ **Documentation Updated**: README includes conda installation instructions

## Current Status

Your package is ready for conda-forge publication! Here's what you have:

### Files Created:
- `conda-recipe/meta.yaml` - Main conda recipe
- `conda-recipe/post-link.sh` - Script to install pip dependencies
- `conda-recipe/README.md` - Build instructions
- `.github/workflows/conda-build.yml` - CI/CD for conda builds
- `README.md` - Updated with conda installation instructions

### Package Information:
- **Name**: sentinel-timelapse
- **Version**: 0.1.0
- **License**: MIT
- **Python**: >=3.8
- **Platform**: All (noarch: python)

## Next Steps to Publish on conda-forge

### 1. Prepare Your Recipe for conda-forge

First, update the recipe with your actual GitHub information:

```yaml
# In conda-recipe/meta.yaml, update these lines:
about:
  home: https://github.com/ramaguirre/sentinel_timelapse  # Your actual repo
  dev_url: https://github.com/ramaguirre/sentinel_timelapse

extra:
  recipe-maintainers:
    - ramaguirre  # Your GitHub username
```

### 2. Submit to conda-forge/staged-recipes

1. **Fork the staged-recipes repository**:
   - Go to https://github.com/conda-forge/staged-recipes
   - Click "Fork" to create your own copy

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/staged-recipes.git
   cd staged-recipes
   ```

3. **Add your recipe**:
   ```bash
   mkdir -p recipes/sentinel-timelapse
   cp -r /path/to/your/sentinel_timelapse/conda-recipe/* recipes/sentinel-timelapse/
   ```

4. **Commit and push**:
   ```bash
   git add recipes/sentinel-timelapse/
   git commit -m "Add sentinel-timelapse recipe"
   git push origin main
   ```

5. **Create a Pull Request**:
   - Go to your fork on GitHub
   - Click "Compare & pull request"
   - Fill in the PR description with:
     - Package description
     - Link to your repository
     - Any special notes about dependencies

### 3. What Happens After PR Approval

Once your PR is merged:
1. conda-forge will create a new repository: `conda-forge/sentinel-timelapse-feedstock`
2. The package will be automatically built and published
3. Users can install with: `conda install -c conda-forge sentinel-timelapse`

### 4. Future Updates

For version updates:
1. Fork the `conda-forge/sentinel-timelapse-feedstock` repository
2. Update the version in `recipe/meta.yaml`
3. Submit a PR to the feedstock repository

## Testing Your Package

### Local Testing (Already Done)
```bash
# Build locally
conda build conda-recipe/

# Test installation
conda install --use-local sentinel-timelapse

# Test functionality
sentinel-timelapse --help
```

### Production Testing
Once published on conda-forge:
```bash
# Install from conda-forge
conda install -c conda-forge sentinel-timelapse

# Test functionality
sentinel-timelapse --help
python -c "import sentinel_timelapse; print('Success!')"
```

## Dependencies Strategy

Your package uses a hybrid approach:
- **Conda dependencies**: geopandas, shapely, rasterio, pyproj, numpy, requests
- **Pip dependencies**: pystac-client, planetary-computer (installed during testing)

This ensures maximum compatibility while handling packages not available in conda-forge. The pip dependencies are installed during the test phase to verify functionality.

## Troubleshooting

### Common Issues:
1. **Missing dependencies**: Ensure all conda dependencies are available in conda-forge
2. **Build failures**: Check the conda-forge CI logs for specific errors
3. **Import errors**: Test the package thoroughly before submitting

### Getting Help:
- conda-forge documentation: https://conda-forge.org/docs/
- conda-forge GitHub discussions: https://github.com/conda-forge/conda-forge.github.io/discussions

## Timeline

- **PR submission**: 1-2 days
- **Review process**: 1-3 days (depending on maintainer availability)
- **Build and publication**: 1-2 days after approval
- **Total time**: 3-7 days

## Success Metrics

Your package will be successfully published when:
- ✅ PR is merged to conda-forge/staged-recipes
- ✅ Feedstock repository is created
- ✅ Package builds successfully on all platforms
- ✅ Users can install with `conda install -c conda-forge sentinel-timelapse`

## Final Notes

Your package is well-prepared for conda-forge publication! The recipe follows best practices and includes all necessary components. The hybrid conda/pip dependency approach ensures broad compatibility while maintaining the functionality of your geospatial package.

Good luck with the publication process!
