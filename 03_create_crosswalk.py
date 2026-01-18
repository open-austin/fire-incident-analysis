#!/usr/bin/env python3
"""
Step 3: Create Spatial Crosswalk
=================================
Creates a crosswalk between census tracts and AFD response areas,
then allocates census demographics to response areas.

Usage:
    python scripts/03_create_crosswalk.py

Input:
    raw_data/afd_response_areas.geojson
    raw_data/travis_county_tracts.shp (or .geojson)
    raw_data/census_population.csv
    raw_data/census_housing.csv
    raw_data/census_year_built.csv

Output:
    processed_data/tract_to_response_area_crosswalk.csv
    processed_data/response_area_demographics.csv
    processed_data/response_areas_with_demographics.geojson
"""

import pandas as pd
import geopandas as gpd
import os
import warnings
warnings.filterwarnings('ignore')

def load_response_areas():
    """Load AFD response area boundaries"""
    print("\nLoading AFD response areas...")
    ra = gpd.read_file("raw_data/afd_response_areas.geojson")
    print(f"  Loaded {len(ra)} response areas")
    print(f"  Columns: {ra.columns.tolist()}")
    print(f"  CRS: {ra.crs}")
    
    # Find the response area ID column
    id_col = None
    for col in ra.columns:
        if 'response' in col.lower() or 'area' in col.lower() or 'id' in col.lower():
            print(f"  Potential ID column: {col} - sample values: {ra[col].head(3).tolist()}")
    
    return ra


def load_census_tracts():
    """Load census tract boundaries for Travis County"""
    print("\nLoading census tract boundaries...")
    
    # Try different possible file locations
    possible_paths = [
        "raw_data/travis_county_tracts.geojson",
        "raw_data/tl_2023_48_tract.shp",
        "raw_data/tl_2023_48_tract/tl_2023_48_tract.shp",
        "raw_data/tl_2022_48_tract.shp",
    ]
    
    tracts = None
    for path in possible_paths:
        if os.path.exists(path):
            print(f"  Found: {path}")
            tracts = gpd.read_file(path)
            break
    
    if tracts is None:
        raise FileNotFoundError(
            "Census tract boundaries not found. Please download and place in raw_data/\n"
            "Options:\n"
            "  1. Download from: https://www2.census.gov/geo/tiger/TIGER2023/TRACT/\n"
            "  2. Or use: python -c \"import geopandas; geopandas.read_file('https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_48_tract.zip').to_file('raw_data/tl_2023_48_tract.shp')\""
        )
    
    print(f"  Loaded {len(tracts)} tracts (all Texas)")
    
    # Filter to Travis County
    county_col = None
    for col in ['COUNTYFP', 'COUNTYFP20', 'COUNTYFP10']:
        if col in tracts.columns:
            county_col = col
            break
    
    if county_col:
        tracts = tracts[tracts[county_col] == '453']
        print(f"  Filtered to Travis County: {len(tracts)} tracts")
    
    return tracts


def load_census_data():
    """Load census population, housing, and year built data"""
    print("\nLoading census data...")

    # Population
    pop = pd.read_csv("raw_data/census_population.csv")
    print(f"  Population data: {len(pop)} rows")

    # Housing
    housing = pd.read_csv("raw_data/census_housing.csv")
    print(f"  Housing data: {len(housing)} rows")

    # Year Built (B25034)
    year_built = None
    if os.path.exists("raw_data/census_year_built.csv"):
        year_built = pd.read_csv("raw_data/census_year_built.csv")
        print(f"  Year built data: {len(year_built)} rows")
    else:
        print("  Warning: Year built data not found")

    return pop, housing, year_built


