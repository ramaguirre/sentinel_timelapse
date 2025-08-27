from setuptools import setup, find_packages

setup(
    name="sentinel_timelapse",
    version="0.1.6",
    packages=find_packages(),
    install_requires=[
        "planetary-computer",
        "pystac-client",
        "rasterio",
        "geopandas",
        "numpy",
        "pyproj",
        "pandas"
    ],
    author="Ramón Aguirre M.",
    author_email="ramaguirre@hotmail.com",
    description="Download and process Sentinel-2 imagery from Planetary Computer",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sentinel_timelapse",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)