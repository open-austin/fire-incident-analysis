#!/usr/bin/env python3
"""
Create GeoJSON: Census Tracts with Incident Data
=================================================
Merges census tract shapefile with tract summary incident data.

Usage:
    python create_tract_geojson.py

Input:
    raw_data/tl_2023_48_tract.shp
    outputs/census_tract_incidents.csv

Output:
    processed_data/census_tracts_with_incidents.geojson
"""
import geopandas as gpd
import pandas as pd

from census_variables import AUSTIN_COUNTIES


def create_tract_geojson():
    """Create GeoJSON file combining census tract shapes with incident data."""
    print("\nCreating census tract GeoJSON with incident data...")
    
    # Load census tract shapefile
    print("  Loading census tract shapefile...")
    tracts_shp = gpd.read_file("raw_data/tl_2023_48_tract.shp")
    
    # Filter to Austin counties only
    tracts_shp = tracts_shp[tracts_shp['COUNTYFP'].isin(AUSTIN_COUNTIES.values())]
    tracts_shp.rename(columns={'TRACTCE': 'tract_code'}, inplace=True)
    print(f"    Austin tracts in shapefile: {len(tracts_shp)}")
    
    
    # Check sample formats
    print(f"    Sample shapefile tract codes: {tracts_shp['tract_code'].head(3).tolist()}")

    # Select relevant columns from shapefile to keep
    # Keep geometry and key identifying columns
    cols_to_keep = ['tract_code', 'GEOID', 'NAME', 'NAMELSAD', 'ALAND', 'geometry']
    cols_available = [c for c in cols_to_keep if c in tracts_shp.columns]
    tracts_shp = tracts_shp[cols_available]
    
    # Save as GeoJSON
    output_path = "processed_data/census_tracts_with_incidents.geojson"
    print(f"\n  Saving to {output_path}...")
    tracts_shp.to_file(output_path, driver="GeoJSON")
    
    print(f"\n✓ Saved: {output_path}")
    print(f"  Total tracts: {len(tracts_shp)}")
    
    return tracts_shp


if __name__ == "__main__":
    create_tract_geojson()