#!/usr/bin/env python3
"""
Step 6: NFIRS Cause Analysis
=============================
Analyzes fire causes and sprinkler effects by housing type using detailed NFIRS data.

Addresses the question: Why does multifamily have 4x higher structure fire rates?

Usage:
    python 06_nfirs_cause_analysis.py

Input:
    raw_data/nfirs/*/data/fireincident.txt
    raw_data/nfirs/*/data/basicincident.txt
    raw_data/nfirs/*/data/codelookup.txt

Output:
    processed_data/nfirs_austin_detailed.csv
    outputs/cause_by_housing_type.csv
    outputs/heat_source_by_housing.csv
    outputs/sprinkler_analysis.csv
    outputs/chart_cause_comparison.png
    outputs/chart_sprinkler_effect.png
"""

import pandas as pd
import numpy as np
import os
import glob
import warnings
warnings.filterwarnings('ignore')


# NFIRS Code Mappings
CAUSE_IGN_MAP = {
    '0': 'Other',
    '1': 'Intentional',
    '2': 'Unintentional',
    '3': 'Equipment failure',
    '4': 'Act of nature',
    '5': 'Under investigation',
    'U': 'Undetermined'
}

PROP_USE_CATEGORIES = {
    # Residential
    '419': 'Single-family',
    '429': 'Multifamily',
    '439': 'Boarding/rooming',
    '449': 'Hotel/motel',
    '459': 'Residential board and care',
    '460': 'Dormitory',
    '462': 'Sorority/fraternity',
    '464': 'Barracks',
    '400': 'Residential (general)',
}

HEAT_SOURCE_CATEGORIES = {
    # Cooking
    '12': 'Cooking - stove/range',
    '13': 'Cooking - oven',
    '14': 'Cooking - grill/hibachi',
    '15': 'Cooking - deep fryer',
    # Heating
    '10': 'Heating - general',
    '11': 'Heating - furnace/boiler',
    '12': 'Heating - fireplace',
    '13': 'Heating - space heater',
    # Electrical
    '40': 'Electrical - general',
    '41': 'Electrical - wiring',
    '42': 'Electrical - extension cord',
    '43': 'Electrical - appliance',
    '44': 'Electrical - lamp/light',
    # Smoking
    '61': 'Smoking - cigarette',
    '62': 'Smoking - pipe/cigar',
    '63': 'Smoking - match',
    # Open flame
    '64': 'Open flame - candle',
    '65': 'Open flame - lighter',
    '66': 'Open flame - match',
}

AREA_ORIGIN_CATEGORIES = {
    '21': 'Bedroom',
    '22': 'Living room',
    '23': 'Dining room',
    '24': 'Kitchen',
    '25': 'Bathroom',
    '26': 'Laundry',
    '27': 'Garage',
    '51': 'Mechanical room',
    '52': 'HVAC',
    '53': 'Electrical',
    '91': 'Exterior - wall',
    '92': 'Exterior - roof',
    '93': 'Exterior - balcony/porch',
}


def load_codelookup():
    """Load code lookup table from NFIRS data"""
    print("\nLoading code lookups...")

    lookup_files = glob.glob("raw_data/nfirs/*/data/codelookup.txt")
    if not lookup_files:
        print("  Warning: No codelookup.txt found")
        return {}

    # Use the first one (they should all be the same)
    df = pd.read_csv(lookup_files[0], sep='^', quotechar='"', dtype=str)
    df.columns = ['fieldid', 'code_value', 'code_descr']

    # Build lookup dictionary
    lookups = {}
    for field in df['fieldid'].unique():
        field_df = df[df['fieldid'] == field]
        lookups[field] = dict(zip(field_df['code_value'], field_df['code_descr']))

    print(f"  Loaded {len(lookups)} code tables")
    return lookups


