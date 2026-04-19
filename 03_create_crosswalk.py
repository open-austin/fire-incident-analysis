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
    raw_data/tl_2023_48_tract.shp (or similar census tract shapefile for Austin-area counties)
    raw_data/census_population.csv
    raw_data/census_housing.csv
    raw_data/census_year_built.csv
    raw_data/census_income.csv

Output:
    processed_data/tract_to_response_area_crosswalk.csv
    processed_data/response_area_demographics.csv
    processed_data/response_areas_with_demographics.geojson
"""

import pandas as pd
import geopandas as gpd
import os
import warnings
from census_variables import YEAR_BUILT_VARS, HOUSING_VARS, POPULATION_VARS, AUSTIN_COUNTIES

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
    """Load census tract boundaries for Austin-area Counties"""
    print("\nLoading census tract boundaries...")
    
    # Try different possible file locations
    possible_paths = [
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
    
    # Filter to Austin-Area Counties (Travis, Hays, Williamson)
    county_col = None
    for col in ['COUNTYFP', 'COUNTYFP20', 'COUNTYFP10']:
        if col in tracts.columns:
            county_col = col
            break
    
    if county_col:
        tracts = tracts[tracts[county_col].isin(AUSTIN_COUNTIES.values())]
        print(f"  Filtered to Austin-area Counties: {len(tracts)} tracts")
    
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

    # Income
    income = None
    if os.path.exists("raw_data/census_income.csv"):
        income = pd.read_csv("raw_data/census_income.csv")
        print(f"  Income data: {len(income)} rows")
    else:
        print("  Warning: Income data not found")

    return pop, housing, year_built, income


def process_census_data(pop_df, housing_df, year_built_df=None, income_df=None):
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

    def _get_code_column(df, code, var_map):
        name = var_map.get(code, code)
        if name in df.columns:
            return name
        if code in df.columns:
            return code
        return None

    # Convert population to numeric
    pop_col = _get_code_column(pop_df, 'B01003_001E', POPULATION_VARS)
    if pop_col:
        pop_df['population'] = pd.to_numeric(pop_df[pop_col], errors='coerce')
    else:
        pop_df['population'] = pd.NA

    # Process housing data
    housing_codes = [c for c in HOUSING_VARS.keys() if c != 'NAME']
    for code in housing_codes:
        src_col = _get_code_column(housing_df, code, HOUSING_VARS)
        if src_col:
            housing_df[code] = pd.to_numeric(housing_df[src_col], errors='coerce')
        else:
            housing_df[code] = pd.NA

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

        # B25034 columns are now defined in census_variables.YEAR_BUILT_VARS
        yb_codes = [c for c in YEAR_BUILT_VARS.keys() if c != 'NAME']
        for code in yb_codes:
            src_col = _get_code_column(year_built_df, code, YEAR_BUILT_VARS)
            if src_col:
                year_built_df[code] = pd.to_numeric(year_built_df[src_col], errors='coerce')
            else:
                year_built_df[code] = pd.NA

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

        
    # Extract Income Data
    if income_df is not None:
        print("  Processing income data...")

        # Create GEOID
        if 'state' in income_df.columns:
            income_df['GEOID'] = (income_df['state'].astype(str).str.zfill(2) +
                                      income_df['county'].astype(str).str.zfill(3) +
                                      income_df['tract'].astype(str).str.zfill(6))
    
        # Only extract relevant income columns
        # This file collates the column codes and the human-readable labels, leaving coded columns blank.
        # So, only extract based on the column code.
        # In future, if this is buggy, pick the column index based on code, and increment by one.
        income_df = income_df[['GEOID', 'Estimate!!Households!!Median income (dollars)']].rename(columns={'Estimate!!Households!!Median income (dollars)': 'median_income'})  
        census = census.merge(
                income_df[['GEOID', 'median_income']],
                on='GEOID',
                how='left'
            )
        
    print(f"  Combined census data: {len(census)} tracts")
    print(f"  Total population: {census['population'].sum():,.0f}")
    print(f"  Total housing units: {census['total_units'].sum():,.0f}")
    if income_df is not None:
        print(f"  Average median income: {census['median_income'].mean():,.0f}")

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
    
    # Find response area ID column
    ra_id_col = 'RESPONSE_AREA_NAME' # Hyphenated alpha-numeric to match incidents dataset.
    
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
    pop_df, housing_df, year_built_df, income_df = load_census_data()

    # Process census data
    census = process_census_data(pop_df, housing_df, year_built_df, income_df)
    
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
