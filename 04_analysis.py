#!/usr/bin/env python3
"""
Step 4: Main Analysis
======================
Joins incident data with response area demographics and calculates
per-capita fire incident rates by urban classification and housing typology.

Usage:
    python scripts/04_analysis.py

Input:
    processed_data/incidents_clean.csv
    processed_data/response_areas_with_demographics.geojson

Output:
    processed_data/incidents_with_demographics.csv
    processed_data/response_areas_final.geojson
    outputs/summary_by_urban_class.csv
    outputs/summary_by_housing_type.csv
    outputs/summary_by_incident_type.csv
    outputs/summary_by_building_age.csv
    outputs/time_series_analysis.csv
    outputs/station_coverage.csv
    outputs/statistical_tests.txt
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')


def load_data():
    """Load incident and response area data"""
    print("\nLoading data...")
    
    incidents = pd.read_csv("processed_data/incidents_clean.csv")
    print(f"  Incidents: {len(incidents):,}")
    
    response_areas = gpd.read_file("processed_data/response_areas_with_demographics.geojson")
    print(f"  Response areas: {len(response_areas)}")
    
    return incidents, response_areas


def join_incidents_to_response_areas(incidents_df, response_areas_gdf):
    """
    Join incidents to response areas.
    Use the responsearea field from incident data if available,
    otherwise do spatial join.
    """
    print("\nJoining incidents to response areas...")
    
    # Find the response area column in incidents
    ra_col = None
    for col in incidents_df.columns:
        if 'responsearea' in col.lower() or 'response_area' in col.lower():
            ra_col = col
            break
    
    # Find the response area ID in the GeoDataFrame
    ra_id_col = 'response_area_id'
    if ra_id_col not in response_areas_gdf.columns:
        # Try to find it
        for col in response_areas_gdf.columns:
            if 'response' in col.lower() or 'area' in col.lower():
                ra_id_col = col
                break
    
    if ra_col:
        print(f"  Using responsearea field from incident data: {ra_col}")
        incidents_df['response_area_id'] = incidents_df[ra_col]
        
        # Check match rate
        ra_ids_in_geo = set(response_areas_gdf[ra_id_col].astype(str).unique())
        incident_ra_ids = set(incidents_df['response_area_id'].astype(str).unique())
        matches = len(ra_ids_in_geo & incident_ra_ids)
        print(f"  Response areas in incidents: {len(incident_ra_ids)}")
        print(f"  Response areas in boundaries: {len(ra_ids_in_geo)}")
        print(f"  Matching: {matches}")
        
        # Standardize the ID format for joining
        incidents_df['response_area_id'] = incidents_df['response_area_id'].astype(str)
        response_areas_gdf['response_area_id'] = response_areas_gdf[ra_id_col].astype(str)
    else:
        print("  No responsearea field found, performing spatial join...")
        # Create GeoDataFrame from incidents
        valid_coords = incidents_df['latitude'].notna() & incidents_df['longitude'].notna()
        incidents_geo = gpd.GeoDataFrame(
            incidents_df[valid_coords],
            geometry=gpd.points_from_xy(
                incidents_df.loc[valid_coords, 'longitude'],
                incidents_df.loc[valid_coords, 'latitude']
            ),
            crs="EPSG:4326"
        )
        
        # Spatial join
        incidents_joined = gpd.sjoin(incidents_geo, response_areas_gdf, how='left', predicate='within')
        incidents_df = pd.DataFrame(incidents_joined.drop(columns='geometry'))
    
    return incidents_df


def aggregate_incidents_by_response_area(incidents_df):
    """
    Count incidents by response area and category.
    """
    print("\nAggregating incidents by response area...")
    
    # Total incidents
    total_counts = incidents_df.groupby('response_area_id').size().reset_index(name='total_incidents')
    
    # Structure fires
    if 'is_structure_fire' in incidents_df.columns:
        structure_counts = incidents_df.groupby('response_area_id')['is_structure_fire'].sum().reset_index()
        structure_counts.columns = ['response_area_id', 'structure_fires']
        total_counts = total_counts.merge(structure_counts, on='response_area_id', how='left')
    
    # Vehicle fires
    if 'is_vehicle_fire' in incidents_df.columns:
        vehicle_counts = incidents_df.groupby('response_area_id')['is_vehicle_fire'].sum().reset_index()
        vehicle_counts.columns = ['response_area_id', 'vehicle_fires']
        total_counts = total_counts.merge(vehicle_counts, on='response_area_id', how='left')
    
    # Outdoor fires
    if 'is_outdoor_fire' in incidents_df.columns:
        outdoor_counts = incidents_df.groupby('response_area_id')['is_outdoor_fire'].sum().reset_index()
        outdoor_counts.columns = ['response_area_id', 'outdoor_fires']
        total_counts = total_counts.merge(outdoor_counts, on='response_area_id', how='left')
    
    # By year (for annualized rates)
    year_col = None
    for col in incidents_df.columns:
        if 'year' in col.lower():
            year_col = col
            break
    
    if year_col:
        years = incidents_df[year_col].nunique()
        total_counts['years_of_data'] = years
        print(f"  Data spans {years} years")
    
    print(f"  Aggregated to {len(total_counts)} response areas")
    
    return total_counts


def merge_incidents_with_demographics(incident_counts_df, response_areas_gdf):
    """
    Merge incident counts with response area demographics.
    """
    print("\nMerging incidents with demographics...")
    
    # Ensure ID columns are same type
    incident_counts_df['response_area_id'] = incident_counts_df['response_area_id'].astype(str)
    response_areas_gdf['response_area_id'] = response_areas_gdf['response_area_id'].astype(str)
    
    # Merge
    merged = response_areas_gdf.merge(incident_counts_df, on='response_area_id', how='left')
    
    # Fill NaN incident counts with 0
    incident_cols = ['total_incidents', 'structure_fires', 'vehicle_fires', 'outdoor_fires']
    for col in incident_cols:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)
    
    # Calculate per-capita rates (per 1,000 population)
    if 'population' in merged.columns:
        merged['incidents_per_1000_pop'] = np.where(
            merged['population'] > 0,
            (merged['total_incidents'] / merged['population']) * 1000,
            np.nan
        )
        if 'structure_fires' in merged.columns:
            merged['structure_fires_per_1000_pop'] = np.where(
                merged['population'] > 0,
                (merged['structure_fires'] / merged['population']) * 1000,
                np.nan
            )
    
    # Calculate per-housing-unit rates (per 1,000 units)
    if 'total_units' in merged.columns:
        merged['incidents_per_1000_units'] = np.where(
            merged['total_units'] > 0,
            (merged['total_incidents'] / merged['total_units']) * 1000,
            np.nan
        )
        if 'structure_fires' in merged.columns:
            merged['structure_fires_per_1000_units'] = np.where(
                merged['total_units'] > 0,
                (merged['structure_fires'] / merged['total_units']) * 1000,
                np.nan
            )
    
    # Annualize if we have years
    if 'years_of_data' in merged.columns:
        years = merged['years_of_data'].iloc[0]
        merged['annual_incidents_per_1000_pop'] = merged['incidents_per_1000_pop'] / years
        merged['annual_incidents_per_1000_units'] = merged['incidents_per_1000_units'] / years
    
    print(f"  Merged dataset: {len(merged)} response areas")
    
    return merged


def analyze_by_urban_class(merged_gdf):
    """
    Calculate summary statistics by urban classification.
    """
    print("\nAnalyzing by urban classification...")
    
    # Filter to valid data
    valid = merged_gdf[
        (merged_gdf['population'] > 0) & 
        (merged_gdf['urban_class'] != 'unknown')
    ].copy()
    
    # Aggregate
    summary = valid.groupby('urban_class').agg({
        'population': 'sum',
        'total_units': 'sum',
        'single_family': 'sum',
        'multifamily': 'sum',
        'total_incidents': 'sum',
        'structure_fires': 'sum',
        'area_sq_miles': 'sum',
        'response_area_id': 'count'  # Count of response areas
    }).reset_index()
    
    summary.columns = ['urban_class', 'population', 'total_units', 'single_family',
                       'multifamily', 'total_incidents', 'structure_fires', 
                       'area_sq_miles', 'num_response_areas']
    
    # Calculate rates
    summary['incidents_per_1000_pop'] = (summary['total_incidents'] / summary['population']) * 1000
    summary['incidents_per_1000_units'] = (summary['total_incidents'] / summary['total_units']) * 1000
    summary['structure_fires_per_1000_units'] = (summary['structure_fires'] / summary['total_units']) * 1000
    summary['pop_density'] = summary['population'] / summary['area_sq_miles']
    summary['pct_single_family'] = summary['single_family'] / summary['total_units'] * 100
    
    # Annualize if we have years data
    if 'years_of_data' in merged_gdf.columns:
        years = merged_gdf['years_of_data'].iloc[0]
        summary['annual_incidents_per_1000_pop'] = summary['incidents_per_1000_pop'] / years
        summary['annual_incidents_per_1000_units'] = summary['incidents_per_1000_units'] / years
    
    # Reorder
    order = ['urban_core', 'inner_suburban', 'outer_suburban']
    summary['urban_class'] = pd.Categorical(summary['urban_class'], categories=order, ordered=True)
    summary = summary.sort_values('urban_class')
    
    print("\n" + "="*80)
    print("SUMMARY BY URBAN CLASSIFICATION")
    print("="*80)
    print(summary.to_string(index=False))
    
    return summary


def analyze_by_housing_type(merged_gdf):
    """
    Analyze incident rates by housing typology (% single-family).
    """
    print("\nAnalyzing by housing typology...")
    
    # Filter to valid data
    valid = merged_gdf[
        (merged_gdf['population'] > 0) & 
        (merged_gdf['total_units'] > 0) &
        (merged_gdf['pct_single_family'].notna())
    ].copy()
    
    # Create bins
    valid['sf_category'] = pd.cut(
        valid['pct_single_family'],
        bins=[0, 25, 50, 75, 100],
        labels=['<25% SF', '25-50% SF', '50-75% SF', '>75% SF'],
        include_lowest=True
    )
    
    # Aggregate
    summary = valid.groupby('sf_category').agg({
        'population': 'sum',
        'total_units': 'sum',
        'total_incidents': 'sum',
        'structure_fires': 'sum',
        'response_area_id': 'count'
    }).reset_index()
    
    summary.columns = ['sf_category', 'population', 'total_units', 'total_incidents',
                       'structure_fires', 'num_response_areas']
    
    # Calculate rates
    summary['incidents_per_1000_pop'] = (summary['total_incidents'] / summary['population']) * 1000
    summary['incidents_per_1000_units'] = (summary['total_incidents'] / summary['total_units']) * 1000
    summary['structure_fires_per_1000_units'] = (summary['structure_fires'] / summary['total_units']) * 1000
    
    print("\n" + "="*80)
    print("SUMMARY BY HOUSING TYPOLOGY")
    print("="*80)
    print(summary.to_string(index=False))
    
    return summary


def run_statistical_tests(merged_gdf):
    """
    Run statistical tests to assess significance of differences.
    """
    print("\nRunning statistical tests...")
    
    results = []
    
    # Filter to valid data
    valid = merged_gdf[
        (merged_gdf['population'] > 100) &  # Exclude very small areas
        (merged_gdf['urban_class'] != 'unknown') &
        (merged_gdf['incidents_per_1000_pop'].notna())
    ].copy()
    
    # T-test: Suburban vs Urban
    urban = valid[valid['urban_class'] == 'urban_core']['incidents_per_1000_pop']
    suburban = valid[valid['urban_class'] == 'inner_suburban']['incidents_per_1000_pop']
    exurban = valid[valid['urban_class'] == 'outer_suburban']['incidents_per_1000_pop']
    
    if len(urban) > 0 and len(suburban) > 0:
        t_stat, p_value = stats.ttest_ind(suburban, urban, equal_var=False)
        results.append(f"T-test: Inner Suburban vs Urban Core")
        results.append(f"  Urban mean: {urban.mean():.2f} incidents per 1,000 pop")
        results.append(f"  Suburban mean: {suburban.mean():.2f} incidents per 1,000 pop")
        results.append(f"  t-statistic: {t_stat:.3f}")
        results.append(f"  p-value: {p_value:.4f}")
        results.append(f"  Significant at α=0.05: {'Yes' if p_value < 0.05 else 'No'}")
        results.append("")
    
    if len(exurban) > 0 and len(urban) > 0:
        t_stat, p_value = stats.ttest_ind(exurban, urban, equal_var=False)
        results.append(f"T-test: Outer Suburban vs Urban Core")
        results.append(f"  Urban mean: {urban.mean():.2f}")
        results.append(f"  Outer Suburban mean: {exurban.mean():.2f}")
        results.append(f"  t-statistic: {t_stat:.3f}")
        results.append(f"  p-value: {p_value:.4f}")
        results.append(f"  Significant at α=0.05: {'Yes' if p_value < 0.05 else 'No'}")
        results.append("")
    
    # ANOVA across all groups
    groups = [urban, suburban, exurban]
    groups = [g for g in groups if len(g) > 0]
    
    if len(groups) >= 2:
        f_stat, p_value = stats.f_oneway(*groups)
        results.append(f"ANOVA: All Urban Classifications")
        results.append(f"  F-statistic: {f_stat:.3f}")
        results.append(f"  p-value: {p_value:.4f}")
        results.append(f"  Significant at α=0.05: {'Yes' if p_value < 0.05 else 'No'}")
        results.append("")
    
    # Correlation: % Single-Family vs Incident Rate
    if 'pct_single_family' in valid.columns:
        corr, p_value = stats.pearsonr(
            valid['pct_single_family'].dropna(),
            valid.loc[valid['pct_single_family'].notna(), 'incidents_per_1000_pop']
        )
        results.append(f"Correlation: % Single-Family vs Incident Rate")
        results.append(f"  Pearson r: {corr:.3f}")
        results.append(f"  p-value: {p_value:.4f}")
        results.append(f"  Interpretation: {'Positive' if corr > 0 else 'Negative'} correlation")
        results.append("")
    
    # Print results
    print("\n" + "="*80)
    print("STATISTICAL TESTS")
    print("="*80)
    for line in results:
        print(line)
    
    return "\n".join(results)


def analyze_by_incident_type(incidents_df, merged_gdf):
    """
    Analyze incident rates by type (structure, vehicle, outdoor, trash, other)
    cross-tabulated with urban classification.
    """
    print("\nAnalyzing by incident type...")

    # Get year column for annualization
    year_col = None
    for col in incidents_df.columns:
        if 'year' in col.lower():
            year_col = col
            break

    years = incidents_df[year_col].nunique() if year_col else 1

    # Count incidents by type and response area
    incidents_df['response_area_id'] = incidents_df['response_area_id'].astype(str)

    type_counts = incidents_df.groupby('response_area_id').agg({
        'is_structure_fire': 'sum',
        'is_vehicle_fire': 'sum',
        'is_outdoor_fire': 'sum',
        'is_trash_fire': 'sum'
    }).reset_index()

    type_counts['other_fires'] = (
        incidents_df.groupby('response_area_id').size().values -
        type_counts['is_structure_fire'] - type_counts['is_vehicle_fire'] -
        type_counts['is_outdoor_fire'] - type_counts['is_trash_fire']
    )

    type_counts.columns = ['response_area_id', 'structure', 'vehicle', 'outdoor', 'trash', 'other']

    # Merge with demographics
    merged_gdf['response_area_id'] = merged_gdf['response_area_id'].astype(str)
    df = merged_gdf[['response_area_id', 'population', 'urban_class']].merge(
        type_counts, on='response_area_id', how='left'
    )
    df = df.fillna(0)

    # Filter to valid data
    valid = df[(df['population'] > 0) & (df['urban_class'] != 'unknown')].copy()

    # Aggregate by urban class
    summary = valid.groupby('urban_class').agg({
        'population': 'sum',
        'structure': 'sum',
        'vehicle': 'sum',
        'outdoor': 'sum',
        'trash': 'sum',
        'other': 'sum'
    }).reset_index()

    # Calculate rates per 1,000 population
    for col in ['structure', 'vehicle', 'outdoor', 'trash', 'other']:
        summary[f'{col}_per_1000'] = (summary[col] / summary['population']) * 1000
        summary[f'{col}_annual_per_1000'] = summary[f'{col}_per_1000'] / years

    # Reorder
    order = ['urban_core', 'inner_suburban', 'outer_suburban']
    summary['urban_class'] = pd.Categorical(summary['urban_class'], categories=order, ordered=True)
    summary = summary.sort_values('urban_class')

    print("\n" + "="*80)
    print("SUMMARY BY INCIDENT TYPE")
    print("="*80)
    rate_cols = ['urban_class', 'population', 'structure_per_1000', 'vehicle_per_1000',
                 'outdoor_per_1000', 'trash_per_1000', 'other_per_1000']
    print(summary[rate_cols].to_string(index=False))

    return summary


def analyze_by_building_age(merged_gdf):
    """
    Analyze incident rates by building age (pre-1970, 1970-2009, 2010+)
    cross-tabulated with urban classification (2x2 matrix).
    """
    print("\nAnalyzing by building age...")

    # Check if building age data exists
    if 'pct_built_2010_plus' not in merged_gdf.columns:
        print("  Warning: Building age data not available")
        return None

    # Filter to valid data
    valid = merged_gdf[
        (merged_gdf['population'] > 0) &
        (merged_gdf['urban_class'] != 'unknown') &
        (merged_gdf['pct_built_2010_plus'].notna())
    ].copy()

    # Classify areas by dominant building age
    # "Newer" = >50% built 2010+, "Older" = <=50% built 2010+
    valid['building_age_class'] = np.where(
        valid['pct_built_2010_plus'] >= 50, 'Newer (50%+ post-2010)', 'Older (<50% post-2010)'
    )

    # Create combined urban × building age category
    valid['urban_age_combo'] = valid['urban_class'] + ' / ' + valid['building_age_class']

    # Aggregate by building age class
    summary_age = valid.groupby('building_age_class').agg({
        'population': 'sum',
        'total_units': 'sum',
        'total_incidents': 'sum',
        'structure_fires': 'sum',
        'response_area_id': 'count'
    }).reset_index()

    summary_age.columns = ['building_age', 'population', 'total_units', 'total_incidents',
                           'structure_fires', 'num_areas']
    summary_age['incidents_per_1000_pop'] = (summary_age['total_incidents'] / summary_age['population']) * 1000
    summary_age['structure_per_1000_units'] = (summary_age['structure_fires'] / summary_age['total_units']) * 1000

    # 2x2 Matrix: Urban/Suburban × Old/New
    # Simplify urban class to just urban vs suburban
    valid['urban_simple'] = np.where(
        valid['urban_class'] == 'urban_core', 'Urban Core',
        np.where(valid['urban_class'] == 'inner_suburban', 'Inner Suburban', 'Outer Suburban')
    )

    matrix = valid.groupby(['urban_simple', 'building_age_class']).agg({
        'population': 'sum',
        'total_incidents': 'sum',
        'structure_fires': 'sum'
    }).reset_index()

    matrix['incidents_per_1000'] = (matrix['total_incidents'] / matrix['population']) * 1000

    print("\n" + "="*80)
    print("SUMMARY BY BUILDING AGE")
    print("="*80)
    print(summary_age.to_string(index=False))

    print("\n" + "-"*40)
    print("2x2 MATRIX: Urban Class × Building Age")
    print("-"*40)
    pivot = matrix.pivot(index='urban_simple', columns='building_age_class', values='incidents_per_1000')
    print(pivot.to_string())

    return summary_age, matrix


def analyze_time_series(incidents_df, merged_gdf):
    """
    Analyze incident trends over time (2018-2024).
    """
    print("\nAnalyzing time series...")

    # Find year column
    year_col = None
    for col in incidents_df.columns:
        if 'year' in col.lower() or 'calendaryear' in col.lower():
            year_col = col
            break

    if year_col is None:
        print("  Warning: Year column not found")
        return None

    # Get total population for rate calculation
    total_pop = merged_gdf[merged_gdf['population'] > 0]['population'].sum()

    # Count incidents by year
    yearly = incidents_df.groupby(year_col).size().reset_index(name='total_incidents')
    yearly.columns = ['year', 'total_incidents']

    # Count by incident type per year
    if 'is_structure_fire' in incidents_df.columns:
        yearly_type = incidents_df.groupby(year_col).agg({
            'is_structure_fire': 'sum',
            'is_vehicle_fire': 'sum',
            'is_outdoor_fire': 'sum'
        }).reset_index()
        yearly_type.columns = ['year', 'structure_fires', 'vehicle_fires', 'outdoor_fires']
        yearly = yearly.merge(yearly_type, on='year', how='left')

    # Calculate rates (per 1,000 population)
    yearly['incidents_per_1000'] = (yearly['total_incidents'] / total_pop) * 1000

    if 'structure_fires' in yearly.columns:
        yearly['structure_per_1000'] = (yearly['structure_fires'] / total_pop) * 1000

    # Sort by year
    yearly = yearly.sort_values('year')

    print("\n" + "="*80)
    print("TIME SERIES ANALYSIS")
    print("="*80)
    print(f"Population base for rates: {total_pop:,.0f}")
    print(f"\nNote: 2006 Austin sprinkler code change (effect visible in 2010+ buildings)")
    print()
    print(yearly.to_string(index=False))

    return yearly


def analyze_structure_fires_by_housing_trend(incidents_df, merged_gdf):
    """
    Analyze STRUCTURE FIRE trends by year and housing classification.
    Focuses only on housing-related fires, excluding vehicle, trash, outdoor fires.
    """
    print("\n" + "="*80)
    print("STRUCTURE FIRE TRENDS BY HOUSING CLASSIFICATION")
    print("="*80)

    # Find year column
    year_col = None
    for col in incidents_df.columns:
        if 'year' in col.lower() or 'calendaryear' in col.lower():
            year_col = col
            break

    if year_col is None:
        print("  Warning: Year column not found")
        return None

    # Filter to STRUCTURE FIRES ONLY
    structure_fires = incidents_df[incidents_df['is_structure_fire'] == True].copy()
    print(f"\nFiltering to structure fires only: {len(structure_fires):,} incidents")
    print(f"  (Excluded: {len(incidents_df) - len(structure_fires):,} non-structure incidents)")

    # Join with response area demographics
    structure_fires['response_area_id'] = structure_fires['response_area_id'].astype(str)
    merged_gdf['response_area_id'] = merged_gdf['response_area_id'].astype(str)

    # Get housing classification for each response area
    ra_housing = merged_gdf[['response_area_id', 'urban_class', 'pct_single_family',
                              'population', 'total_units']].copy()

    # Create housing typology categories
    ra_housing['housing_type'] = pd.cut(
        ra_housing['pct_single_family'],
        bins=[0, 25, 50, 75, 100],
        labels=['Multifamily (<25% SF)', 'Mixed-low (25-50% SF)',
                'Mixed-high (50-75% SF)', 'Single-family (>75% SF)'],
        include_lowest=True
    )

    # Merge structure fires with housing classification
    fires_with_housing = structure_fires.merge(
        ra_housing[['response_area_id', 'urban_class', 'housing_type', 'population', 'total_units']],
        on='response_area_id', how='left'
    )
    fires_with_housing = fires_with_housing[fires_with_housing['housing_type'].notna()]

    # --- TREND BY YEAR AND HOUSING TYPE ---
    trend_housing = fires_with_housing.groupby([year_col, 'housing_type']).size().reset_index(name='fires')
    trend_housing.columns = ['year', 'housing_type', 'fires']

    pop_by_housing = ra_housing.groupby('housing_type').agg({
        'population': 'sum', 'total_units': 'sum'
    }).reset_index()

    trend_housing = trend_housing.merge(pop_by_housing, on='housing_type', how='left')
    trend_housing['fires_per_1000_units'] = (trend_housing['fires'] / trend_housing['total_units']) * 1000

    pivot_rates = trend_housing.pivot(index='housing_type', columns='year', values='fires_per_1000_units').fillna(0)

    print("\nStructure Fires per 1,000 Housing Units by Type and Year:")
    print(pivot_rates.round(2).to_string())

    # --- TREND BY YEAR AND URBAN CLASS ---
    fires_urban = fires_with_housing[fires_with_housing['urban_class'].isin(
        ['urban_core', 'inner_suburban', 'outer_suburban'])]

    trend_urban = fires_urban.groupby([year_col, 'urban_class']).size().reset_index(name='fires')
    trend_urban.columns = ['year', 'urban_class', 'fires']

    pop_by_urban = merged_gdf[merged_gdf['urban_class'] != 'unknown'].groupby('urban_class').agg({
        'population': 'sum', 'total_units': 'sum'
    }).reset_index()

    trend_urban = trend_urban.merge(pop_by_urban, on='urban_class', how='left')
    trend_urban['fires_per_1000_units'] = (trend_urban['fires'] / trend_urban['total_units']) * 1000

    pivot_urban = trend_urban.pivot(index='urban_class', columns='year', values='fires_per_1000_units').fillna(0)
    pivot_urban = pivot_urban.reindex(['urban_core', 'inner_suburban', 'outer_suburban'])

    print("\nStructure Fires per 1,000 Housing Units by Urban Class and Year:")
    print(pivot_urban.round(2).to_string())

    return {'trend_by_housing': trend_housing, 'trend_by_urban': trend_urban,
            'pivot_housing_rates': pivot_rates, 'pivot_urban_rates': pivot_urban}


def analyze_station_coverage(merged_gdf):
    """
    Analyze fire station coverage by urban classification.
    """
    print("\nAnalyzing fire station coverage...")

    # Load fire stations
    import json
    stations_path = "raw_data/fire_stations.geojson"
    if not os.path.exists(stations_path):
        print("  Warning: Fire stations data not available")
        return None

    stations = gpd.read_file(stations_path)
    print(f"  Loaded {len(stations)} stations")

    # Filter to AFD stations only
    if 'DEPARTMENT' in stations.columns:
        afd_stations = stations[stations['DEPARTMENT'].str.upper().isin(['AFD', 'AUSTIN', 'AUSTIN FIRE'])]
        print(f"  AFD stations: {len(afd_stations)}")
    else:
        afd_stations = stations

    # Calculate stations per urban class
    # First, spatial join stations to response areas
    response_areas = merged_gdf.to_crs(stations.crs)
    stations_joined = gpd.sjoin(afd_stations, response_areas[['response_area_id', 'urban_class', 'geometry']],
                                 how='left', predicate='within')

    # Count stations by urban class
    station_counts = stations_joined.groupby('urban_class').size().reset_index(name='num_stations')

    # Get population by urban class
    pop_by_class = merged_gdf[merged_gdf['urban_class'] != 'unknown'].groupby('urban_class').agg({
        'population': 'sum',
        'area_sq_miles': 'sum'
    }).reset_index()

    # Merge
    coverage = pop_by_class.merge(station_counts, on='urban_class', how='left')
    coverage['num_stations'] = coverage['num_stations'].fillna(0)

    # Calculate coverage metrics
    coverage['pop_per_station'] = coverage['population'] / coverage['num_stations'].replace(0, np.nan)
    coverage['sq_miles_per_station'] = coverage['area_sq_miles'] / coverage['num_stations'].replace(0, np.nan)
    coverage['stations_per_100k'] = (coverage['num_stations'] / coverage['population']) * 100000

    print("\n" + "="*80)
    print("FIRE STATION COVERAGE BY URBAN CLASS")
    print("="*80)
    print(coverage.to_string(index=False))

    return coverage


def main():
    print("\n" + "#"*60)
    print("# FIRE RESOURCE ANALYSIS - MAIN ANALYSIS")
    print("#"*60)
    
    # Load data
    incidents, response_areas = load_data()
    
    # Join incidents to response areas
    incidents = join_incidents_to_response_areas(incidents, response_areas)
    
    # Aggregate incidents
    incident_counts = aggregate_incidents_by_response_area(incidents)
    
    # Merge with demographics
    merged = merge_incidents_with_demographics(incident_counts, response_areas)
    
    # Analysis - Original
    summary_urban = analyze_by_urban_class(merged)
    summary_housing = analyze_by_housing_type(merged)
    test_results = run_statistical_tests(merged)

    # Analysis - New (per Tim's feedback)
    summary_incident_type = analyze_by_incident_type(incidents, merged)
    building_age_results = analyze_by_building_age(merged)
    time_series = analyze_time_series(incidents, merged)
    station_coverage = analyze_station_coverage(merged)

    # Structure fire trends by housing classification
    structure_fire_trends = analyze_structure_fires_by_housing_trend(incidents, merged)

    # Save outputs
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("processed_data", exist_ok=True)

    summary_urban.to_csv("outputs/summary_by_urban_class.csv", index=False)
    print(f"\n✓ Saved: outputs/summary_by_urban_class.csv")

    summary_housing.to_csv("outputs/summary_by_housing_type.csv", index=False)
    print(f"✓ Saved: outputs/summary_by_housing_type.csv")

    summary_incident_type.to_csv("outputs/summary_by_incident_type.csv", index=False)
    print(f"✓ Saved: outputs/summary_by_incident_type.csv")

    if building_age_results is not None:
        summary_age, matrix = building_age_results
        summary_age.to_csv("outputs/summary_by_building_age.csv", index=False)
        matrix.to_csv("outputs/building_age_matrix.csv", index=False)
        print(f"✓ Saved: outputs/summary_by_building_age.csv")
        print(f"✓ Saved: outputs/building_age_matrix.csv")

    if time_series is not None:
        time_series.to_csv("outputs/time_series_analysis.csv", index=False)
        print(f"✓ Saved: outputs/time_series_analysis.csv")

    if station_coverage is not None:
        station_coverage.to_csv("outputs/station_coverage.csv", index=False)
        print(f"✓ Saved: outputs/station_coverage.csv")

    if structure_fire_trends is not None:
        structure_fire_trends['trend_by_housing'].to_csv("outputs/structure_fires_by_housing_trend.csv", index=False)
        structure_fire_trends['trend_by_urban'].to_csv("outputs/structure_fires_by_urban_trend.csv", index=False)
        structure_fire_trends['pivot_housing_rates'].to_csv("outputs/structure_fires_housing_pivot.csv")
        structure_fire_trends['pivot_urban_rates'].to_csv("outputs/structure_fires_urban_pivot.csv")
        print(f"✓ Saved: outputs/structure_fires_by_housing_trend.csv")
        print(f"✓ Saved: outputs/structure_fires_by_urban_trend.csv")
        print(f"✓ Saved: outputs/structure_fires_housing_pivot.csv")
        print(f"✓ Saved: outputs/structure_fires_urban_pivot.csv")

    with open("outputs/statistical_tests.txt", 'w') as f:
        f.write(test_results)
    print(f"✓ Saved: outputs/statistical_tests.txt")
    
    # Save final geodata
    merged.to_file("processed_data/response_areas_final.geojson", driver='GeoJSON')
    print(f"✓ Saved: processed_data/response_areas_final.geojson")
    
    # Save incidents with demographics for further analysis
    incidents.to_csv("processed_data/incidents_with_demographics.csv", index=False)
    print(f"✓ Saved: processed_data/incidents_with_demographics.csv")
    
    # Key findings
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)
    
    # Compare urban vs suburban rates
    if len(summary_urban) > 0:
        urban_rate = summary_urban[summary_urban['urban_class'] == 'urban_core']['incidents_per_1000_pop'].values
        suburban_rate = summary_urban[summary_urban['urban_class'] == 'inner_suburban']['incidents_per_1000_pop'].values
        exurban_rate = summary_urban[summary_urban['urban_class'] == 'outer_suburban']['incidents_per_1000_pop'].values
        
        if len(urban_rate) > 0 and len(suburban_rate) > 0:
            diff = ((suburban_rate[0] / urban_rate[0]) - 1) * 100
            print(f"\nInner suburban areas have {abs(diff):.1f}% {'MORE' if diff > 0 else 'FEWER'} "
                  f"fire incidents per capita than urban core areas.")
        
        if len(urban_rate) > 0 and len(exurban_rate) > 0:
            diff = ((exurban_rate[0] / urban_rate[0]) - 1) * 100
            print(f"Outer suburban areas have {abs(diff):.1f}% {'MORE' if diff > 0 else 'FEWER'} "
                  f"fire incidents per capita than urban core areas.")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Review outputs/summary_by_urban_class.csv
   - Do the findings support Tim's hypothesis?

2. Review outputs/statistical_tests.txt
   - Are the differences statistically significant?

3. Run visualization script:
   python scripts/05_visualize.py

4. Consider additional analysis:
   - Control for housing age
   - Control for income
   - Separate analysis for structure fires only
""")


if __name__ == "__main__":
    main()