def extract_austin_nfirs():
    """Extract Austin (WP801) fire incidents from national NFIRS data"""
    print("\nExtracting Austin NFIRS data...")

    # Find all fireincident files
    fire_files = glob.glob("raw_data/nfirs/*/data/fireincident.txt")
    basic_files = glob.glob("raw_data/nfirs/*/data/basicincident.txt")

    if not fire_files:
        print("  Error: No fireincident.txt files found")
        return None

    print(f"  Found {len(fire_files)} years of NFIRS data")

    # Load and filter fireincident data
    fire_dfs = []
    for f in fire_files:
        year = f.split('/')[2]  # Extract year from path
        print(f"  Processing fireincident {year}...")

        df = pd.read_csv(f, sep='^', quotechar='"', dtype=str, low_memory=False, encoding='latin-1')
        # Filter to Texas WP801 (Austin area)
        df_austin = df[(df['STATE'] == 'TX') & (df['FDID'] == 'WP801')]
        df_austin = df_austin.copy()
        df_austin['YEAR'] = year
        fire_dfs.append(df_austin)
        print(f"    Found {len(df_austin)} Austin fire incidents")

    fire_df = pd.concat(fire_dfs, ignore_index=True)
    print(f"  Total fireincident records: {len(fire_df)}")

    # Load and filter basicincident data
    basic_dfs = []
    for f in basic_files:
        year = f.split('/')[2]
        print(f"  Processing basicincident {year}...")

        df = pd.read_csv(f, sep='^', quotechar='"', dtype=str, low_memory=False, encoding='latin-1')
        df_austin = df[(df['STATE'] == 'TX') & (df['FDID'] == 'WP801')]
        df_austin = df_austin.copy()
        df_austin['YEAR'] = year
        basic_dfs.append(df_austin)
        print(f"    Found {len(df_austin)} Austin basic incidents")

    basic_df = pd.concat(basic_dfs, ignore_index=True)
    print(f"  Total basicincident records: {len(basic_df)}")

    # Join on incident key
    key_cols = ['STATE', 'FDID', 'INC_DATE', 'INC_NO', 'EXP_NO']

    # Select columns from fireincident
    fire_cols = key_cols + ['YEAR', 'AREA_ORIG', 'HEAT_SOURC', 'FIRST_IGN', 'CAUSE_IGN',
                           'FACT_IGN_1', 'HUM_FAC_1', 'EQUIP_INV', 'FIRE_SPRD',
                           'AES_PRES', 'AES_TYPE', 'AES_OPER', 'AES_FAIL',
                           'DET_ALERT', 'DET_TYPE', 'DET_OPERAT', 'DET_EFFECT']
    fire_cols = [c for c in fire_cols if c in fire_df.columns]

    # Select columns from basicincident
    basic_cols = key_cols + ['INC_TYPE', 'PROP_USE', 'PROP_LOSS', 'CONT_LOSS']
    basic_cols = [c for c in basic_cols if c in basic_df.columns]

    # Merge
    merged = fire_df[fire_cols].merge(
        basic_df[basic_cols],
        on=key_cols,
        how='inner'
    )

    print(f"\n  Merged dataset: {len(merged)} records")

    return merged


def classify_housing_type(df):
    """Classify incidents by housing type based on PROP_USE code"""
    print("\nClassifying housing types...")

    def get_housing_type(prop_use):
        if pd.isna(prop_use) or prop_use == '':
            return 'Unknown'

        prop_use = str(prop_use).strip()

        # Single-family (1-2 family dwellings)
        if prop_use in ['419']:
            return 'Single-family'
        # Multifamily (apartments, condos)
        elif prop_use in ['429']:
            return 'Multifamily'
        # Other residential
        elif prop_use.startswith('4'):
            return 'Other residential'
        else:
            return 'Non-residential'

    df['housing_type'] = df['PROP_USE'].apply(get_housing_type)

    print("  Housing type distribution:")
    print(df['housing_type'].value_counts().to_string())

    return df


def classify_cause(df, lookups):
    """Add human-readable cause labels"""
    print("\nClassifying fire causes...")

    # Cause of ignition
    df['cause_label'] = df['CAUSE_IGN'].map(CAUSE_IGN_MAP).fillna('Unknown')

    # Heat source category
    def categorize_heat_source(code):
        if pd.isna(code) or code in ['', 'UU', 'NN']:
            return 'Unknown'
        code = str(code).strip()[:2]  # First two digits
        if code in ['12', '13', '14', '15']:
            return 'Cooking'
        elif code in ['10', '11']:
            return 'Heating'
        elif code.startswith('4'):
            return 'Electrical'
        elif code in ['61', '62', '63']:
            return 'Smoking'
        elif code in ['64', '65', '66']:
            return 'Open flame'
        else:
            return 'Other'

    df['heat_source_category'] = df['HEAT_SOURC'].apply(categorize_heat_source)

    # Area of origin category
    def categorize_area(code):
        if pd.isna(code) or code in ['', 'UU', 'NN']:
            return 'Unknown'
        code = str(code).strip()
        if code == '24':
            return 'Kitchen'
        elif code in ['21', '22', '23']:
            return 'Living areas'
        elif code in ['25', '26']:
            return 'Bathroom/Laundry'
        elif code == '27':
            return 'Garage'
        elif code in ['51', '52', '53']:
            return 'Mechanical/Electrical'
        elif code.startswith('9'):
            return 'Exterior'
        else:
            return 'Other'

    df['area_category'] = df['AREA_ORIG'].apply(categorize_area)

    print("  Cause distribution:")
    print(df['cause_label'].value_counts().to_string())

    return df


