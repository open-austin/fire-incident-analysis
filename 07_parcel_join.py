#!/usr/bin/env python3
"""
Step 7: Parcel Spatial Join
============================
Downloads City of Austin Land Database parcel polygons and spatially joins
fire incident points to their containing parcels.

Usage:
    python 07_parcel_join.py

Input:
    processed_data/incidents_clean.csv
    (downloads raw_data/parcels.geojson from ArcGIS if not present)

Output:
    processed_data/incidents_with_parcels.csv
"""

import os
import json
import time
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import warnings

warnings.filterwarnings('ignore')

# City of Austin Land Database - ArcGIS FeatureServer
PARCEL_URL = (
    "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/"
    "2023_Land_Database_Dash_View/FeatureServer/93/query"
)

# Fields to keep from parcels (skip geometry-heavy unused fields)
PARCEL_FIELDS = [
    "PARCEL_ID", "PROP_ID", "LAND_USE", "GENERAL_LAND_USE",
    "PROPERTY_ADDRESS", "IMPRV_TYPE", "BLDG_SQUARE_FOOTAGE",
    "YEAR_BUILT", "UNITS", "ZONING_ZTYPE", "ZONING_BASE",
    "COUNCIL_DISTRICT", "MARKET_VALUE", "APPRAISED_VAL",
    "LAND_ACRES", "FAR"
]

PAGE_SIZE = 2000


def download_parcels(output_path):
    """Download all parcels from ArcGIS with pagination."""
    print("\n" + "=" * 60)
    print("DOWNLOADING PARCEL DATA FROM CITY OF AUSTIN")
    print("=" * 60)

    all_features = []
    offset = 0
    page = 0

    while True:
        page += 1
        params = {
            "where": "1=1",
            "outFields": ",".join(PARCEL_FIELDS),
            "outSR": "4326",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": PAGE_SIZE,
        }

        try:
            resp = requests.get(PARCEL_URL, params=params, timeout=120)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  Page {page} failed: {e}")
            print("  Retrying in 5 seconds...")
            time.sleep(5)
            continue

        features = data.get("features", [])
        if not features:
            break

        all_features.extend(features)
        offset += len(features)
        print(f"  Page {page}: got {len(features)} parcels (total: {len(all_features):,})")

        # ArcGIS signals no more data when fewer than requested are returned
        if len(features) < PAGE_SIZE:
            break

        # Brief pause to be polite to the server
        time.sleep(0.5)

    print(f"\n  Total parcels downloaded: {len(all_features):,}")

    # Save as GeoJSON
    geojson = {"type": "FeatureCollection", "features": all_features}
    with open(output_path, "w") as f:
        json.dump(geojson, f)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  Saved to {output_path} ({size_mb:.1f} MB)")

    return geojson


def load_parcels(filepath):
    """Load parcel polygons into GeoDataFrame."""
    print(f"\nLoading parcels from {filepath}...")
    parcels = gpd.read_file(filepath)
    print(f"  Loaded {len(parcels):,} parcels")
    print(f"  CRS: {parcels.crs}")

    # Ensure WGS84
    if parcels.crs is None:
        parcels = parcels.set_crs("EPSG:4326")
    elif parcels.crs.to_epsg() != 4326:
        parcels = parcels.to_crs("EPSG:4326")

    # Drop parcels with null geometry
    before = len(parcels)
    parcels = parcels[parcels.geometry.notnull()].copy()
    if len(parcels) < before:
        print(f"  Dropped {before - len(parcels)} parcels with null geometry")

    return parcels


