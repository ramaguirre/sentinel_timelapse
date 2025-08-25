from setuptools import setup, find_packages

setup(
    name="sentinel_timelapse",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "planetary-computer",
        "pystac-client",
        "rasterio",
        "geopandas",
        "shapely",
        "tqdm"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for processing Sentinel-2 time series",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
)