def analyze_cause_by_housing(df):
    """Analyze fire causes by housing type"""
    print("\n" + "="*80)
    print("CAUSE OF IGNITION BY HOUSING TYPE")
    print("="*80)

    # Filter to residential only
    residential = df[df['housing_type'].isin(['Single-family', 'Multifamily'])].copy()

    if len(residential) == 0:
        print("  Warning: No residential incidents found")
        return None

    # Cross-tabulation: cause by housing type
    cause_counts = pd.crosstab(
        residential['housing_type'],
        residential['cause_label'],
        margins=True
    )

    # Calculate percentages
    cause_pct = pd.crosstab(
        residential['housing_type'],
        residential['cause_label'],
        normalize='index'
    ) * 100

    print("\nCause Counts:")
    print(cause_counts.to_string())

    print("\nCause Percentages:")
    print(cause_pct.round(1).to_string())

    # Calculate ratio of multifamily to single-family for each cause
    if 'Single-family' in cause_pct.index and 'Multifamily' in cause_pct.index:
        print("\nMultifamily vs Single-family Comparison:")
        for cause in cause_pct.columns:
            sf_pct = cause_pct.loc['Single-family', cause]
            mf_pct = cause_pct.loc['Multifamily', cause]
            diff = mf_pct - sf_pct
            print(f"  {cause}: SF={sf_pct:.1f}%, MF={mf_pct:.1f}%, Diff={diff:+.1f}%")

    return cause_pct


def analyze_heat_source_by_housing(df):
    """Analyze heat sources by housing type"""
    print("\n" + "="*80)
    print("HEAT SOURCE BY HOUSING TYPE")
    print("="*80)

    residential = df[df['housing_type'].isin(['Single-family', 'Multifamily'])].copy()

    if len(residential) == 0:
        return None

    # Cross-tabulation
    heat_pct = pd.crosstab(
        residential['housing_type'],
        residential['heat_source_category'],
        normalize='index'
    ) * 100

    print("\nHeat Source Percentages:")
    print(heat_pct.round(1).to_string())

    return heat_pct


def analyze_area_origin_by_housing(df):
    """Analyze area of origin by housing type"""
    print("\n" + "="*80)
    print("AREA OF ORIGIN BY HOUSING TYPE")
    print("="*80)

    residential = df[df['housing_type'].isin(['Single-family', 'Multifamily'])].copy()

    if len(residential) == 0:
        return None

    # Cross-tabulation
    area_pct = pd.crosstab(
        residential['housing_type'],
        residential['area_category'],
        normalize='index'
    ) * 100

    print("\nArea of Origin Percentages:")
    print(area_pct.round(1).to_string())

    return area_pct


def analyze_sprinkler_effect(df):
    """Analyze sprinkler presence and effectiveness"""
    print("\n" + "="*80)
    print("SPRINKLER ANALYSIS")
    print("="*80)

    residential = df[df['housing_type'].isin(['Single-family', 'Multifamily'])].copy()

    if len(residential) == 0:
        return None

    # Sprinkler presence by housing type
    residential['sprinkler_present'] = residential['AES_PRES'].apply(
        lambda x: 'Yes' if x == 'Y' else ('No' if x == 'N' else 'Unknown')
    )

    sprinkler_pct = pd.crosstab(
        residential['housing_type'],
        residential['sprinkler_present'],
        normalize='index'
    ) * 100

    print("\nSprinkler Presence by Housing Type:")
    print(sprinkler_pct.round(1).to_string())

    # Sprinkler operation when present
    with_sprinkler = residential[residential['AES_PRES'] == 'Y'].copy()
    if len(with_sprinkler) > 0:
        with_sprinkler['sprinkler_operated'] = with_sprinkler['AES_OPER'].apply(
            lambda x: 'Operated' if x == 'Y' else ('Did not operate' if x == 'N' else 'Unknown')
        )

        operation_pct = pd.crosstab(
            with_sprinkler['housing_type'],
            with_sprinkler['sprinkler_operated'],
            normalize='index'
        ) * 100

        print("\nSprinkler Operation (when present):")
        print(operation_pct.round(1).to_string())

    # Fire spread comparison
    residential['fire_spread'] = residential['FIRE_SPRD'].apply(
        lambda x: {
            '1': 'Confined to object',
            '2': 'Confined to room',
            '3': 'Confined to floor',
            '4': 'Confined to building',
            '5': 'Beyond building'
        }.get(str(x), 'Unknown') if pd.notna(x) else 'Unknown'
    )

    # Compare fire spread with vs without sprinklers
    print("\nFire Spread - With Sprinklers:")
    with_spr = residential[residential['AES_PRES'] == 'Y']
    if len(with_spr) > 0:
        print(with_spr['fire_spread'].value_counts(normalize=True).mul(100).round(1).to_string())

    print("\nFire Spread - Without Sprinklers:")
    without_spr = residential[residential['AES_PRES'] == 'N']
    if len(without_spr) > 0:
        print(without_spr['fire_spread'].value_counts(normalize=True).mul(100).round(1).to_string())

    return sprinkler_pct