def process_census_data(pop_df, housing_df, year_built_df=None):
    """
    Process census data into usable format.
    Census API returns data with header row, need to handle that.
    """
    print("\nProcessing census data...")

    # Check if first row is header (check the actual value type)
    if isinstance(pop_df.iloc[0, 0], str) and pop_df.iloc[0, 0] == 'B01003_001E':
        pop_df.columns = pop_df.iloc[0]
        pop_df = pop_df.iloc[1:]

    if isinstance(housing_df.iloc[0, 0], str) and housing_df.iloc[0, 0] == 'B25024_001E':
        housing_df.columns = housing_df.iloc[0]
        housing_df = housing_df.iloc[1:]

    # Create GEOID from state + county + tract (properly formatted)
    if 'state' in pop_df.columns and 'county' in pop_df.columns and 'tract' in pop_df.columns:
        # Convert to strings and pad with zeros to proper lengths
        pop_df['GEOID'] = (pop_df['state'].astype(str).str.zfill(2) +
                          pop_df['county'].astype(str).str.zfill(3) +
                          pop_df['tract'].astype(str).str.zfill(6))
        housing_df['GEOID'] = (housing_df['state'].astype(str).str.zfill(2) +
                              housing_df['county'].astype(str).str.zfill(3) +
                              housing_df['tract'].astype(str).str.zfill(6))

    # Convert population to numeric
    pop_df['population'] = pd.to_numeric(pop_df['B01003_001E'], errors='coerce')

    # Process housing data
    # B25024_002E: 1, detached
    # B25024_003E: 1, attached
    # B25024_004E: 2 units
    # B25024_005E: 3-4 units
    # B25024_006E: 5-9 units
    # B25024_007E: 10-19 units
    # B25024_008E: 20-49 units
    # B25024_009E: 50+ units
    # B25024_010E: Mobile home
    # B25024_011E: Boat, RV, van

    housing_cols = ['B25024_001E', 'B25024_002E', 'B25024_003E', 'B25024_004E',
                    'B25024_005E', 'B25024_006E', 'B25024_007E', 'B25024_008E',
                    'B25024_009E', 'B25024_010E', 'B25024_011E']

    for col in housing_cols:
        if col in housing_df.columns:
            housing_df[col] = pd.to_numeric(housing_df[col], errors='coerce')

    # Calculate housing categories (detailed breakdown per Tim's feedback)
    housing_df['total_units'] = housing_df['B25024_001E']
    housing_df['single_family'] = housing_df['B25024_002E'].fillna(0) + housing_df['B25024_003E'].fillna(0)
    housing_df['duplex'] = housing_df['B25024_004E'].fillna(0)  # 2 units
    housing_df['small_multifamily'] = (housing_df['B25024_005E'].fillna(0) +  # 3-4 units
                                       housing_df['B25024_006E'].fillna(0) +  # 5-9 units
                                       housing_df['B25024_007E'].fillna(0))   # 10-19 units
    housing_df['large_multifamily'] = housing_df['B25024_008E'].fillna(0) + housing_df['B25024_009E'].fillna(0)  # 20+ units
    housing_df['multifamily'] = housing_df['duplex'] + housing_df['small_multifamily'] + housing_df['large_multifamily']
    housing_df['mobile_other'] = housing_df['B25024_010E'].fillna(0) + housing_df['B25024_011E'].fillna(0)

    # Merge population and housing
    census = pop_df[['GEOID', 'population']].merge(
        housing_df[['GEOID', 'total_units', 'single_family', 'duplex',
                    'small_multifamily', 'large_multifamily', 'multifamily', 'mobile_other']],
        on='GEOID',
        how='outer'
    )

    # Process year built data (B25034) if available
    if year_built_df is not None:
        print("  Processing year built data...")

        # Handle header row
        if isinstance(year_built_df.iloc[0, 0], str) and year_built_df.iloc[0, 0] == 'B25034_001E':
            year_built_df.columns = year_built_df.iloc[0]
            year_built_df = year_built_df.iloc[1:]

        # Create GEOID
        if 'state' in year_built_df.columns:
            year_built_df['GEOID'] = (year_built_df['state'].astype(str).str.zfill(2) +
                                      year_built_df['county'].astype(str).str.zfill(3) +
                                      year_built_df['tract'].astype(str).str.zfill(6))

        # B25034 columns:
        # B25034_001E: Total
        # B25034_002E: Built 2020 or later
        # B25034_003E: Built 2010-2019
        # B25034_004E: Built 2000-2009
        # B25034_005E: Built 1990-1999
        # B25034_006E: Built 1980-1989
        # B25034_007E: Built 1970-1979
        # B25034_008E: Built 1960-1969
        # B25034_009E: Built 1950-1959
        # B25034_010E: Built 1940-1949
        # B25034_011E: Built 1939 or earlier

        yb_cols = [f'B25034_{str(i).zfill(3)}E' for i in range(1, 12)]
        for col in yb_cols:
            if col in year_built_df.columns:
                year_built_df[col] = pd.to_numeric(year_built_df[col], errors='coerce')

        # Calculate building age categories (using 2010 cutoff per plan)
        year_built_df['yb_total'] = year_built_df['B25034_001E']
        year_built_df['built_2010_plus'] = (year_built_df['B25034_002E'].fillna(0) +
                                             year_built_df['B25034_003E'].fillna(0))  # 2010+
        year_built_df['built_1970_2009'] = (year_built_df['B25034_004E'].fillna(0) +  # 2000-2009
                                             year_built_df['B25034_005E'].fillna(0) +  # 1990-1999
                                             year_built_df['B25034_006E'].fillna(0) +  # 1980-1989
                                             year_built_df['B25034_007E'].fillna(0))   # 1970-1979
        year_built_df['built_pre_1970'] = (year_built_df['B25034_008E'].fillna(0) +  # 1960-1969
                                            year_built_df['B25034_009E'].fillna(0) +  # 1950-1959
                                            year_built_df['B25034_010E'].fillna(0) +  # 1940-1949
                                            year_built_df['B25034_011E'].fillna(0))   # 1939 or earlier

        # Merge with census data
        census = census.merge(
            year_built_df[['GEOID', 'yb_total', 'built_2010_plus', 'built_1970_2009', 'built_pre_1970']],
            on='GEOID',
            how='left'
        )

        print(f"    Buildings 2010+: {census['built_2010_plus'].sum():,.0f}")
        print(f"    Buildings 1970-2009: {census['built_1970_2009'].sum():,.0f}")
        print(f"    Buildings pre-1970: {census['built_pre_1970'].sum():,.0f}")

    print(f"  Combined census data: {len(census)} tracts")
    print(f"  Total population: {census['population'].sum():,.0f}")
    print(f"  Total housing units: {census['total_units'].sum():,.0f}")

    return census


