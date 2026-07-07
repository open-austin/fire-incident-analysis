#!/usr/bin/env python3
"""
Step 8: Parcel-Level Fire Rate Analysis
=========================================
Calculates fire incident rates by building type and year built
using parcel-level data from the spatial join.

Usage:
    python 08_parcel_analysis.py

Input:
    processed_data/incidents_with_parcels.csv
    raw_data/parcels.geojson (for denominator counts)

Output:
    outputs/fire_rates_by_building_type.csv
    outputs/fire_rates_by_year_built.csv
    outputs/structure_fire_rates_by_year_built.csv
    outputs/parcel_analysis_summary.txt
"""

import pandas as pd
import geopandas as gpd
import warnings

warnings.filterwarnings("ignore")


# Group improvement types into broader categories for analysis
BUILDING_TYPE_MAP = {
    "1 FAM DWELLING": "Single Family",
    "2 FAM DWELLING": "Duplex",
    "TOWNHOMES": "Townhome",
    "FOURPLEX": "Small Multifamily (3-4)",
    "TRIPLEX": "Small Multifamily (3-4)",
    "APARTMENT 5-25": "Mid Multifamily (5-25)",
    "APARTMENT 25-49": "Mid Multifamily (5-25)",
    "APARTMENT 50-100": "Large Multifamily (50+)",
    "APARTMENT 100+": "Large Multifamily (50+)",
    "Real, Residential, Single": "Single Family",
    "Real, Residential, Two-Fa": "Duplex",
    "MOHO SINGLE REAL": "Manufactured Home",
    "MOHO DOUBLE REAL": "Manufactured Home",
    "CONVENIENCE STOR": "Commercial",
    "OFFICE LG >35000": "Commercial",
    "OFFICE (SMALL)": "Commercial",
    "OFFICE MED 10-35": "Commercial",
    "STRIP CTR >10000": "Commercial",
    "STRIP CTR <10000": "Commercial",
    "DISC STR >25,000": "Commercial",
    "SM STORE <10K SF": "Commercial",
    "FAST FOOD REST": "Commercial",
    "RESTAURANT": "Commercial",
    "GROCERY STORE": "Commercial",
    "SVC/REPAIR GAR'G": "Commercial",
    "WAREHOUSE <20000": "Industrial/Warehouse",
    "WAREHOUSE >20000": "Industrial/Warehouse",
    "MINI-WAREHOUSE": "Industrial/Warehouse",
    "HOTEL-LMTD SERVC": "Hotel/Hospitality",
    "HOTEL-FULL SERVI": "Hotel/Hospitality",
    "MOTEL": "Hotel/Hospitality",
}

# Year-built cohorts aligned with code changes
YEAR_COHORTS = [
    (0, 1969, "Pre-1970"),
    (1970, 1989, "1970-1989"),
    (1990, 2005, "1990-2005"),
    (2006, 2015, "2006-2015 (post-sprinkler code)"),
    (2016, 2030, "2016-present"),
]


def classify_building_type(imprv_type):
    if pd.isna(imprv_type):
        return None
    imprv_type = imprv_type.strip()
    return BUILDING_TYPE_MAP.get(imprv_type, None)


def classify_year_cohort(year):
    if pd.isna(year) or year <= 0:
        return None
    for lo, hi, label in YEAR_COHORTS:
        if lo <= year <= hi:
            return label
    return None


def load_data():
    """Load incident-parcel join and full parcel inventory."""
    print("Loading incident data...")
    incidents = pd.read_csv("processed_data/incidents_with_parcels.csv")
    matched = incidents[incidents["PARCEL_ID"].notna()].copy()
    print(f"  {len(matched):,} incidents matched to parcels")

    print("Loading parcel inventory (attributes only)...")
    parcels = gpd.read_file("raw_data/parcels.geojson", ignore_geometry=True)
    print(f"  {len(parcels):,} total parcels")

    return matched, parcels


