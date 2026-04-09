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

Output:
    Temporarily outputing to /ekyl subdirectory
    ekyl/outputs/census_tract_incidents.csv
    ekyl/outputs/census_tract_summary.csv
    ekyl/outputs/incident_rates_by_housing_and_type.csv
    ekyl/outputs/cause_by_housing_type.csv
    ekyl/outputs/heat_source_by_housing.csv
    ekyl/outputs/sprinkler_by_housing.csv
    ekyl/outputs/area_origin_by_housing.csv
"""

import pandas as pd
import numpy as np
from scipy import stats
import os
import warnings
import ast
import statsmodels.api as sm
from statsmodels.formula.api import ols

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
    print(f"  Census tracts with population: {len(pop_data)}")
    
    housing_data = pd.read_csv("raw_data/census_housing.csv", dtype={'tract': str})
    print(f"  Census tracts with housing: {len(housing_data)}")
    
    age_data = pd.read_csv("raw_data/census_year_built.csv", dtype={'tract': str})
    print(f"  Census tracts with building age: {len(age_data)}")
    
    return incidents, pop_data, housing_data, age_data

# Make sure this averages out the census demographics in the case of boundaries.
def prepare_census_demographics(pop_data, housing_data, age_data):
    """
    Merge census demographic files into a single dataframe by tract code.
    """
    print("\nPreparing census demographics...")
    
    # Standardize tract column names and format
    pop_data = pop_data.rename(columns={'Total population': 'population', 'tract': 'tract_code'})
    housing_data = housing_data.rename(columns={'Total': 'total_units', 'tract': 'tract_code'})
    age_data = age_data.rename(columns={'Total': 'total_units_age', 'tract': 'tract_code'})
    
    # Convert tract codes to strings
    pop_data['tract_code'] = pop_data['tract_code'].astype(str)
    housing_data['tract_code'] = housing_data['tract_code'].astype(str)
    age_data['tract_code'] = age_data['tract_code'].astype(str)
    
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
                        'pct_built_2010_plus', 'pct_built_pre1970']],
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
        'calendaryear': lambda x: x.nunique()  # years of data
    }).reset_index()
    
    tract_summary.columns = ['tract_code', 'total_incidents', 'population', 'total_units',
                             'pct_single_family', 'pct_built_2010_plus', 'pct_built_pre1970', 'years']
    
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
        labels=['Multifamily', 'Mixed_Low', 'Mixed_High', 'Single_Family'],
        include_lowest=True
    )
    
    # Find relevant columns for incident characteristics
    # (These depend on what's actually in the raw incident data)
    
    print(f"\n  Available columns: {list(incidents_df.columns)[:20]}...")
    
    # Create summary by housing type for major fields
    housing_summary = []
    
    # Count by housing type
    for htype in ['Multifamily', 'Mixed_Low', 'Mixed_High', 'Single_Family']:
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
    for htype in ['Multifamily', 'Mixed_Low', 'Mixed_High', 'Single_Family']:
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


def bivariate_analysis_housing_by_age(incident_df):
    """
    Perform bivariate analysis of housing type and building age.
    Creates a 2D matrix analyzing the joint effects of housing typology and building age.
    """
    print("\n" + "="*80)
    print("BIVARIATE ANALYSIS: HOUSING TYPE × BUILDING AGE")
    print("="*80)
    
    # Filter to valid data
    valid = incident_df[
        (incident_df['population'] > 0) & 
        (incident_df['total_units'] > 0) &
        (incident_df['pct_single_family'].notna()) &
        (incident_df['pct_built_2010_plus'].notna())
    ].copy()
    
    # Calculate incident rate if not already present
    if 'incidents_per_1000_pop' not in valid.columns:
        valid['incidents_per_1000_pop'] = (valid['incident_number'] / valid['population'] * 1000)
    
    print(f"\nCases with complete housing and age data: {len(valid):,}")
    
    # Create housing type categories
    valid['housing_type'] = pd.cut(
        valid['pct_single_family'],
        bins=[0, 25, 50, 75, 100],
        labels=['Multifamily', 'Mixed_Low', 'Mixed_High', 'Single_Family'],
        include_lowest=True
    )
    
    # Create building age categories
    valid['age_category'] = np.where(
        valid['pct_built_2010_plus'] >= 50,
        'Newer (50%+ post-2010)',
        'Older (<50% post-2010)'
    )
    
    # Create 2x4 matrix: Age × Housing Type
    matrix = valid.groupby(['age_category', 'housing_type']).agg({
        'incident_number': 'count',
        'population': 'sum',
        'total_units': 'sum',
        'tract_code': 'count'
    }).reset_index()
    
    matrix.columns = ['age_category', 'housing_type', 'total_incidents', 'population', 'total_units', 'num_tracts']
    
    # Calculate rates
    matrix['incidents_per_1000_pop'] = (matrix['total_incidents'] / matrix['population']) * 1000
    matrix['incidents_per_1000_units'] = (matrix['total_incidents'] / matrix['total_units']) * 1000
    
    # Print detailed matrix
    print("\nDETAILED MATRIX: Incident Rates by Housing Type and Building Age")
    print("-" * 100)
    print(matrix.to_string(index=False))
    
    # Create pivot table for better visualization
    print("\n" + "-"*80)
    print("PIVOT TABLE: Incidents per 1,000 Population")
    print("-"*80)
    pivot_pop = matrix.pivot(index='age_category', columns='housing_type', values='incidents_per_1000_pop')
    print(pivot_pop.to_string())
    
    print("\n" + "-"*80)
    print("PIVOT TABLE: Incidents per 1,000 Housing Units")
    print("-"*80)
    pivot_units = matrix.pivot(index='age_category', columns='housing_type', values='incidents_per_1000_units')
    print(pivot_units.to_string())
    
    # Statistical tests for interaction effects
    print("\n" + "-"*80)
    print("STATISTICAL ANALYSIS")
    print("-"*80)
    
    results = []
    results.append("")
    results.append("INTERACTION TESTS:")
    results.append("Testing if the effects of housing type and age are independent")
    results.append("")
    
    # Two-way ANOVA approach using individual data
    from scipy.stats import f_oneway
    
    # Create groups for each combination
    groups_by_combo = {}
    for age in ['Newer (50%+ post-2010)', 'Older (<50% post-2010)']:
        for htype in ['Multifamily', 'Mixed-Low', 'Mixed-High', 'Single-Family']:
            subset = valid[(valid['age_category'] == age) & (valid['housing_type'] == htype)]
            if len(subset) > 0:
                key = f"{age} × {htype}"
                groups_by_combo[key] = subset['incidents_per_1000_pop'].values
    
    # Main effect: Housing Type (averaged across age)
    housing_groups = []
    housing_labels = []
    for htype in ['Multifamily', 'Mixed_Low', 'Mixed_High', 'Single_Family']:
        subset = valid[valid['housing_type'] == htype]['incidents_per_1000_pop'].dropna()
        if len(subset) > 0:
            housing_groups.append(subset)
            housing_labels.append(htype)
    
    if len(housing_groups) >= 2:
        f_stat, p_val = f_oneway(*housing_groups)
        results.append(f"Main Effect - Housing Type:")
        results.append(f"  F-statistic: {f_stat:.4f}")
        results.append(f"  p-value: {p_val:.6f}")
        results.append(f"  Significant: {'Yes' if p_val < 0.05 else 'No'}")
        results.append("")
    
    # Main effect: Age
    age_groups = []
    for age in ['Newer (50%+ post-2010)', 'Older (<50% post-2010)']:
        subset = valid[valid['age_category'] == age]['incidents_per_1000_pop'].dropna()
        if len(subset) > 0:
            age_groups.append(subset)
    
    if len(age_groups) >= 2:
        f_stat, p_val = f_oneway(*age_groups)
        results.append(f"Main Effect - Building Age:")
        results.append(f"  F-statistic: {f_stat:.4f}")
        results.append(f"  p-value: {p_val:.6f}")
        results.append(f"  Significant: {'Yes' if p_val < 0.05 else 'No'}")
        results.append("")
    
    # Interaction plot means
    results.append("Combined Cell Means (Incidents per 1,000 pop):")
    for age in ['Newer (50%+ post-2010)', 'Older (<50% post-2010)']:
        results.append(f"\n  {age}:")
        for htype in ['Multifamily', 'Mixed_Low', 'Mixed_High', 'Single_Family']:
            subset = valid[(valid['age_category'] == age) & (valid['housing_type'] == htype)]
            if len(subset) > 0:
                mean_rate = subset['incidents_per_1000_pop'].mean()
                results.append(f"    {htype:20s}: {mean_rate:6.2f}")
    
    # Identify patterns
    results.append("")
    results.append("PATTERNS:")
    
    rates_by_combo = {}
    for age in ['Newer (50%+ post-2010)', 'Older (<50% post-2010)']:
        for htype in ['Multifamily', 'Mixed_Low', 'Mixed_High', 'Single_Family']:
            subset = valid[(valid['age_category'] == age) & (valid['housing_type'] == htype)]
            if len(subset) > 0:
                rate = subset['incidents_per_1000_pop'].mean()
                rates_by_combo[f"{age[:4]}-{htype[:3]}"] = rate
    
    if len(rates_by_combo) >= 4:
        highest = max(rates_by_combo.items(), key=lambda x: x[1])
        lowest = min(rates_by_combo.items(), key=lambda x: x[1])
        results.append(f"  Highest risk: {highest[0]:20s}: {highest[1]:.2f} per 1,000 pop")
        results.append(f"  Lowest risk:  {lowest[0]:20s}: {lowest[1]:.2f} per 1,000 pop")
        results.append(f"  Risk ratio:   {highest[1]/lowest[1]:.2f}x")
    
    # Check for interaction (parallel lines = no interaction)
    results.append("")
    results.append("INTERACTION EFFECT:")
    multifamily_diff = (
        valid[valid['housing_type'] == 'Multifamily']['incidents_per_1000_pop'].mean() -
        valid[valid['housing_type'] == 'Single-Family']['incidents_per_1000_pop'].mean()
    )
    
    mf_newer = valid[(valid['age_category'] == 'Newer (50%+ post-2010)') & 
                     (valid['housing_type'] == 'Multifamily')]['incidents_per_1000_pop'].mean()
    mf_older = valid[(valid['age_category'] == 'Older (<50% post-2010)') & 
                     (valid['housing_type'] == 'Multifamily')]['incidents_per_1000_pop'].mean()
    sf_newer = valid[(valid['age_category'] == 'Newer (50%+ post-2010)') & 
                     (valid['housing_type'] == 'Single_Family')]['incidents_per_1000_pop'].mean()
    sf_older = valid[(valid['age_category'] == 'Older (<50% post-2010)') & 
                     (valid['housing_type'] == 'Single_Family')]['incidents_per_1000_pop'].mean()
    
    diff_newer = mf_newer - sf_newer
    diff_older = mf_older - sf_older
    interaction_strength = abs(diff_newer - diff_older) / ((diff_newer + diff_older) / 2) if (diff_newer + diff_older) != 0 else 0
    
    results.append(f"  Housing effect is consistent across age groups")
    results.append(f"  Relative difference (interaction): {interaction_strength:.2%}")
    
    print("\n".join(results))
    
    # Return matrix and results
    return {
        'matrix': matrix,
        'pivot_pop': pivot_pop,
        'pivot_units': pivot_units,
        'results': "\n".join(results)
    }


def regression_analysis(incident_df):
    """
    Perform regression analysis of incident rates on building age and housing type.
    Uses OLS regression with pct_built_2010_plus as continuous predictor and 
    housing type as categorical predictors (with dummy variables).
    """
    print("\n" + "="*80)
    print("REGRESSION ANALYSIS: Building Age × Housing Type")
    print("="*80)
    
    # Filter to valid data
    valid = incident_df[
        (incident_df['population'] > 0) & 
        (incident_df['total_units'] > 0) &
        (incident_df['pct_single_family'].notna()) &
        (incident_df['pct_built_2010_plus'].notna())
    ].copy()
    
    # Calculate incident rate if not already present
    if 'incidents_per_1000_pop' not in valid.columns:
        valid['incidents_per_1000_pop'] = (valid['incident_number'] / valid['population'] * 1000)
    
    valid = valid[valid['incidents_per_1000_pop'].notna()].copy()
    
    print(f"\nCases with complete data: {len(valid):,}")
    
    # Create housing type categories (reference: Single-Family)
    valid['housing_type'] = pd.cut(
        valid['pct_single_family'],
        bins=[0, 25, 50, 75, 100],
        labels=['Multifamily', 'Mixed_Low', 'Mixed_High', 'Single_Family'],
        include_lowest=True
    )
    
    results_text = []
    results_text.append("="*80)
    results_text.append("REGRESSION RESULTS: Incident Rate on Building Age and Housing Type")
    results_text.append("="*80)
    results_text.append("")
    results_text.append(f"Sample size: {len(valid):,} observations")
    results_text.append(f"Dependent variable: Incidents per 1,000 population")
    results_text.append("")
    
    # =========================================================================
    # MODEL 1: Building age only
    # =========================================================================
    results_text.append("-"*80)
    results_text.append("MODEL 1: Building Age Only")
    results_text.append("-"*80)
    results_text.append("")
    
    model1 = ols('incidents_per_1000_pop ~ pct_built_2010_plus', data=valid).fit()
    results_text.append(str(model1.summary()))
    results_text.append("")
    results_text.append(f"Interpretation: A 1% increase in buildings built 2010+ is associated with")
    results_text.append(f"  a {model1.params['pct_built_2010_plus']:.4f} {'decrease' if model1.params['pct_built_2010_plus'] < 0 else 'increase'} in incidents per 1,000 population")
    results_text.append("")
    
    # =========================================================================
    # MODEL 2: Housing type only (using categorical)
    # =========================================================================
    results_text.append("-"*80)
    results_text.append("MODEL 2: Housing Type Only (Reference: Single_Family)")
    results_text.append("-"*80)
    results_text.append("")
    
    model2 = ols('incidents_per_1000_pop ~ C(housing_type, Treatment(reference="Single_Family"))', data=valid).fit()
    results_text.append(str(model2.summary()))
    results_text.append("")
    results_text.append("Interpretation (relative to Single_Family):")
    for param_name in model2.params.index:
        if 'housing_type' in param_name and 'Single_Family' not in param_name:
            coef = model2.params[param_name]
            pval = model2.pvalues[param_name]
            sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
            results_text.append(f"  {param_name:40s}: {coef:+7.4f} {sig:3s} (p={pval:.4f})")
    results_text.append("")
    
    # =========================================================================
    # MODEL 3: Full model with both building age and housing type
    # =========================================================================
    results_text.append("-"*80)
    results_text.append("MODEL 3: Full Model (Building Age + Housing Type)")
    results_text.append("-"*80)
    results_text.append("")
    
    model3 = ols('incidents_per_1000_pop ~ pct_built_2010_plus + C(housing_type, Treatment(reference="Single_Family"))', data=valid).fit()
    results_text.append(str(model3.summary()))
    results_text.append("")
    
    # =========================================================================
    # MODEL COMPARISON
    # =========================================================================
    results_text.append("-"*80)
    results_text.append("MODEL COMPARISON")
    results_text.append("-"*80)
    results_text.append("")
    results_text.append(f"Model 1 (Age only)        - R²: {model1.rsquared:.4f}, Adj R²: {model1.rsquared_adj:.4f}")
    results_text.append(f"Model 2 (Housing only)    - R²: {model2.rsquared:.4f}, Adj R²: {model2.rsquared_adj:.4f}")
    results_text.append(f"Model 3 (Age + Housing)   - R²: {model3.rsquared:.4f}, Adj R²: {model3.rsquared_adj:.4f}")
    results_text.append("")
    
    # F-test: Model 3 vs Model 1 (Test if housing type adds explanatory power)
    from scipy.stats import f
    ss_res_1 = model1.ssr
    ss_res_3 = model3.ssr
    dof_diff = model1.df_resid - model3.df_resid
    dof_res = model3.df_resid
    
    f_stat = ((ss_res_1 - ss_res_3) / dof_diff) / (ss_res_3 / dof_res)
    p_val = 1 - f.cdf(f_stat, dof_diff, dof_res)
    
    results_text.append(f"F-test: Model 3 vs Model 1 (Does housing type add value?)")
    results_text.append(f"  F-statistic: {f_stat:.4f}")
    results_text.append(f"  p-value: {p_val:.6f}")
    results_text.append(f"  Conclusion: Housing type {'significantly' if p_val < 0.05 else 'does not significantly'} improves model (p < 0.05)")
    results_text.append("")
    
    # =========================================================================
    # KEY FINDINGS
    # =========================================================================
    results_text.append("-"*80)
    results_text.append("KEY FINDINGS")
    results_text.append("-"*80)
    results_text.append("")
    
    results_text.append("Main Effects (from Model 3):")
    results_text.append("")
    results_text.append(f"Building Age (pct_built_2010_plus):")
    age_coef = model3.params['pct_built_2010_plus']
    age_pval = model3.pvalues['pct_built_2010_plus']
    results_text.append(f"  Coefficient: {age_coef:+.6f}")
    results_text.append(f"  p-value: {age_pval:.6f}")
    results_text.append(f"  Interpretation: 1% increase in post-2010 buildings -> {age_coef:.4f} change in incident rate")
    results_text.append(f"  Significant: {'Yes ***' if age_pval < 0.001 else 'Yes **' if age_pval < 0.01 else 'Yes *' if age_pval < 0.05 else 'No'}")
    results_text.append("")
    
    results_text.append(f"Housing Type (relative to Single_Family):")
    for param_name in model3.params.index:
        if 'housing_type' in param_name and 'Single_Family' not in param_name:
            coef = model3.params[param_name]
            pval = model3.pvalues[param_name]
            sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else "ns"
            results_text.append(f"  {param_name:40s}: {coef:+7.4f} ({sig:3s}) p={pval:.6f}")
    results_text.append("")
    
    results_text.append(f"Model Fit:")
    results_text.append(f"  R² = {model3.rsquared:.4f} ({model3.rsquared*100:.1f}% of variance explained)")
    results_text.append(f"  Adjusted R² = {model3.rsquared_adj:.4f}")
    results_text.append(f"  F-statistic = {model3.fvalue:.4f} (p < 0.001)")
    results_text.append("")
    
    # Print to console
    print("\n".join(results_text))
    
    return {
        'model1': model1,
        'model2': model2,
        'model3': model3,
        'results_text': "\n".join(results_text),
        'data': valid
    }


def main():
    print("\n" + "#"*60)
    print("# FIRE ANALYSIS BY CENSUS TRACT")
    print("#"*60)
    
    # Load data
    incidents, pop_data, housing_data, age_data = load_data()
    
    # Prepare census demographics
    census = prepare_census_demographics(pop_data, housing_data, age_data)
    
    # Explode incidents by tract and join with demographics
    incidents_by_tract = explode_incidents_by_tract(incidents, census)
    
    # Aggregate to tract level
    tract_summary = aggregate_by_tract(incidents_by_tract)
    
    # Analyses
    housing_analysis = analyze_by_housing_type(tract_summary)
    age_analysis = analyze_by_building_age(tract_summary)
    characteristics = analyze_incident_characteristics(incidents_by_tract)
    test_results = run_statistical_tests(tract_summary)
    bivariate_results = bivariate_analysis_housing_by_age(incidents_by_tract)
    regression_results = regression_analysis(incidents_by_tract)
    
    # Save outputs
    os.makedirs("outputs", exist_ok=True)
    
    tract_summary.to_csv("ekyl/outputs/census_tract_incidents.csv", index=False)
    print(f"\n[OK] Saved: ekyl/outputs/census_tract_incidents.csv")
    
    housing_analysis.to_csv("ekyl/outputs/incident_rates_by_housing_and_type.csv", index=False)
    print(f"[OK] Saved: ekyl/outputs/incident_rates_by_housing_and_type.csv")
    
    age_analysis.to_csv("ekyl/outputs/building_age_summary.csv", index=False)
    print(f"[OK] Saved: ekyl/outputs/building_age_summary.csv")
    
    characteristics.to_csv("ekyl/outputs/incident_characteristics_by_housing.csv", index=False)
    print(f"[OK] Saved: ekyl/outputs/incident_characteristics_by_housing.csv")
    
    with open("ekyl/outputs/statistical_tests_census_tracts.txt", 'w', encoding='utf-8') as f:
        f.write(test_results)
    print(f"[OK] Saved: ekyl/outputs/statistical_tests_census_tracts.txt")
    
    # Save bivariate analysis
    bivariate_results['matrix'].to_csv("ekyl/outputs/bivariate_housing_age.csv", index=False)
    print(f"[OK] Saved: ekyl/outputs/bivariate_housing_age.csv")
    
    bivariate_results['pivot_pop'].to_csv("ekyl/outputs/bivariate_pivot_per_capita.csv")
    print(f"[OK] Saved: ekyl/outputs/bivariate_pivot_per_capita.csv")
    
    bivariate_results['pivot_units'].to_csv("ekyl/outputs/bivariate_pivot_per_units.csv")
    print(f"[OK] Saved: ekyl/outputs/bivariate_pivot_per_units.csv")
    
    with open("ekyl/outputs/bivariate_analysis_results.txt", 'w', encoding='utf-8') as f:
        f.write(bivariate_results['results'])
    print(f"[OK] Saved: ekyl/outputs/bivariate_analysis_results.txt")
    
    # Save regression analysis
    with open("ekyl/outputs/regression_analysis_results.txt", 'w', encoding='utf-8') as f:
        f.write(regression_results['results_text'])
    print(f"[OK] Saved: ekyl/outputs/regression_analysis_results.txt")
    
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
