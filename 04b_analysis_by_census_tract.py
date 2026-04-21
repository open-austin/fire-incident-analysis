#!/usr/bin/env python3
"""
Step 4c: Analysis by Census Tract
==================================
Analyzes structure fire incidents by census tract using demographic data.
This approach ignores response areas and focuses on geographic census boundaries.

Usage:
    python 04c_analysis_by_census_tract.py

Input:
    processed_data/sf_incidents_with_tracts.csv
    raw_data/census_population.csv
    raw_data/census_housing.csv
    raw_data/census_year_built.csv
    raw_data/census_income.csv

Output:
    outputs/census_tract_incidents.csv
    outputs/census_tract_summary.csv
    outputs/incident_rates_by_housing_and_type.csv
    outputs/cause_by_housing_type.csv
    outputs/heat_source_by_housing.csv
    outputs/sprinkler_by_housing.csv
    outputs/area_origin_by_housing.csv
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import os
import warnings
from scipy import stats
import ast
from census_variables import YEAR_BUILT_VARS, HOUSING_VARS, POPULATION_VARS, AUSTIN_COUNTIES

warnings.filterwarnings('ignore')


def parse_census_tracts(tract_str):
    """
    Parse census tract string from incidents file.
    Input: string like "['410']" or "['15.03']" or "['2.04', '2.03']"
    Returns: list of tract codes, or empty list if parsing fails
    """
    if pd.isna(tract_str) or tract_str == '':
        return []
    try:
        # Remove any whitespace
        tract_str = str(tract_str).strip()
        # Try to evaluate as Python literal
        tracts = ast.literal_eval(tract_str)
        if isinstance(tracts, str):
            return [tracts]
        elif isinstance(tracts, list):
            return [str(t) for t in tracts]
        else:
            return []
    except:
        return []


def load_data():
    """Load incident and census demographic data"""
    print("\nLoading data...")
    
    # Load structure fire incidents with census tracts
    incidents = pd.read_csv("processed_data/sf_incidents_with_tracts.csv")
    print(f"  Structure fire incidents: {len(incidents):,}")
    
    # Parse census tract column
    incidents['tract_list'] = incidents['tract_codes'].apply(parse_census_tracts)
    
    # Check coverage
    has_tract = incidents['tract_list'].apply(len) > 0
    print(f"  Incidents with tract data: {has_tract.sum():,} ({has_tract.sum()/len(incidents)*100:.1f}%)")

    
    # Load census demographics
    pop_data = pd.read_csv("raw_data/census_population.csv", dtype={'tract': str})
    pop_data = pop_data.rename(columns={'B01003_001E': POPULATION_VARS['B01003_001E']})
    print(f"  Census tracts with population: {len(pop_data)}")
    
    housing_data = pd.read_csv("raw_data/census_housing.csv", dtype={'tract': str})
    for c in housing_data.columns:
        housing_data.rename(columns={c: HOUSING_VARS.get(c, c)}, inplace=True)

    print(f"  Census tracts with housing: {len(housing_data)}")
    
    age_data = pd.read_csv("raw_data/census_year_built.csv", dtype={'tract': str})
    for c in age_data.columns:
        age_data.rename(columns={c: YEAR_BUILT_VARS.get(c, c)}, inplace=True)
    print(f"  Census tracts with building age: {len(age_data)}")
    
    income_data = pd.read_csv("raw_data/census_income.csv", dtype={'tract': str})
    # Only extract relevant income columns
    # This file collates the column codes and the human-readable labels, leaving coded columns blank.
    # So, only extract based on the column code.
    # In future, if this is buggy, pick the column index based on code, and increment by one.
    income_data = income_data[['tract', 'Estimate!!Households!!Median income (dollars)']]
    
    print(f"  Census tracts with income: {len(income_data)}")

    shape_data = gpd.read_file("raw_data/tl_2023_48_tract.shp")
    shape_data = shape_data[['TRACTCE', 'ALAND']]

    return incidents, pop_data, housing_data, age_data, income_data, shape_data

# Make sure this averages out the census demographics in the case of boundaries.
def prepare_census_demographics(pop_data, housing_data, age_data, income_data, shape_data):
    """
    Merge census demographic files into a single dataframe by tract code.
    """
    print("\nPreparing census demographics...")
    
    # Standardize tract column names and format
    pop_data = pop_data.rename(columns={'Total population': 'population', 'tract': 'tract_code'})
    housing_data = housing_data.rename(columns={'Total': 'total_units', 'tract': 'tract_code'})
    age_data = age_data.rename(columns={'Total': 'total_units_age', 'tract': 'tract_code'})
    income_data = income_data.rename(columns={'Estimate!!Households!!Median income (dollars)': 'median_income', 'tract': 'tract_code'})
    shape_data = shape_data.rename(columns={'TRACTCE': 'tract_code', 'ALAND': 'land_area_m2'})
    
    # Convert tract codes to strings
    pop_data['tract_code'] = pop_data['tract_code'].astype(str)
    housing_data['tract_code'] = housing_data['tract_code'].astype(str)
    age_data['tract_code'] = age_data['tract_code'].astype(str)
    income_data['tract_code'] = income_data['tract_code'].astype(str)
    shape_data['tract_code'] = shape_data['tract_code'].astype(str)

    # Merge population with housing
    census = pop_data[['tract_code', 'population']].merge(
        housing_data[['tract_code', 'total_units', '1-unit, detached', '1-unit, attached']],
        on='tract_code', how='outer'
    )
    
    # Merge with building age
    census = census.merge(
        age_data[['tract_code', 'total_units_age', 'Built 2010-2019', 'Built 2020 or later', 'Built 1939 or earlier']],
        on='tract_code', how='outer'
    )
    
    # Calculate single-family percentage
    census['single_family_units'] = (
        census['1-unit, detached'].fillna(0) + census['1-unit, attached'].fillna(0)
    )
    census['pct_single_family'] = np.where(
        census['total_units'] > 0,
        census['single_family_units'] / census['total_units'] * 100,
        np.nan
    )
    
    # Calculate building age percentages
    census['pct_built_2010_plus'] = np.where(
        census['total_units_age'] > 0,
        (census['Built 2010-2019'].fillna(0) + census['Built 2020 or later'].fillna(0)) / 
        census['total_units_age'] * 100,
        np.nan
    )
    
    census['pct_built_pre1970'] = np.where(
        census['total_units_age'] > 0,
        census['Built 1939 or earlier'].fillna(0) / census['total_units_age'] * 100,
        np.nan
    )
    
    # Merge with income data
    census = census.merge(
        income_data[['tract_code', 'median_income']],
        on='tract_code',
        how='left'
    )
    
    # Merge with shape data for land area and density
    census = census.merge(
        shape_data,
        on='tract_code',
        how='left'
    )
    # Population density, converted to sq miles
    census['population_density'] = census['population'] / census['land_area_m2'] * 2.59e+6 

    print(f"  Census tracts in demographics: {len(census)}")
    
    return census


def explode_incidents_by_tract(incidents_df, census_df):
     ### Since we're exploding by tract, we need to make sure to average out the census demographics in the case of boundaries.
    """
    Create one row per incident-tract combination.
    For incidents in multiple tracts, duplicate the row.
    """
    print("\nExploding incidents by tract...")
    
    # Create list of incident-tract pairs
    pairs = []
    for idx, row in incidents_df.iterrows():
        tracts = row['tract_list']
        if len(tracts) > 0:
            for tract in tracts:
                pairs.append({**row.to_dict(), 'tract_code': tract})
    
    # Convert to dataframe
    exploded = pd.DataFrame(pairs)
    print(f"  Incident-tract pairs: {len(exploded):,}")

    exploded = exploded.merge(
        census_df[['tract_code', 'population', 'total_units', 'pct_single_family', 
                        'pct_built_2010_plus', 'pct_built_pre1970', 'median_income']],
        on='tract_code',
        how='left'
    )
    
    matched = exploded['population'].notna().sum()
    print(f"  Incidents with census data: {matched:,} ({matched/len(exploded)*100:.1f}%)")
    
    if matched < len(exploded) * 0.1:  # If match rate is still low, try simpler approach
        print(f"  Match rate low - checking available tracts in data...")
        print(f"    Unique incident tracts: {exploded['tract_code'].nunique()}")
        print(f"    Unique census tracts: {census_df['tract_code'].nunique()}")
        print(f"    Sample incident codes: {exploded['tract_code'].unique()[:10]}")
        print(f"    Sample census codes: {census_df['tract_code'].unique()[:10]}")
    
    return exploded


def aggregate_by_tract(incidents_df):
    """
    Aggregate incidents to census tract level.
    """
    print("\nAggregating incidents by census tract...")
    
    # Get unique census tracts and demographics
    tract_summary = incidents_df.groupby('tract_code').agg({
        'incident_number': 'count',
        'population': 'first',
        'total_units': 'first',
        'pct_single_family': 'first',
        'pct_built_2010_plus': 'first',
        'pct_built_pre1970': 'first',
        'median_income': 'first',
        'calendaryear': lambda x: x.nunique()  # years of data
    }).reset_index()
    
    tract_summary.columns = ['tract_code', 'total_incidents', 'population', 'total_units',
                             'pct_single_family', 'pct_built_2010_plus', 'pct_built_pre1970', 'median_income', 'years']
    
    # Calculate per-capita and per-unit rates
    tract_summary['incidents_per_1000_pop'] = np.where(
        tract_summary['population'] > 0,
        (tract_summary['total_incidents'] / tract_summary['population']) * 1000,
        np.nan
    )
    
    tract_summary['incidents_per_1000_units'] = np.where(
        tract_summary['total_units'] > 0,
        (tract_summary['total_incidents'] / tract_summary['total_units']) * 1000,
        np.nan
    )
    
    # Annualize
    tract_summary['annual_incidents_per_1000_pop'] = (
        tract_summary['incidents_per_1000_pop'] / tract_summary['years']
    )
    tract_summary['annual_incidents_per_1000_units'] = (
        tract_summary['incidents_per_1000_units'] / tract_summary['years']
    )
    
    print(f"  Census tracts with incidents: {len(tract_summary)}")
    print(f"  Total incidents: {tract_summary['total_incidents'].sum():,}")
    print(f"  Population covered: {tract_summary['population'].sum():,.0f}")
    print(f"  Housing units covered: {tract_summary['total_units'].sum():,.0f}")
    
    return tract_summary


def analyze_by_housing_type(incident_df):
    """
    Analyze incidents by housing typology (% single-family).
    """
    print("\nAnalyzing by housing typology...")
    
    # Filter to valid data
    valid = incident_df[
        (incident_df['population'] > 0) & 
        (incident_df['total_units'] > 0) &
        (incident_df['pct_single_family'].notna())
    ].copy()
    
    # Create housing categories
    valid['housing_type'] = pd.cut(
        valid['pct_single_family'],
        bins=[0, 25, 50, 75, 100],
        labels=['Multifamily (<25% SF)', 'Mixed-Low (25-50% SF)', 
                'Mixed-High (50-75% SF)', 'Single-Family (>75% SF)'],
        include_lowest=True
    )
    
    # Aggregate
    summary = valid.groupby('housing_type').agg({
        'total_incidents': 'sum',
        'population': 'sum',
        'total_units': 'sum',
        'tract_code': 'count'
    }).reset_index()
    
    summary.columns = ['housing_type', 'total_incidents', 'population', 'total_units', 'num_tracts']
    
    # Calculate rates
    summary['incidents_per_1000_pop'] = (summary['total_incidents'] / summary['population']) * 1000
    summary['incidents_per_1000_units'] = (summary['total_incidents'] / summary['total_units']) * 1000
    
    print("\n" + "="*80)
    print("INCIDENTS BY HOUSING TYPOLOGY")
    print("="*80)
    print(summary.to_string(index=False))
    
    return summary


def analyze_by_building_age(incident_df):
    """
    Analyze incidents by building age (pre-1970 vs 2010+).
    """
    print("\nAnalyzing by building age...")
    
    # Filter to valid data
    valid = incident_df[
        (incident_df['population'] > 0) & 
        (incident_df['total_units'] > 0) &
        (incident_df['pct_built_2010_plus'].notna())
    ].copy()
    
    # Create age categories
    valid['age_category'] = np.where(
        valid['pct_built_2010_plus'] >= 50,
        'Newer (50%+ post-2010)',
        'Older (<50% post-2010)'
    )
    
    # Aggregate
    summary = valid.groupby('age_category').agg({
        'total_incidents': 'sum',
        'population': 'sum',
        'total_units': 'sum',
        'tract_code': 'count'
    }).reset_index()
    
    summary.columns = ['age_category', 'total_incidents', 'population', 'total_units', 'num_tracts']
    
    # Calculate rates
    summary['incidents_per_1000_pop'] = (summary['total_incidents'] / summary['population']) * 1000
    summary['incidents_per_1000_units'] = (summary['total_incidents'] / summary['total_units']) * 1000
    
    print("\n" + "="*80)
    print("INCIDENTS BY BUILDING AGE")
    print("="*80)
    print(summary.to_string(index=False))
    
    return summary


def analyze_incident_characteristics(incidents_df):
    """
    Analyze incident characteristics by housing type and building age.
    Focus on cause, heat source, sprinkler presence, area of origin.
    """
    print("\nAnalyzing incident characteristics...")
    
    # Filter to valid data with housing information
    valid = incidents_df[
        (incidents_df['population'] > 0) & 
        (incidents_df['total_units'] > 0) &
        (incidents_df['pct_single_family'].notna())
    ].copy()
    
    # Create housing categories
    valid['housing_type'] = pd.cut(
        valid['pct_single_family'],
        bins=[0, 25, 50, 75, 100],
        labels=['Multifamily', 'Mixed-Low', 'Mixed-High', 'Single-Family'],
        include_lowest=True
    )
    
    # Create summary by housing type for major fields
    housing_summary = []
    
    # Count by housing type
    for htype in ['Multifamily', 'Mixed-Low', 'Mixed-High', 'Single-Family']:
        subset = valid[valid['housing_type'] == htype]
        housing_summary.append({
            'housing_type': htype,
            'num_incidents': len(subset),
            'num_tracts': subset['tract_code'].nunique(),
            'avg_incidents_per_tract': len(subset) / subset['tract_code'].nunique() if subset['tract_code'].nunique() > 0 else 0,
            'population': subset['population'].sum(),
            'housing_units': subset['total_units'].sum()
        })
    
    housing_df = pd.DataFrame(housing_summary)
    housing_df['incidents_per_1000_units'] = (
        housing_df['num_incidents'] / housing_df['housing_units'] * 1000
    )
    
    print("\n" + "="*80)
    print("INCIDENT CHARACTERISTICS BY HOUSING TYPE")
    print("="*80)
    print(housing_df.to_string(index=False))
    
    return housing_df


def run_statistical_tests(tract_summary_df):
    """
    Run statistical tests on tract-level data.
    """
    print("\nRunning statistical tests...")
    
    results = []
    
    # Filter to valid data
    valid = tract_summary_df[
        (tract_summary_df['population'] > 100) &
        (tract_summary_df['incidents_per_1000_pop'].notna())
    ].copy()
    
    results.append("="*80)
    results.append("STATISTICAL TESTS - CENSUS TRACT ANALYSIS")
    results.append("="*80)
    results.append("")
    
    # Housing type analysis
    valid['housing_type'] = pd.cut(
        valid['pct_single_family'],
        bins=[0, 25, 50, 75, 100],
        labels=['Multifamily', 'Mixed-Low', 'Mixed-High', 'Single-Family'],
        include_lowest=True
    )
    
    # ANOVA: Incidents per capita by housing type
    groups = []
    for htype in ['Multifamily', 'Mixed-Low', 'Mixed-High', 'Single-Family']:
        group_data = valid[valid['housing_type'] == htype]['incidents_per_1000_pop'].dropna()
        if len(group_data) > 0:
            groups.append(group_data)
    
    if len(groups) >= 2:
        f_stat, p_value = stats.f_oneway(*groups)
        results.append("ANOVA: Incident Rates by Housing Type")
        results.append(f"  F-statistic: {f_stat:.3f}")
        results.append(f"  p-value: {p_value:.6f}")
        results.append(f"  Significant (alpha=0.05): {'Yes' if p_value < 0.05 else 'No'}")
        results.append("")
    
    # Correlation: % Single-Family vs Incident Rate
    corr_data = valid[['pct_single_family', 'incidents_per_1000_pop']].dropna()
    if len(corr_data) > 10:
        corr, p_value = stats.pearsonr(
            corr_data['pct_single_family'],
            corr_data['incidents_per_1000_pop']
        )
        results.append("Correlation: % Single-Family vs Incident Rate")
        results.append(f"  Pearson r: {corr:.3f}")
        results.append(f"  p-value: {p_value:.6f}")
        results.append(f"  Interpretation: {'Positive' if corr > 0 else 'Negative'} correlation")
        results.append("")
    
    # Correlation: % Built 2010+ vs Incident Rate
    if 'pct_built_2010_plus' in valid.columns:
        age_data = valid[['pct_built_2010_plus', 'incidents_per_1000_pop']].dropna()
        if len(age_data) > 10:
            corr, p_value = stats.pearsonr(
                age_data['pct_built_2010_plus'],
                age_data['incidents_per_1000_pop']
            )
            results.append("Correlation: % Built 2010+ vs Incident Rate")
            results.append(f"  Pearson r: {corr:.3f}")
            results.append(f"  p-value: {p_value:.6f}")
            results.append(f"  Interpretation: {'Newer' if corr < 0 else 'Older'} buildings have higher rates")
            results.append("")
    
    # T-test: High vs Low single-family concentration
    median_sf = valid['pct_single_family'].median()
    high_sf = valid[valid['pct_single_family'] >= median_sf]['incidents_per_1000_pop'].dropna()
    low_sf = valid[valid['pct_single_family'] < median_sf]['incidents_per_1000_pop'].dropna()
    
    if len(high_sf) > 0 and len(low_sf) > 0:
        t_stat, p_value = stats.ttest_ind(high_sf, low_sf, equal_var=False)
        results.append("T-Test: High SF vs Low SF Tracts")
        results.append(f"  High SF mean: {high_sf.mean():.2f} incidents per 1,000 pop")
        results.append(f"  Low SF mean: {low_sf.mean():.2f} incidents per 1,000 pop")
        results.append(f"  t-statistic: {t_stat:.3f}")
        results.append(f"  p-value: {p_value:.6f}")
        results.append(f"  Significant (alpha=0.05): {'Yes' if p_value < 0.05 else 'No'}")
        results.append("")
    
    print("\n" + "\n".join(results))
    
    return "\n".join(results)


def main():
    print("\n" + "#"*60)
    print("# FIRE ANALYSIS BY CENSUS TRACT")
    print("#"*60)
    
    # Load data
    incidents, pop_data, housing_data, age_data, income_data, shape_data = load_data()
    
    # Prepare census demographics
    census = prepare_census_demographics(pop_data, housing_data, age_data, income_data, shape_data)
    census.to_csv("processed_data/census_demographics.csv", index=False)

    # Explode incidents by tract and join with demographics
    incidents_by_tract = explode_incidents_by_tract(incidents, census)

    # Aggregate to tract level
    tract_summary = aggregate_by_tract(incidents_by_tract)
    
    # Analyses
    housing_analysis = analyze_by_housing_type(tract_summary)
    age_analysis = analyze_by_building_age(tract_summary)
    characteristics = analyze_incident_characteristics(incidents_by_tract)
    test_results = run_statistical_tests(tract_summary)
    
    # Save outputs
    os.makedirs("outputs", exist_ok=True)
    
    tract_summary.to_csv("outputs/census_tract_incidents.csv", index=False)
    print(f"\n✓ Saved: outputs/census_tract_incidents.csv")
    
    housing_analysis.to_csv("outputs/incident_rates_by_housing_and_type.csv", index=False)
    print(f"✓ Saved: outputs/incident_rates_by_housing_and_type.csv")
    
    age_analysis.to_csv("outputs/building_age_summary.csv", index=False)
    print(f"✓ Saved: outputs/building_age_summary.csv")
    
    characteristics.to_csv("outputs/incident_characteristics_by_housing.csv", index=False)
    print(f"✓ Saved: outputs/incident_characteristics_by_housing.csv")
    
    with open("outputs/statistical_tests_census_tracts.txt", 'w', encoding='utf-8') as f:
        f.write(test_results)
    print(f"✓ Saved: outputs/statistical_tests_census_tracts.txt")
    
    # Print summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"Total structure fire incidents: {incidents['incident_number'].nunique():,}")
    print(f"Total incident-tract pairs: {len(incidents_by_tract):,}")
    print(f"Census tracts with incidents: {tract_summary['tract_code'].nunique():,}")
    print(f"Total population in affected tracts: {tract_summary['population'].sum():,.0f}")
    print(f"Total housing units in affected tracts: {tract_summary['total_units'].sum():,.0f}")
    print(f"Average incidents per tract: {tract_summary['total_incidents'].mean():.1f}")
    print(f"Median incidents per tract: {tract_summary['total_incidents'].median():.1f}")
    print(f"Max incidents in single tract: {tract_summary['total_incidents'].max():.0f}")
    print(f"Overall incident rate: {(tract_summary['total_incidents'].sum() / tract_summary['population'].sum() * 1000):.2f} per 1,000 pop")


if __name__ == "__main__":
    main()