def create_crosswalk(tracts_gdf, response_areas_gdf):
    """
    Create area-weighted crosswalk between census tracts and response areas.
    """
    print("\nCreating spatial crosswalk...")
    
    # Ensure same CRS (use a projected CRS for accurate area calculations)
    target_crs = "EPSG:32614"  # UTM Zone 14N (covers Austin)
    tracts = tracts_gdf.to_crs(target_crs)
    ra = response_areas_gdf.to_crs(target_crs)
    
    # Calculate tract areas
    tracts['tract_area'] = tracts.geometry.area
    
    # Find GEOID column in tracts
    geoid_col = None
    for col in ['GEOID', 'GEOID20', 'GEOID10', 'TRACTCE', 'TRACTCE20']:
        if col in tracts.columns:
            geoid_col = col
            break
    
    if geoid_col != 'GEOID':
        tracts['GEOID'] = tracts[geoid_col]
    
    # Make sure GEOID is full 11-character format (state + county + tract)
    if tracts['GEOID'].str.len().max() == 6:  # Just tract code
        tracts['GEOID'] = '48453' + tracts['GEOID'].astype(str).str.zfill(6)
    
    # Find response area ID column
    ra_id_col = None
    for col in ra.columns:
        col_lower = col.lower()
        if 'response' in col_lower or ('area' in col_lower and 'id' not in col_lower):
            if ra[col].dtype == 'object' or ra[col].dtype == 'int64':
                ra_id_col = col
                break
    
    if ra_id_col is None:
        # Use first non-geometry column as ID
        ra_id_col = [c for c in ra.columns if c != 'geometry'][0]
    
    print(f"  Using tract ID column: GEOID")
    print(f"  Using response area ID column: {ra_id_col}")
    
    # Intersect tracts with response areas
    print("  Computing intersection (this may take a moment)...")
    intersected = gpd.overlay(tracts, ra, how='intersection')
    print(f"  Created {len(intersected)} intersection polygons")
    
    # Calculate intersection areas
    intersected['intersect_area'] = intersected.geometry.area
    
    # Calculate weight (proportion of tract in this response area)
    intersected['weight'] = intersected['intersect_area'] / intersected['tract_area']
    
    # Create crosswalk table
    crosswalk = intersected[['GEOID', ra_id_col, 'weight', 'tract_area', 'intersect_area']].copy()
    crosswalk.columns = ['GEOID', 'response_area_id', 'weight', 'tract_area', 'intersect_area']
    
    # Validate weights
    weight_sums = crosswalk.groupby('GEOID')['weight'].sum()
    print(f"\n  Weight validation:")
    print(f"    Min weight sum per tract: {weight_sums.min():.3f}")
    print(f"    Max weight sum per tract: {weight_sums.max():.3f}")
    print(f"    Mean weight sum per tract: {weight_sums.mean():.3f}")
    
    return crosswalk, ra_id_col


