#!/usr/bin/env python3
"""
Run All Workflows - Austin Fire Resource Allocation Analysis

This script runs the complete analysis pipeline for new users.
It handles dependency checking, data downloading, and all analysis steps.

Usage:
    python run_all.py           # Run full pipeline
    python run_all.py --skip-download  # Skip data download (if already downloaded)
    python run_all.py --check-only     # Only check dependencies, don't run
"""

import subprocess
import sys
import os
import argparse
import zipfile
from pathlib import Path


# Pipeline steps in execution order
PIPELINE_STEPS = [
    ("01_download_data.py", "Downloading data from public APIs"),
    ("02_clean_incidents.py", "Cleaning incident data"),
    ("03_create_crosswalk.py", "Creating census tract to response area crosswalk"),
    ("04_analysis.py", "Running statistical analysis"),
    ("05_visualize.py", "Generating maps and visualizations"),
]

OPTIONAL_STEPS = [
    ("06_nfirs_cause_analysis.py", "NFIRS cause analysis (requires manual data download)"),
]

REQUIRED_PACKAGES = [
    "pandas",
    "geopandas",
    "requests",
    "shapely",
    "folium",
    "matplotlib",
    "seaborn",
    "scipy",
    "numpy",
]


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_step(step_num: int, total: int, text: str) -> None:
    """Print a step indicator."""
    print(f"\n[{step_num}/{total}] {text}")
    print("-" * 50)


def check_python_version() -> bool:
    """Check if Python version is 3.8+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"ERROR: Python 3.8+ required. You have {version.major}.{version.minor}")
        return False
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies() -> tuple[bool, list[str]]:
    """Check if all required packages are installed."""
    missing = []
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    return len(missing) == 0, missing


def install_dependencies() -> bool:
    """Install dependencies from requirements.txt."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("ERROR: requirements.txt not found")
        return False

    print("Installing dependencies from requirements.txt...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"ERROR: Failed to install dependencies")
        print(result.stderr)
        return False

    print("Dependencies installed successfully")
    return True


def unzip_tract_data() -> bool:
    """Unzip the census tract shapefile if needed."""
    raw_data_dir = Path(__file__).parent / "raw_data"
    zip_file = raw_data_dir / "tl_2023_48_tract.zip"
    extract_dir = raw_data_dir / "tl_2023_48_tract"

    if not zip_file.exists():
        # Will be downloaded in the download step
        return True

    if extract_dir.exists() and any(extract_dir.glob("*.shp")):
        print("Census tract shapefiles already extracted")
        return True

    print("Extracting census tract shapefiles...")
    try:
        extract_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(zip_file, 'r') as zf:
            zf.extractall(extract_dir)
        print("Extraction complete")
        return True
    except Exception as e:
        print(f"ERROR: Failed to extract tract data: {e}")
        return False


def run_script(script_name: str, description: str) -> bool:
    """Run a Python script and return success status."""
    script_path = Path(__file__).parent / script_name

    if not script_path.exists():
        print(f"ERROR: Script not found: {script_name}")
        return False

    print(f"Running {script_name}...")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=Path(__file__).parent
    )

    if result.returncode != 0:
        print(f"ERROR: {script_name} failed with exit code {result.returncode}")
        return False

    print(f"Completed: {description}")
    return True


def check_data_exists() -> bool:
    """Check if raw data has already been downloaded."""
    raw_data_dir = Path(__file__).parent / "raw_data"
    required_files = [
        "afd_incidents_2022_2024.csv",
        "afd_response_areas.geojson",
        "fire_stations.geojson",
        "census_population.csv",
        "census_housing.csv",
    ]

    if not raw_data_dir.exists():
        return False

    for f in required_files:
        if not (raw_data_dir / f).exists():
            return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Run the complete Austin Fire Resource Allocation Analysis pipeline"
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip data download step (use if data already downloaded)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check dependencies, don't run the pipeline"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Automatically install missing dependencies"
    )
    args = parser.parse_args()

    print_header("Austin Fire Resource Allocation Analysis")
    print("Complete Pipeline Runner")
    print("Research Hub - Austin Housing & Land Use Working Group")

    # Step 1: Check Python version
    print_step(1, 4, "Checking Python version")
    if not check_python_version():
        sys.exit(1)

    # Step 2: Check dependencies
    print_step(2, 4, "Checking dependencies")
    deps_ok, missing = check_dependencies()

    if not deps_ok:
        print(f"Missing packages: {', '.join(missing)}")
        if args.install_deps:
            if not install_dependencies():
                sys.exit(1)
            # Re-check after install
            deps_ok, missing = check_dependencies()
            if not deps_ok:
                print(f"ERROR: Still missing packages after install: {', '.join(missing)}")
                sys.exit(1)
        else:
            print("\nTo install dependencies, run one of:")
            print("  pip install -r requirements.txt")
            print("  python run_all.py --install-deps")
            sys.exit(1)
    else:
        print("All required packages are installed")

    if args.check_only:
        print("\n--check-only specified. Exiting after dependency check.")
        print("All checks passed!")
        sys.exit(0)

    # Step 3: Check/download data
    print_step(3, 4, "Checking data availability")

    if args.skip_download:
        if check_data_exists():
            print("--skip-download specified and data exists. Skipping download.")
        else:
            print("WARNING: --skip-download specified but data is missing!")
            print("Run without --skip-download to download data.")
            sys.exit(1)
    else:
        print("Data will be downloaded from public APIs (~100MB)")

    # Step 4: Run pipeline
    print_step(4, 4, "Running analysis pipeline")

    steps_to_run = PIPELINE_STEPS.copy()
    if args.skip_download:
        steps_to_run = steps_to_run[1:]  # Skip download step

    total_steps = len(steps_to_run)
    for i, (script, description) in enumerate(steps_to_run, 1):
        print(f"\n--- Pipeline Step {i}/{total_steps}: {description} ---")
        if not run_script(script, description):
            print(f"\nERROR: Pipeline failed at step {i}")
            sys.exit(1)

        # Unzip tract data after download step
        if script == "01_download_data.py":
            if not unzip_tract_data():
                print("ERROR: Failed to extract census tract data")
                sys.exit(1)

    # Success!
    print_header("Pipeline Complete!")

    print("Generated outputs in the 'outputs/' directory:")
    outputs_dir = Path(__file__).parent / "outputs"
    if outputs_dir.exists():
        print("\nMaps (open in browser):")
        for f in sorted(outputs_dir.glob("*.html")):
            print(f"  - {f.name}")

        print("\nCharts:")
        for f in sorted(outputs_dir.glob("*.png")):
            print(f"  - {f.name}")

        print("\nData tables:")
        for f in sorted(outputs_dir.glob("*.csv")):
            print(f"  - {f.name}")

        print("\nStatistical results:")
        for f in sorted(outputs_dir.glob("*.txt")):
            print(f"  - {f.name}")

    print("\n" + "=" * 60)
    print("  Next steps:")
    print("  1. Open outputs/map_incidents_per_capita.html in a browser")
    print("  2. Review outputs/summary_by_urban_class.csv for main findings")
    print("  3. Check outputs/statistical_tests.txt for significance testing")
    print("=" * 60)


if __name__ == "__main__":
    main()