def analyze_by_building_type(incidents, parcels):
    """Fire rates per 1,000 parcels by building type."""
    print("\n" + "=" * 60)
    print("FIRE RATES BY BUILDING TYPE")
    print("=" * 60)

    incidents["building_type"] = incidents["IMPRV_TYPE"].apply(classify_building_type)
    parcels["building_type"] = parcels["IMPRV_TYPE"].apply(classify_building_type)

    # Denominator: total parcels per type
    denom = parcels[parcels["building_type"].notna()].groupby("building_type").size()
    denom.name = "total_parcels"

    # Numerator: all fire incidents
    all_fires = incidents[incidents["building_type"].notna()].groupby("building_type").size()
    all_fires.name = "all_incidents"

    # Structure fires only
    struct = incidents[
        (incidents["building_type"].notna()) & (incidents["is_structure_fire"] == True)
    ].groupby("building_type").size()
    struct.name = "structure_fires"

    # Trash/dumpster fires
    trash = incidents[
        (incidents["building_type"].notna()) & (incidents["is_trash_fire"] == True)
    ].groupby("building_type").size()
    trash.name = "trash_fires"

    result = pd.concat([denom, all_fires, struct, trash], axis=1).fillna(0)
    result["all_rate_per_1k"] = (result["all_incidents"] / result["total_parcels"] * 1000).round(1)
    result["structure_rate_per_1k"] = (result["structure_fires"] / result["total_parcels"] * 1000).round(1)
    result["trash_rate_per_1k"] = (result["trash_fires"] / result["total_parcels"] * 1000).round(1)
    result = result.sort_values("all_rate_per_1k", ascending=False)

    print(result.to_string())

    result.to_csv("outputs/fire_rates_by_building_type.csv")
    print("\n  Saved: outputs/fire_rates_by_building_type.csv")
    return result


def analyze_by_year_built(incidents, parcels):
    """Fire rates by year-built cohort, overall and by building type."""
    print("\n" + "=" * 60)
    print("FIRE RATES BY YEAR BUILT")
    print("=" * 60)

    incidents["year_cohort"] = incidents["YEAR_BUILT"].apply(classify_year_cohort)
    parcels["year_cohort"] = parcels["YEAR_BUILT"].apply(classify_year_cohort)

    # --- Overall rates by cohort ---
    denom = parcels[parcels["year_cohort"].notna()].groupby("year_cohort").size()
    denom.name = "total_parcels"

    all_fires = incidents[incidents["year_cohort"].notna()].groupby("year_cohort").size()
    all_fires.name = "all_incidents"

    struct = incidents[
        (incidents["year_cohort"].notna()) & (incidents["is_structure_fire"] == True)
    ].groupby("year_cohort").size()
    struct.name = "structure_fires"

    result = pd.concat([denom, all_fires, struct], axis=1).fillna(0)
    result["all_rate_per_1k"] = (result["all_incidents"] / result["total_parcels"] * 1000).round(1)
    result["structure_rate_per_1k"] = (result["structure_fires"] / result["total_parcels"] * 1000).round(1)

    # Sort by cohort order
    cohort_order = [label for _, _, label in YEAR_COHORTS]
    result = result.reindex([c for c in cohort_order if c in result.index])

    print("\nAll building types:")
    print(result.to_string())

    result.to_csv("outputs/fire_rates_by_year_built.csv")
    print("\n  Saved: outputs/fire_rates_by_year_built.csv")

    # --- Structure fire rates by cohort AND building type ---
    print("\n" + "-" * 60)
    print("STRUCTURE FIRE RATES BY YEAR BUILT × BUILDING TYPE")
    print("-" * 60)

    incidents["building_type"] = incidents["IMPRV_TYPE"].apply(classify_building_type)
    parcels["building_type"] = parcels["IMPRV_TYPE"].apply(classify_building_type)

    mask_i = incidents["year_cohort"].notna() & incidents["building_type"].notna()
    mask_p = parcels["year_cohort"].notna() & parcels["building_type"].notna()

    denom2 = parcels[mask_p].groupby(["building_type", "year_cohort"]).size()
    denom2.name = "total_parcels"

    struct2 = incidents[
        mask_i & (incidents["is_structure_fire"] == True)
    ].groupby(["building_type", "year_cohort"]).size()
    struct2.name = "structure_fires"

    cross = pd.concat([denom2, struct2], axis=1).fillna(0)
    cross["structure_rate_per_1k"] = (cross["structure_fires"] / cross["total_parcels"] * 1000).round(1)

    # Pivot for readability
    pivot = cross["structure_rate_per_1k"].unstack("year_cohort")
    pivot = pivot.reindex(columns=[c for c in cohort_order if c in pivot.columns])

    # Only show types with enough data
    counts_pivot = cross["total_parcels"].unstack("year_cohort").fillna(0)
    has_data = counts_pivot.sum(axis=1) >= 50
    pivot = pivot[has_data]

    print(pivot.to_string())

    cross.to_csv("outputs/structure_fire_rates_by_year_built.csv")
    print("\n  Saved: outputs/structure_fire_rates_by_year_built.csv")

    return result, cross


