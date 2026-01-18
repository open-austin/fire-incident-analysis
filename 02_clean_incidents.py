#!/usr/bin/env python3
"""
Step 2: Clean Incident Data
============================
Loads, cleans, and combines the fire incident datasets.

Usage:
    python scripts/02_clean_incidents.py

Input:
    raw_data/afd_incidents_2022_2024.csv
    raw_data/afd_incidents_2018_2021.csv

Output:
    processed_data/incidents_clean.csv
    outputs/incident_type_summary.csv
"""

import pandas as pd
import os

def load_and_inspect(filepath):
    """Load CSV and print basic info"""
    print(f"\nLoading: {filepath}")
    df = pd.read_csv(filepath, low_memory=False)
    print(f"  Rows: {len(df):,}")
    print(f"  Columns: {df.columns.tolist()}")
    return df


def standardize_columns(df):
    """Standardize column names to lowercase with underscores"""
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
    return df


def parse_location(df):
    """
    Parse location field to extract lat/long.
    Format varies: "(-97.xxx, 30.xxx)" or "(30.xxx, -97.xxx)"
    """
    if 'location' not in df.columns:
        print("  Warning: No 'location' column found")
        return df
    
    # Extract coordinates
    coords = df['location'].str.extract(r'\(([^,]+),\s*([^)]+)\)')
    coords.columns = ['coord1', 'coord2']
    
    # Convert to numeric
    coords['coord1'] = pd.to_numeric(coords['coord1'], errors='coerce')
    coords['coord2'] = pd.to_numeric(coords['coord2'], errors='coerce')
    
    # Determine which is lat vs long based on typical Austin coordinates
    # Austin: lat ~30.2, long ~-97.7
    # If coord1 is negative, it's longitude
    df['longitude'] = coords.apply(
        lambda x: x['coord1'] if x['coord1'] < 0 else x['coord2'], axis=1
    )
    df['latitude'] = coords.apply(
        lambda x: x['coord2'] if x['coord1'] < 0 else x['coord1'], axis=1
    )
    
    # Validate ranges
    valid_lat = (df['latitude'] >= 29) & (df['latitude'] <= 32)
    valid_lon = (df['longitude'] >= -99) & (df['longitude'] <= -96)
    
    df.loc[~(valid_lat & valid_lon), ['latitude', 'longitude']] = None
    
    return df


def classify_incident_type(df):
    """
    Create incident type categories for analysis.
    """
    # Column might be 'problem' or 'Problem' or 'call_type'
    problem_col = None
    for col in ['problem', 'Problem', 'call_type', 'Call_Type']:
        if col in df.columns:
            problem_col = col
            break
    
    if problem_col is None:
        print("  Warning: No problem/call_type column found")
        return df
    
    # Standardize to lowercase for matching
    problem_lower = df[problem_col].str.upper().fillna('')
    
    # Structure fire indicators
    structure_keywords = [
        'STRUCTURE', 'BOX', 'APARTMENT', 'HOUSE', 'RESIDENTIAL', 
        'COMMERCIAL', 'BUILDING', 'HIGHRISE', 'HIGH RISE'
    ]
    df['is_structure_fire'] = problem_lower.str.contains('|'.join(structure_keywords), regex=True)
    
    # Vehicle fire
    df['is_vehicle_fire'] = problem_lower.str.contains('VEHICLE|AUTO|CAR|TRUCK', regex=True)
    
    # Outdoor/vegetation fire
    df['is_outdoor_fire'] = problem_lower.str.contains('GRASS|BRUSH|WILDLAND|OUTSIDE', regex=True)
    
    # Trash/dumpster fire
    df['is_trash_fire'] = problem_lower.str.contains('TRASH|DUMP|RUBBISH', regex=True)
    
    # Create summary category
    def categorize(row):
        if row['is_structure_fire']:
            return 'Structure Fire'
        elif row['is_vehicle_fire']:
            return 'Vehicle Fire'
        elif row['is_outdoor_fire']:
            return 'Outdoor/Vegetation Fire'
        elif row['is_trash_fire']:
            return 'Trash/Dumpster Fire'
        else:
            return 'Other'
    
    df['incident_category'] = df.apply(categorize, axis=1)
    
    return df