def load_incidents(filepath):
    """Load incident data and create point geometries."""
    print(f"\nLoading incidents from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"  Loaded {len(df):,} incidents")

    # Drop rows without coordinates
    before = len(df)
    df = df.dropna(subset=["latitude", "longitude"]).copy()
    if len(df) < before:
        print(f"  Dropped {before - len(df)} incidents without coordinates")

    # Create GeoDataFrame with point geometries
    geometry = [Point(lon, lat) for lon, lat in zip(df["longitude"], df["latitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    print(f"  Created {len(gdf):,} incident points")

    return gdf


def spatial_join(incidents, parcels, max_distance_ft=200):
    """Join incidents to parcels via point-in-polygon, with nearest-parcel fallback.

    Incident coordinates often land on roads/sidewalks rather than inside
    the parcel polygon, so unmatched points are snapped to the nearest
    parcel within max_distance_ft (default 200 ft).
    """
    print("\nPerforming spatial join (point-in-polygon)...")
    print("  This may take a minute with ~230k parcels...")

    parcel_cols = [c for c in parcels.columns if c != "geometry"]

    # --- Phase 1: exact point-in-polygon ---
    joined = gpd.sjoin(incidents, parcels, how="left", predicate="within")
    if "index_right" in joined.columns:
        joined = joined.drop(columns=["index_right"])

    matched_mask = joined["PARCEL_ID"].notna()
    n_exact = matched_mask.sum()
    print(f"  Exact match: {n_exact:,} / {len(joined):,}")

    # --- Phase 2: nearest-parcel fallback for unmatched ---
    unmatched = joined[~matched_mask].copy()
    if len(unmatched) > 0:
        print(f"  Running nearest-parcel fallback for {len(unmatched):,} unmatched points "
              f"(within {max_distance_ft} ft)...")

        # Project to State Plane TX Central (feet) for distance calculation
        parcels_proj = parcels.to_crs("EPSG:2277")
        unmatched_proj = unmatched[["geometry"]].to_crs("EPSG:2277")

        nearest = gpd.sjoin_nearest(
            unmatched_proj, parcels_proj,
            how="left", max_distance=max_distance_ft, distance_col="_dist_ft"
        )

        # De-duplicate: if a point is near multiple parcels, keep closest
        nearest = nearest.loc[~nearest.index.duplicated(keep="first")]

        # Merge parcel attributes back onto unmatched rows
        for col in parcel_cols:
            joined.loc[nearest.index, col] = nearest["index_right"].map(
                parcels.set_index(parcels.index)[col]
            ).values

        n_nearest = joined.loc[unmatched.index, "PARCEL_ID"].notna().sum()
        print(f"  Nearest match: {n_nearest:,} additional")

    total_matched = joined["PARCEL_ID"].notna().sum()
    print(f"  Total matched: {total_matched:,} / {len(joined):,} ({total_matched/len(joined)*100:.1f}%)")

    return joined


def main():
    print("\n" + "#" * 60)
    print("# STEP 7: PARCEL SPATIAL JOIN")
    print("#" * 60)

    parcel_path = "raw_data/parcels.geojson"
    incident_path = "processed_data/incidents_clean.csv"
    output_path = "processed_data/incidents_with_parcels.csv"

    # 1. Download parcels if needed
    if not os.path.isfile(parcel_path):
        download_parcels(parcel_path)
    else:
        print(f"\nParcel file already exists: {parcel_path}")

    # 2. Load data
    parcels = load_parcels(parcel_path)
    incidents = load_incidents(incident_path)

    # 3. Spatial join
    result = spatial_join(incidents, parcels)

    # 4. Save (drop geometry column for CSV output)
    print(f"\nSaving to {output_path}...")
    result_df = pd.DataFrame(result.drop(columns=["geometry"]))
    result_df.to_csv(output_path, index=False)
    print(f"  Saved {len(result_df):,} rows with {len(result_df.columns)} columns")

    # 5. Quick summary
    print("\n" + "=" * 60)
    print("PARCEL JOIN SUMMARY")
    print("=" * 60)

    if "IMPRV_TYPE" in result_df.columns:
        print("\nTop improvement types for matched incidents:")
        print(result_df["IMPRV_TYPE"].value_counts().head(10).to_string())

    if "LAND_USE" in result_df.columns:
        print("\nLand use code distribution:")
        print(result_df["LAND_USE"].value_counts().head(10).to_string())

    if "YEAR_BUILT" in result_df.columns:
        valid_years = result_df["YEAR_BUILT"].dropna()
        if len(valid_years) > 0:
            print(f"\nYear built range: {valid_years.min():.0f} - {valid_years.max():.0f}")
            print(f"Median year built: {valid_years.median():.0f}")

    print("\nDone! Output: " + output_path)


if __name__ == "__main__":
    main()