def write_summary(btype_result, year_result):
    """Write a plain-text summary of key findings."""
    lines = []
    lines.append("PARCEL-LEVEL FIRE RATE ANALYSIS — KEY FINDINGS")
    lines.append("=" * 60)
    lines.append("")

    # Top building types by structure fire rate
    lines.append("STRUCTURE FIRE RATES BY BUILDING TYPE (per 1,000 parcels, 2022-2024)")
    lines.append("-" * 60)
    top = btype_result.sort_values("structure_rate_per_1k", ascending=False)
    for btype, row in top.iterrows():
        if row["total_parcels"] >= 50:
            lines.append(
                f"  {btype:<30s}  {row['structure_rate_per_1k']:>6.1f}  "
                f"({int(row['structure_fires'])} fires / {int(row['total_parcels']):,} parcels)"
            )

    lines.append("")
    lines.append("STRUCTURE FIRE RATES BY YEAR BUILT COHORT (per 1,000 parcels)")
    lines.append("-" * 60)
    for cohort, row in year_result.iterrows():
        lines.append(
            f"  {cohort:<35s}  {row['structure_rate_per_1k']:>6.1f}  "
            f"({int(row['structure_fires'])} fires / {int(row['total_parcels']):,} parcels)"
        )

    # Sprinkler code comparison
    lines.append("")
    lines.append("2006 SPRINKLER CODE IMPACT")
    lines.append("-" * 60)
    pre = year_result.loc[
        year_result.index.isin(["Pre-1970", "1970-1989", "1990-2005"])
    ]
    post = year_result.loc[
        year_result.index.isin(["2006-2015 (post-sprinkler code)", "2016-present"])
    ]
    if len(pre) > 0 and len(post) > 0:
        pre_rate = pre["structure_fires"].sum() / pre["total_parcels"].sum() * 1000
        post_rate = post["structure_fires"].sum() / post["total_parcels"].sum() * 1000
        reduction = (1 - post_rate / pre_rate) * 100
        lines.append(f"  Pre-2006 structure fire rate:   {pre_rate:.1f} per 1,000 parcels")
        lines.append(f"  Post-2006 structure fire rate:  {post_rate:.1f} per 1,000 parcels")
        lines.append(f"  Reduction:                      {reduction:.0f}%")

    summary = "\n".join(lines)
    print("\n" + summary)

    with open("outputs/parcel_analysis_summary.txt", "w") as f:
        f.write(summary)
    print("\n  Saved: outputs/parcel_analysis_summary.txt")


def main():
    print("\n" + "#" * 60)
    print("# STEP 8: PARCEL-LEVEL FIRE RATE ANALYSIS")
    print("#" * 60)

    incidents, parcels = load_data()

    btype_result = analyze_by_building_type(incidents, parcels)
    year_result, cross_result = analyze_by_year_built(incidents, parcels)
    write_summary(btype_result, year_result)

    print("\nDone!")


if __name__ == "__main__":
    main()
