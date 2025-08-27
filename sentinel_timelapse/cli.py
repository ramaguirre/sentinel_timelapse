#!/usr/bin/env python3
"""
Command line interface for sentinel-timelapse.

This module provides a command-line interface for the sentinel-timelapse package,
allowing users to download and process Sentinel-2 imagery directly from the
command line without writing Python code.
"""

import argparse
import sys
from datetime import datetime
from typing import List, Union

from .main import download_images


def parse_bounds(bounds_str: List[str]) -> tuple:
    """
    Parse bounding box coordinates from command line arguments.

    This function validates and converts the bounding box coordinates provided
    as command line arguments into a tuple of floating-point numbers.

    Args:
        bounds_str: List of 4 string values representing xmin, ymin, xmax, ymax

    Returns:
        tuple: Tuple of 4 float values (xmin, ymin, xmax, ymax)

    Raises:
        ValueError: If the number of arguments is not exactly 4, or if any
                   value cannot be converted to a float

    Example:
        >>> parse_bounds(['407500.0', '7494500.0', '415200.0', '7505700.0'])
        (407500.0, 7494500.0, 415200.0, 7505700.0)
    """
    if len(bounds_str) != 4:
        raise ValueError("Bounds must be exactly 4 values: xmin ymin xmax ymax")

    try:
        return tuple(float(x) for x in bounds_str)
    except ValueError:
        raise ValueError("All bounds values must be numeric")


def parse_assets(assets_str: List[str]) -> List[str]:
    """
    Parse asset names from command line arguments.

    This function validates the asset names provided as command line arguments.
    Currently, it simply returns the input list as-is, but could be extended
    to validate against a list of known Sentinel-2 assets.

    Args:
        assets_str: List of asset names to download (e.g., ['visual', 'B04'])

    Returns:
        List[str]: List of validated asset names

    Example:
        >>> parse_assets(['visual', 'B04', 'SCL'])
        ['visual', 'B04', 'SCL']
    """
    return assets_str


def main():
    """
    Main command-line interface function.
    
    This function sets up the argument parser, processes command line arguments,
    and orchestrates the Sentinel-2 image download process. It provides a
    user-friendly interface for the sentinel-timelapse functionality.
    
    The function handles:
    - Command line argument parsing and validation
    - Coordinate system and bounds processing
    - Asset specification and validation
    - Date range processing
    - Cloud coverage filtering configuration
    - Error handling and user feedback
    
    Returns:
        None
    
    Raises:
        SystemExit: On argument parsing errors, user cancellation, or processing errors
    
    Example:
        $ sentinel-timelapse --bounds 407500 7494500 415200 7505700 \\
        >                      --assets visual B04 \\
        >                      --prefix mining_area \\
        >                      --start-date 2023-01-01 \\
        >                      --end-date 2023-01-31 \\
        >                      --max-cloud-pct 10
    """
    # Set up the argument parser with detailed help and examples
    parser = argparse.ArgumentParser(
        description="Download and process Sentinel-2 imagery for timelapse creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download visual and B04 bands for a mining area
  sentinel-timelapse --bounds 407500.0 7494500.0 415200.0 7505700.0 \\
                     --assets visual B04 \\
                     --prefix mining_area \\
                     --start-date 2023-12-01 \\
                     --end-date 2023-12-31 \\
                     --max-cloud-pct 5

  # Download with WGS84 coordinates
  sentinel-timelapse --bounds -70.5 -24.5 -70.4 -24.4 \\
                     --assets visual \\
                     --prefix coastal_area \\
                     --input-crs 4326 \\
                     --start-date 2023-01-01 \\
                     --end-date 2023-01-31
        """,
    )

    # Define command line arguments with detailed help text
    parser.add_argument(
        "--bounds",
        nargs=4,
        type=str,
        required=True,
        help="Bounding box coordinates: xmin ymin xmax ymax",
    )

    parser.add_argument(
        "--assets",
        nargs="+",
        type=str,
        required=True,
        help="Asset names to download (e.g., visual B04 SCL)",
    )

    parser.add_argument(
        "--prefix", type=str, required=True, help="Output directory prefix"
    )

    parser.add_argument(
        "--input-crs",
        type=str,
        default="24879",
        help="Input CRS (EPSG code or string, default: 24879)",
    )

    parser.add_argument(
        "--start-date",
        type=str,
        default="2014-08-01",
        help="Start date in YYYY-MM-DD format (default: 2014-08-01)",
    )

    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="End date in YYYY-MM-DD format (default: today)",
    )

    parser.add_argument(
        "--max-cloud-pct",
        type=int,
        default=5,
        help="Maximum cloud coverage percentage (default: 5)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    # Parse command line arguments
    args = parser.parse_args()

    try:
        # Parse and validate bounding box coordinates
        bounds = parse_bounds(args.bounds)

        # Parse and validate asset names
        assets = parse_assets(args.assets)

        # Parse and convert coordinate reference system
        input_crs = args.input_crs
        if isinstance(input_crs, str) and input_crs.isdigit():
            input_crs = int(input_crs)

        # Display processing parameters if verbose mode is enabled
        if args.verbose:
            print(f"Processing bounds: {bounds}")
            print(f"Assets: {assets}")
            print(f"Input CRS: {input_crs}")
            print(f"Date range: {args.start_date} to {args.end_date or 'today'}")
            print(f"Max cloud coverage: {args.max_cloud_pct}%")
            print(f"Output prefix: {args.prefix}")
            print()

        # Execute the main image download and processing workflow
        stats = download_images(
            bounds=bounds,
            assets=assets,
            prefix=args.prefix,
            input_crs=input_crs,
            start_date=args.start_date,
            end_date=args.end_date,
            max_cloud_pct=args.max_cloud_pct,
        )

        # Display processing results and statistics
        print(f"\nProcessing complete!")
        print(f"Total images found: {stats['total_images']}")
        print(f"Images filtered due to clouds: {stats['cloud_filtered']}")
        print(f"Images processed per asset: {stats['asset_counts']}")

    except ValueError as e:
        # Handle validation errors (invalid bounds, CRS, etc.)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        # Handle user cancellation (Ctrl+C)
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