def create_visualizations(df, cause_pct, heat_pct, sprinkler_pct):
    """Create comparison charts"""
    print("\nCreating visualizations...")

    import matplotlib.pyplot as plt

    # Chart 1: Cause of Ignition Comparison
    if cause_pct is not None:
        fig, ax = plt.subplots(figsize=(10, 6))

        cause_pct_plot = cause_pct.drop('Unknown', axis=1, errors='ignore')
        cause_pct_plot = cause_pct_plot[['Unintentional', 'Intentional', 'Equipment failure', 'Undetermined']]

        x = range(len(cause_pct_plot.columns))
        width = 0.35

        if 'Single-family' in cause_pct_plot.index and 'Multifamily' in cause_pct_plot.index:
            sf_vals = cause_pct_plot.loc['Single-family'].values
            mf_vals = cause_pct_plot.loc['Multifamily'].values

            bars1 = ax.bar([i - width/2 for i in x], sf_vals, width, label='Single-family', color='#2ca02c')
            bars2 = ax.bar([i + width/2 for i in x], mf_vals, width, label='Multifamily', color='#d62728')

            ax.set_ylabel('Percentage of Fires (%)')
            ax.set_title('Cause of Ignition: Single-family vs Multifamily')
            ax.set_xticks(x)
            ax.set_xticklabels(cause_pct_plot.columns, rotation=15, ha='right')
            ax.legend()

            # Add value labels
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.0f}%', ha='center', va='bottom', fontsize=9)
            for bar in bars2:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.0f}%', ha='center', va='bottom', fontsize=9)

            plt.tight_layout()
            plt.savefig('outputs/chart_cause_comparison.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("  Saved: outputs/chart_cause_comparison.png")

    # Chart 2: Heat Source Comparison
    if heat_pct is not None:
        fig, ax = plt.subplots(figsize=(12, 6))

        heat_pct_plot = heat_pct.drop('Unknown', axis=1, errors='ignore')

        x = range(len(heat_pct_plot.columns))
        width = 0.35

        if 'Single-family' in heat_pct_plot.index and 'Multifamily' in heat_pct_plot.index:
            sf_vals = heat_pct_plot.loc['Single-family'].values
            mf_vals = heat_pct_plot.loc['Multifamily'].values

            bars1 = ax.bar([i - width/2 for i in x], sf_vals, width, label='Single-family', color='#2ca02c')
            bars2 = ax.bar([i + width/2 for i in x], mf_vals, width, label='Multifamily', color='#d62728')

            ax.set_ylabel('Percentage of Fires (%)')
            ax.set_title('Heat Source: Single-family vs Multifamily\n(What started the fire?)')
            ax.set_xticks(x)
            ax.set_xticklabels(heat_pct_plot.columns, rotation=15, ha='right')
            ax.legend()

            plt.tight_layout()
            plt.savefig('outputs/chart_heat_source_comparison.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("  Saved: outputs/chart_heat_source_comparison.png")

    # Chart 3: Sprinkler Presence
    if sprinkler_pct is not None:
        fig, ax = plt.subplots(figsize=(8, 6))

        sprinkler_plot = sprinkler_pct[['Yes', 'No']].copy() if 'Yes' in sprinkler_pct.columns else sprinkler_pct

        x = range(len(sprinkler_plot.index))
        width = 0.35

        if 'Yes' in sprinkler_plot.columns and 'No' in sprinkler_plot.columns:
            yes_vals = sprinkler_plot['Yes'].values
            no_vals = sprinkler_plot['No'].values

            bars1 = ax.bar([i - width/2 for i in x], yes_vals, width, label='Sprinkler Present', color='#1f77b4')
            bars2 = ax.bar([i + width/2 for i in x], no_vals, width, label='No Sprinkler', color='#ff7f0e')

            ax.set_ylabel('Percentage of Fires (%)')
            ax.set_title('Sprinkler Presence by Housing Type')
            ax.set_xticks(x)
            ax.set_xticklabels(sprinkler_plot.index)
            ax.legend()

            # Add value labels
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.0f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
            for bar in bars2:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.0f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

            plt.tight_layout()
            plt.savefig('outputs/chart_sprinkler_by_housing.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("  Saved: outputs/chart_sprinkler_by_housing.png")


def main():
    print("\n" + "#"*60)
    print("# NFIRS CAUSE ANALYSIS")
    print("# Why does multifamily have 4x higher fire rates?")
    print("#"*60)

    # Load code lookups
    lookups = load_codelookup()

    # Extract Austin NFIRS data
    df = extract_austin_nfirs()

    if df is None or len(df) == 0:
        print("\nError: No data extracted. Check that NFIRS files exist.")
        return

    # Classify housing type
    df = classify_housing_type(df)

    # Classify causes
    df = classify_cause(df, lookups)

    # Save detailed dataset
    os.makedirs("processed_data", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    df.to_csv("processed_data/nfirs_austin_detailed.csv", index=False)
    print(f"\nSaved: processed_data/nfirs_austin_detailed.csv ({len(df)} records)")

    # Run analyses
    cause_pct = analyze_cause_by_housing(df)
    heat_pct = analyze_heat_source_by_housing(df)
    area_pct = analyze_area_origin_by_housing(df)
    sprinkler_pct = analyze_sprinkler_effect(df)

    # Save analysis outputs
    if cause_pct is not None:
        cause_pct.to_csv("outputs/cause_by_housing_type.csv")
        print("Saved: outputs/cause_by_housing_type.csv")

    if heat_pct is not None:
        heat_pct.to_csv("outputs/heat_source_by_housing.csv")
        print("Saved: outputs/heat_source_by_housing.csv")

    if area_pct is not None:
        area_pct.to_csv("outputs/area_origin_by_housing.csv")
        print("Saved: outputs/area_origin_by_housing.csv")

    if sprinkler_pct is not None:
        sprinkler_pct.to_csv("outputs/sprinkler_by_housing.csv")
        print("Saved: outputs/sprinkler_by_housing.csv")

    # Create visualizations
    create_visualizations(df, cause_pct, heat_pct, sprinkler_pct)

    # Summary
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)

    residential = df[df['housing_type'].isin(['Single-family', 'Multifamily'])]

    if len(residential) > 0:
        # Intentional fire comparison
        sf_intentional = residential[
            (residential['housing_type'] == 'Single-family') &
            (residential['cause_label'] == 'Intentional')
        ]
        mf_intentional = residential[
            (residential['housing_type'] == 'Multifamily') &
            (residential['cause_label'] == 'Intentional')
        ]

        sf_total = len(residential[residential['housing_type'] == 'Single-family'])
        mf_total = len(residential[residential['housing_type'] == 'Multifamily'])

        if sf_total > 0 and mf_total > 0:
            sf_int_pct = len(sf_intentional) / sf_total * 100
            mf_int_pct = len(mf_intentional) / mf_total * 100

            print(f"\n1. INTENTIONAL FIRES (Arson):")
            print(f"   Single-family: {sf_int_pct:.1f}% of fires")
            print(f"   Multifamily:   {mf_int_pct:.1f}% of fires")
            if mf_int_pct > sf_int_pct:
                print(f"   -> Multifamily has {mf_int_pct/sf_int_pct:.1f}x higher arson rate")

        # Sprinkler comparison
        sf_sprinkler = residential[
            (residential['housing_type'] == 'Single-family') &
            (residential['AES_PRES'] == 'Y')
        ]
        mf_sprinkler = residential[
            (residential['housing_type'] == 'Multifamily') &
            (residential['AES_PRES'] == 'Y')
        ]

        if sf_total > 0 and mf_total > 0:
            sf_spr_pct = len(sf_sprinkler) / sf_total * 100
            mf_spr_pct = len(mf_sprinkler) / mf_total * 100

            print(f"\n2. SPRINKLER PRESENCE:")
            print(f"   Single-family: {sf_spr_pct:.1f}% have sprinklers")
            print(f"   Multifamily:   {mf_spr_pct:.1f}% have sprinklers")

    print("\n" + "="*60)
    print("Analysis complete. Review outputs/ for detailed results.")
    print("="*60)


if __name__ == "__main__":
    main()