def allocate_demographics(crosswalk, census_df, response_areas_gdf, ra_id_col):
    """
    Allocate census demographics to response areas using the crosswalk weights.
    """
    print("\nAllocating demographics to response areas...")

    # Ensure GEOID is string type in both dataframes
    crosswalk['GEOID'] = crosswalk['GEOID'].astype(str)
    census_df['GEOID'] = census_df['GEOID'].astype(str)

    # Merge crosswalk with census data
    merged = crosswalk.merge(census_df, on='GEOID', how='left')

    # Apply weights to all numeric columns
    numeric_cols = ['population', 'total_units', 'single_family', 'duplex',
                    'small_multifamily', 'large_multifamily', 'multifamily', 'mobile_other',
                    'yb_total', 'built_2010_plus', 'built_1970_2009', 'built_pre_1970']

    for col in numeric_cols:
        if col in merged.columns:
            merged[f'{col}_weighted'] = merged[col] * merged['weight']

    # Aggregate to response area
    agg_cols = {f'{col}_weighted': 'sum' for col in numeric_cols if f'{col}_weighted' in merged.columns}

    ra_demographics = merged.groupby('response_area_id').agg(agg_cols).reset_index()

    # Rename columns (remove _weighted suffix)
    ra_demographics.columns = [c.replace('_weighted', '') for c in ra_demographics.columns]

    # Calculate derived metrics - housing type percentages
    if 'single_family' in ra_demographics.columns and 'total_units' in ra_demographics.columns:
        ra_demographics['pct_single_family'] = (ra_demographics['single_family'] / ra_demographics['total_units'] * 100).fillna(0)
        ra_demographics['pct_duplex'] = (ra_demographics['duplex'] / ra_demographics['total_units'] * 100).fillna(0)
        ra_demographics['pct_small_mf'] = (ra_demographics['small_multifamily'] / ra_demographics['total_units'] * 100).fillna(0)
        ra_demographics['pct_large_mf'] = (ra_demographics['large_multifamily'] / ra_demographics['total_units'] * 100).fillna(0)
        ra_demographics['pct_multifamily'] = (ra_demographics['multifamily'] / ra_demographics['total_units'] * 100).fillna(0)

    # Calculate derived metrics - building age percentages
    if 'built_2010_plus' in ra_demographics.columns and 'yb_total' in ra_demographics.columns:
        ra_demographics['pct_built_2010_plus'] = (ra_demographics['built_2010_plus'] / ra_demographics['yb_total'] * 100).fillna(0)
        ra_demographics['pct_built_1970_2009'] = (ra_demographics['built_1970_2009'] / ra_demographics['yb_total'] * 100).fillna(0)
        ra_demographics['pct_built_pre_1970'] = (ra_demographics['built_pre_1970'] / ra_demographics['yb_total'] * 100).fillna(0)

    print(f"\n  Response area demographics summary:")
    print(f"    Total response areas: {len(ra_demographics)}")
    print(f"    Total allocated population: {ra_demographics['population'].sum():,.0f}")
    print(f"    Total allocated housing units: {ra_demographics['total_units'].sum():,.0f}")

    if 'built_2010_plus' in ra_demographics.columns:
        print(f"    Buildings 2010+: {ra_demographics['built_2010_plus'].sum():,.0f}")
        print(f"    Buildings 1970-2009: {ra_demographics['built_1970_2009'].sum():,.0f}")
        print(f"    Buildings pre-1970: {ra_demographics['built_pre_1970'].sum():,.0f}")
    
    # Merge back with response area geometries
    ra = response_areas_gdf.copy()
    ra['response_area_id'] = ra[ra_id_col]
    ra = ra.merge(ra_demographics, on='response_area_id', how='left')
    
    # Calculate area in square miles
    ra_projected = ra.to_crs("EPSG:32614")
    ra['area_sq_miles'] = ra_projected.geometry.area / 2.59e6  # sq meters to sq miles
    
    # Calculate population density
    ra['pop_density'] = ra['population'] / ra['area_sq_miles']
    
    # Classify urban/suburban
    def classify(density):
        if pd.isna(density) or density == 0:
            return 'unknown'
        elif density >= 10000:
            return 'urban_core'
        elif density >= 3000:
            return 'inner_suburban'
        else:
            return 'outer_suburban'
    
    ra['urban_class'] = ra['pop_density'].apply(classify)
    
    print(f"\n  Urban classification distribution:")
    print(ra['urban_class'].value_counts())
    
    return ra_demographics, ra