def main():
    import os

    print("\n" + "#"*60)
    print("# FIRE RESOURCE ANALYSIS - CLEAN INCIDENT DATA")
    print("#"*60)

    # Load datasets
    df_recent = load_and_inspect("raw_data/afd_incidents_2022_2024.csv")

    # Check if historical data exists
    historical_path = "raw_data/afd_incidents_2018_2021.csv"
    if os.path.exists(historical_path):
        df_historical = load_and_inspect(historical_path)

        # Standardize columns
        df_recent = standardize_columns(df_recent)
        df_historical = standardize_columns(df_historical)

        print("\n" + "-"*40)
        print("Recent data columns:", df_recent.columns.tolist())
        print("Historical data columns:", df_historical.columns.tolist())

        # Find common columns
        common_cols = list(set(df_recent.columns) & set(df_historical.columns))
        print(f"\nCommon columns: {common_cols}")

        # Combine datasets
        print("\nCombining datasets...")
        df = pd.concat([df_recent, df_historical], ignore_index=True)
        print(f"Combined rows: {len(df):,}")
    else:
        print(f"\nWarning: Historical data file not found at {historical_path}")
        print("Proceeding with recent data only (2022-2024)")

        # Standardize columns
        df_recent = standardize_columns(df_recent)

        print("\n" + "-"*40)
        print("Recent data columns:", df_recent.columns.tolist())

        # Use only recent data
        df = df_recent
        print(f"Total rows: {len(df):,}")
    
    # Parse locations
    print("\nParsing locations...")
    df = parse_location(df)
    valid_coords = df['latitude'].notna().sum()
    print(f"  Valid coordinates: {valid_coords:,} ({valid_coords/len(df)*100:.1f}%)")
    
    # Filter to AFD jurisdiction
    jurisdiction_col = None
    for col in ['jurisdiction', 'Jurisdiction']:
        if col in df.columns:
            jurisdiction_col = col
            break
    
    if jurisdiction_col:
        print(f"\nJurisdiction distribution:")
        print(df[jurisdiction_col].value_counts())
        
        # Keep only AFD
        df = df[df[jurisdiction_col].str.upper() == 'AFD']
        print(f"\nFiltered to AFD: {len(df):,} incidents")
    
    # Deduplicate by incident number
    incident_col = None
    for col in ['incident_number', 'Incident_Number', 'masterincidentnumber', 'MasterIncidentNumber']:
        if col in df.columns:
            incident_col = col
            break
    
    if incident_col:
        before = len(df)
        df = df.drop_duplicates(subset=[incident_col], keep='first')
        after = len(df)
        print(f"\nDeduplicated: {before:,} → {after:,} ({before-after:,} duplicates removed)")
    
    # Classify incident types
    print("\nClassifying incident types...")
    df = classify_incident_type(df)
    
    # Summary of incident types
    print("\nIncident Category Distribution:")
    category_counts = df['incident_category'].value_counts()
    print(category_counts)
    
    # Year distribution
    year_col = None
    for col in ['calendaryear', 'CalendarYear', 'calendar_year']:
        if col in df.columns:
            year_col = col
            break
    
    if year_col:
        print(f"\nYear Distribution:")
        print(df[year_col].value_counts().sort_index())
    
    # Response area distribution
    ra_col = None
    for col in ['responsearea', 'ResponseArea', 'response_area']:
        if col in df.columns:
            ra_col = col
            break
    
    if ra_col:
        print(f"\nResponse areas with incidents: {df[ra_col].nunique()}")
    
    # Save cleaned data
    os.makedirs("processed_data", exist_ok=True)
    df.to_csv("processed_data/incidents_clean.csv", index=False)
    print(f"\n✓ Saved: processed_data/incidents_clean.csv")
    
    # Save incident type summary
    os.makedirs("outputs", exist_ok=True)
    
    # Find problem column for detailed summary
    problem_col = None
    for col in df.columns:
        if 'problem' in col.lower():
            problem_col = col
            break
    
    if problem_col:
        type_summary = df[problem_col].value_counts().reset_index()
        type_summary.columns = ['incident_type', 'count']
        type_summary.to_csv("outputs/incident_type_summary.csv", index=False)
        print(f"✓ Saved: outputs/incident_type_summary.csv")
    
    # Summary stats
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total incidents: {len(df):,}")
    print(f"Date range: {df[year_col].min()} - {df[year_col].max()}" if year_col else "")
    print(f"Structure fires: {df['is_structure_fire'].sum():,}")
    print(f"Vehicle fires: {df['is_vehicle_fire'].sum():,}")
    print(f"Outdoor fires: {df['is_outdoor_fire'].sum():,}")
    print(f"Trash fires: {df['is_trash_fire'].sum():,}")
    print(f"Valid coordinates: {valid_coords:,}")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Review outputs/incident_type_summary.csv
   - Do the incident types make sense?
   - Any categories that should be reclassified?

2. Run the next script:
   python scripts/03_create_crosswalk.py
""")


if __name__ == "__main__":
    main()