def main():
    print("\n" + "#"*60)
    print("# FIRE RESOURCE ANALYSIS - CREATE SPATIAL CROSSWALK")
    print("#"*60)
    
    # Load data
    response_areas = load_response_areas()
    tracts = load_census_tracts()
    pop_df, housing_df, year_built_df = load_census_data()

    # Process census data
    census = process_census_data(pop_df, housing_df, year_built_df)
    
    # Create crosswalk
    crosswalk, ra_id_col = create_crosswalk(tracts, response_areas)
    
    # Allocate demographics
    ra_demographics, ra_with_demographics = allocate_demographics(
        crosswalk, census, response_areas, ra_id_col
    )
    
    # Save outputs
    os.makedirs("processed_data", exist_ok=True)
    
    crosswalk.to_csv("processed_data/tract_to_response_area_crosswalk.csv", index=False)
    print(f"\n✓ Saved: processed_data/tract_to_response_area_crosswalk.csv")
    
    ra_demographics.to_csv("processed_data/response_area_demographics.csv", index=False)
    print(f"✓ Saved: processed_data/response_area_demographics.csv")
    
    # Save as GeoJSON (convert back to WGS84)
    ra_with_demographics = ra_with_demographics.to_crs("EPSG:4326")
    ra_with_demographics.to_file("processed_data/response_areas_with_demographics.geojson", driver='GeoJSON')
    print(f"✓ Saved: processed_data/response_areas_with_demographics.geojson")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Response areas with demographics: {len(ra_with_demographics)}")
    print(f"\nUrban classification:")
    for cls, count in ra_with_demographics['urban_class'].value_counts().items():
        pop = ra_with_demographics[ra_with_demographics['urban_class'] == cls]['population'].sum()
        print(f"  {cls}: {count} areas, {pop:,.0f} population")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Review the response_areas_with_demographics.geojson in QGIS or geojson.io
   - Does the urban/suburban classification look reasonable?
   - Any response areas with missing data?

2. Adjust density thresholds if needed in this script

3. Run the next script:
   python scripts/04_analysis.py
""")


if __name__ == "__main__":
    main()
