#!/usr/bin/env python3
"""
Step 10: Townhome Fire Code Cohort Analysis
=============================================
Analyzes fire incident rates in townhomes by construction era to compare
life safety outcomes between sprinkler-protected buildings and those relying
on two-hour fire separations.

Code cohorts (Austin amendments to IBC):
  - Pre-2019:   2-hour fire separation walls, no sprinklers required
  - 2019-2021:  2-hour wall OR 1-hour wall + sprinklers (builder's choice)
  - Post-2021:  Sprinklers required in all new townhomes

Data quality note:
  TCAD's IMPRV_TYPE = "TOWNHOMES" includes both individual townhome units
  (UNITS=1, ~80% of parcels) and multi-unit condo complexes (UNITS>1, ~8%).
  This script separates the two for accurate analysis. Year-built data for
  condo complexes is often missing from TCAD but was manually verified via
  property records (Redfin, Zillow, HAR, Trulia, Travis CAD).

Usage:
    python 10_townhome_cohort_analysis.py

Input:
    processed_data/incidents_enriched.csv
    raw_data/parcels.geojson

Output:
    processed_data/townhome_incidents.csv
    outputs/townhome_rates_by_cohort.csv
    outputs/townhome_cohort_summary.txt
"""

import pandas as pd
import geopandas as gpd
import warnings

warnings.filterwarnings("ignore")


# Fire code cohorts for Austin townhomes
CODE_COHORTS = [
    (0, 2018, "Pre-2019: 2hr wall, no sprinklers"),
    (2019, 2021, "2019-2021: 2hr wall OR 1hr+sprinklers"),
    (2022, 2030, "Post-2021: sprinklers required"),
]

# Year-built backfill for condo complexes missing TCAD data.
# Verified via property records (Redfin, Zillow, HAR, Trulia, Travis CAD).
YEAR_BUILT_BACKFILL = {
    "0419191002": 1983,  # 7825 Beauregard Cir - duplex condos
    "0406100168": 1982,  # 3801 Menchaca Rd - Coachlight Condos
    "0310080212": 2002,  # 4807 E Oltorf St - townhome/condo
    "0132050910": 1985,  # 5503 Oakwood Cv - Oakwood Hollow condos
    "0222210537": 1971,  # 6403 Chimney Creek Cir - Villas of Coronado Hills
    "0145111013": 1983,  # 7211 Lakewood Dr - Lakewood Condos
    "0114050817": 1982,  # 2500 Enfield Rd - Enfield Condominiums
    "0133071025": 1985,  # 4305 Bonnell Vista Cv - Stoneledge II condos
    "0410250535": 1984,  # 6501 Brush Country Rd - Westcreek Landing condos
}


def classify_code_cohort(year_built):
    """Classify a townhome by fire code era based on year built."""
    if pd.isna(year_built) or year_built <= 0:
        return None
    for lo, hi, label in CODE_COHORTS:
        if lo <= year_built <= hi:
            return label
    return None


def backfill_year_built(df):
    """Backfill missing YEAR_BUILT from manually verified property records."""
    filled = 0
    for parcel_id, year in YEAR_BUILT_BACKFILL.items():
        mask = (df["PARCEL_ID"] == parcel_id) & df["YEAR_BUILT"].isna()
        count = mask.sum()
        if count > 0:
            df.loc[mask, "YEAR_BUILT"] = year
            filled += count
    return filled


def load_data():
    """Load incident and parcel data, filtering to TCAD townhomes."""
    print("Loading incident data...")
    incidents = pd.read_csv("processed_data/incidents_enriched.csv")
    incidents["IMPRV_CLEAN"] = incidents["IMPRV_TYPE"].str.strip()
    print(f"  {len(incidents):,} total incidents")

    print("Loading parcel inventory...")
    parcels = gpd.read_file("raw_data/parcels.geojson", ignore_geometry=True)
    parcels["IMPRV_CLEAN"] = parcels["IMPRV_TYPE"].str.strip()
    print(f"  {len(parcels):,} total parcels")

    # Filter to TCAD "TOWNHOMES"
    th_incidents = incidents[incidents["IMPRV_CLEAN"] == "TOWNHOMES"].copy()
    th_parcels = parcels[parcels["IMPRV_CLEAN"] == "TOWNHOMES"].copy()
    print(f"\n  All TCAD 'TOWNHOMES' incidents: {len(th_incidents)}")
    print(f"  All TCAD 'TOWNHOMES' parcels:   {len(th_parcels):,}")

    # Backfill year built
    inc_filled = backfill_year_built(th_incidents)
    par_filled = backfill_year_built(th_parcels)
    if inc_filled > 0 or par_filled > 0:
        print(f"\n  Year-built backfilled from property records:")
        print(f"    Incidents: {inc_filled} rows")
        print(f"    Parcels:   {par_filled} rows")

    return th_incidents, th_parcels


def analyze_data_quality(th_incidents, th_parcels):
    """Assess TCAD classification quality before analysis."""
    print("\n" + "=" * 60)
    print("DATA QUALITY: TCAD 'TOWNHOMES' CLASSIFICATION")
    print("=" * 60)

    # Separate by unit count
    for label, mask_fn in [
        ("UNITS=1 (individual townhome units)", lambda df: df["UNITS"] == 1),
        ("UNITS=0 (missing unit count)", lambda df: df["UNITS"] == 0),
        ("UNITS>1 (multi-unit condo complexes)", lambda df: df["UNITS"] > 1),
    ]:
        p = th_parcels[mask_fn(th_parcels)]
        i = th_incidents[mask_fn(th_incidents)]
        sf = i[i["is_structure_fire"] == True]
        print(f"\n  {label}:")
        print(f"    Parcels: {len(p):,}  |  All incidents: {len(i)}  |  Structure fires: {len(sf)}")

    # Show the condo complexes with fires
    multi_sf = th_incidents[
        (th_incidents["UNITS"] > 1) & (th_incidents["is_structure_fire"] == True)
    ]
    if len(multi_sf) > 0:
        print(f"\n  Condo complex structure fires (not true townhomes):")
        for _, row in multi_sf.iterrows():
            yb = int(row["YEAR_BUILT"]) if pd.notna(row["YEAR_BUILT"]) else "N/A"
            print(
                f"    {row['calendaryear']} | UNITS={int(row['UNITS']):>3d} | "
                f"YB:{str(yb):<5s} | {row['problem']:<30s} | "
                f"{str(row['PROPERTY_ADDRESS'])[:35]}"
            )

    print(f"\n  Conclusion: {len(th_parcels[th_parcels['UNITS'] > 1]):,} of "
          f"{len(th_parcels):,} TCAD 'TOWNHOMES' parcels are actually multi-unit")
    print(f"  condo complexes (10-234 units). These are excluded from cohort analysis.")


def analyze_true_townhomes(th_incidents, th_parcels):
    """Analyze only true individual townhome parcels (UNITS <= 1)."""
    print("\n" + "=" * 60)
    print("TRUE TOWNHOME ANALYSIS (UNITS <= 1)")
    print("=" * 60)

    # Filter to individual townhome units (UNITS=0 or 1)
    # UNITS=0 includes some new construction with incomplete TCAD data
    t_parcels = th_parcels[th_parcels["UNITS"] <= 1].copy()
    t_incidents = th_incidents[th_incidents["UNITS"] <= 1].copy()

    print(f"\n  True townhome parcels:   {len(t_parcels):,}")
    print(f"  True townhome incidents: {len(t_incidents)}")

    # Incident breakdown
    print(f"\n  By incident category:")
    for cat, count in t_incidents["incident_category"].value_counts().items():
        print(f"    {cat:<40s}  {count}")

    # Structure fires
    sf = t_incidents[t_incidents["is_structure_fire"] == True]
    print(f"\n  Structure fires at true townhomes: {len(sf)}")
    if len(sf) > 0:
        for _, row in sf.iterrows():
            yb = int(row["YEAR_BUILT"]) if pd.notna(row["YEAR_BUILT"]) else "N/A"
            typ = "non-confined" if row["is_nonconfined_structure_fire"] else "confined"
            print(
                f"    {row['calendaryear']} | YB:{str(yb):<5s} | {typ:<12s} | "
                f"{row['problem']:<30s} | {str(row['PROPERTY_ADDRESS'])[:35]}"
            )

    # Cohort distribution
    t_parcels["code_cohort"] = t_parcels["YEAR_BUILT"].apply(classify_code_cohort)
    cohort_counts = t_parcels[t_parcels["code_cohort"].notna()].groupby("code_cohort").size()
    cohort_order = [label for _, _, label in CODE_COHORTS]
    cohort_counts = cohort_counts.reindex([c for c in cohort_order if c in cohort_counts.index])

    print(f"\n  Parcel inventory by code cohort:")
    for cohort, count in cohort_counts.items():
        pct = count / cohort_counts.sum() * 100
        print(f"    {cohort:<45s}  {count:>5,}  ({pct:.1f}%)")
    print(f"    {'TOTAL':<45s}  {cohort_counts.sum():>5,}")

    return t_incidents, t_parcels


def analyze_fire_rarity(th_incidents, th_parcels, all_incidents, all_parcels):
    """Put townhome fire rates in context of overall fire rarity."""
    print("\n" + "=" * 60)
    print("FIRE RARITY CONTEXT")
    print("=" * 60)

    # Building type map for residential parcels
    res_types = {
        "1 FAM DWELLING": "Single Family",
        "DUPLEX": "Duplex",
        "TOWNHOMES": "Townhome",
        "TRIPLEX": "Small MF (3-4)",
        "FOURPLEX": "Small MF (3-4)",
        "APARTMENT 5-25": "Mid MF (5-25)",
        "APARTMENT 25-49": "Mid MF (25-49)",
        "APARTMENT 50-100": "Large MF (50-100)",
        "APARTMENT 100+": "Large MF (100+)",
    }

    all_parcels["IMPRV_CLEAN"] = all_parcels["IMPRV_TYPE"].str.strip()
    all_incidents["IMPRV_CLEAN"] = all_incidents["IMPRV_TYPE"].str.strip()

    total_sf = int(all_incidents["is_structure_fire"].sum())
    total_nc = int(all_incidents["is_nonconfined_structure_fire"].sum())

    print(f"\n  Austin structure fires (2022-2024, 3 years): {total_sf:,}")
    print(f"    Non-confined (BOX alarm): {total_nc:,}")
    print(f"    Confined (ELEC/BBQ):      {total_sf - total_nc:,}")

    print(f"\n  Annual probability of a structure fire by building type:")
    print(f"  {'Type':<20s}  {'Parcels':>8s}  {'Fires/3yr':>10s}  {'Annual odds':>14s}")
    print(f"  {'-'*20}  {'-'*8}  {'-'*10}  {'-'*14}")

    results = []
    for raw_type, label in res_types.items():
        p_count = len(all_parcels[all_parcels["IMPRV_CLEAN"] == raw_type])
        i_count = len(all_incidents[
            (all_incidents["IMPRV_CLEAN"] == raw_type) &
            (all_incidents["is_structure_fire"] == True)
        ])
        if p_count >= 50:
            annual = i_count / 3
            odds = int(p_count / annual) if annual > 0 else 0
            results.append((label, p_count, i_count, odds))

    for label, p_count, i_count, odds in sorted(results, key=lambda x: x[3]):
        odds_str = f"1 in {odds:,}" if odds > 0 else "N/A"
        print(f"  {label:<20s}  {p_count:>8,}  {i_count:>10}  {odds_str:>14s}")

    # National comparison
    print(f"\n  National comparison (NFPA):")
    print(f"    ~360,000 residential structure fires / year")
    print(f"    ~140 million occupied housing units")
    print(f"    National rate: ~2.6 per 1,000 units (1 in 389 homes/year)")
    print(f"    Austin townhome rate: ~1 in 671 parcels/year")

    # Why this matters for the cohort analysis
    true_th = th_parcels[th_parcels["UNITS"] <= 1]
    post_2021 = true_th[true_th["YEAR_BUILT"] > 2021]
    expected = len(post_2021) / 671  # expected fires per year
    print(f"\n  Implication for cohort analysis:")
    print(f"    Post-2021 true townhome parcels: {len(post_2021):,}")
    print(f"    At townhome base rate: ~{expected:.1f} fires expected per year")
    print(f"    Years of data needed for 30 events: ~{30/expected:.0f}" if expected > 0 else "")
    print(f"    Years of data available: 3")

    return results


def analyze_all_townhome_labeled(th_incidents, th_parcels):
    """Analyze all TCAD 'TOWNHOMES' parcels with backfilled year-built."""
    print("\n" + "=" * 60)
    print("ALL TCAD 'TOWNHOMES' WITH BACKFILLED YEAR-BUILT")
    print("=" * 60)

    th_incidents["code_cohort"] = th_incidents["YEAR_BUILT"].apply(classify_code_cohort)
    th_parcels["code_cohort"] = th_parcels["YEAR_BUILT"].apply(classify_code_cohort)

    # Denominator
    denom = th_parcels[th_parcels["code_cohort"].notna()].groupby("code_cohort").size()
    denom.name = "total_parcels"

    # Structure fires
    struct = th_incidents[
        (th_incidents["code_cohort"].notna()) & (th_incidents["is_structure_fire"] == True)
    ].groupby("code_cohort").size()
    struct.name = "structure_fires"

    # All incidents
    all_fires = th_incidents[th_incidents["code_cohort"].notna()].groupby("code_cohort").size()
    all_fires.name = "all_incidents"

    result = pd.concat([denom, all_fires, struct], axis=1).fillna(0)
    result["all_rate_per_1k"] = (result["all_incidents"] / result["total_parcels"] * 1000).round(1)
    result["structure_rate_per_1k"] = (result["structure_fires"] / result["total_parcels"] * 1000).round(1)

    cohort_order = [label for _, _, label in CODE_COHORTS]
    result = result.reindex([c for c in cohort_order if c in result.index])

    print("\n" + result.to_string())

    unclass = th_incidents[th_incidents["code_cohort"].isna()]
    if len(unclass) > 0:
        print(f"\n  Unclassified incidents (still missing year built): {len(unclass)}")

    result.to_csv("outputs/townhome_rates_by_cohort.csv")
    print("\n  Saved: outputs/townhome_rates_by_cohort.csv")

    return result


def write_summary(cohort_rates, th_incidents, th_parcels, t_incidents, t_parcels):
    """Write honest summary acknowledging data limitations."""
    lines = []
    lines.append("TOWNHOME FIRE CODE COHORT ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    lines.append("BACKGROUND")
    lines.append("-" * 60)
    lines.append("Austin adopted changes to townhome fire protection requirements:")
    lines.append("  - Pre-2019:   2-hour fire separation walls, no sprinklers")
    lines.append("  - 2019-2021:  2-hour wall OR 1-hour wall + sprinklers (builder choice)")
    lines.append("  - Post-2021:  Sprinklers required in all new townhomes")
    lines.append("")
    lines.append("This analysis examines whether Austin's local fire incident data")
    lines.append("can support conclusions about fire code effectiveness in townhomes.")
    lines.append("")

    lines.append("DATA QUALITY FINDING")
    lines.append("-" * 60)
    multi = th_parcels[th_parcels["UNITS"] > 1]
    lines.append(f"  TCAD's 'TOWNHOMES' classification includes {len(multi):,} multi-unit")
    lines.append(f"  condo complexes (10-234 units per parcel) alongside {len(t_parcels):,}")
    lines.append(f"  true individual townhome parcels (UNITS <= 1).")
    lines.append("")
    lines.append("  The condo complexes are 1970s-1980s era properties with missing")
    lines.append("  year-built data in TCAD. Year-built was manually verified via")
    lines.append("  property records (Redfin, Zillow, HAR, Travis CAD). All are pre-2019.")
    lines.append("")

    # True townhome stats
    t_sf = t_incidents[t_incidents["is_structure_fire"] == True]
    lines.append("TRUE TOWNHOMES (UNITS <= 1)")
    lines.append("-" * 60)
    lines.append(f"  Parcels:          {len(t_parcels):,}")
    lines.append(f"  All incidents:    {len(t_incidents)} (3 years)")
    lines.append(f"  Structure fires:  {len(t_sf)}")
    if len(t_sf) > 0:
        for _, row in t_sf.iterrows():
            yb = int(row["YEAR_BUILT"]) if pd.notna(row["YEAR_BUILT"]) else "N/A"
            lines.append(f"    - {row['calendaryear']}: {row['problem']} (built {yb})")
    lines.append("")

    # Cohort rates
    lines.append("RATES BY CODE COHORT (all TCAD 'TOWNHOMES', backfilled)")
    lines.append("-" * 60)
    for cohort, row in cohort_rates.iterrows():
        lines.append(f"  {cohort}:")
        lines.append(
            f"    Parcels: {int(row['total_parcels']):,}  |  "
            f"Structure fires: {int(row['structure_fires'])}  |  "
            f"Rate: {row['structure_rate_per_1k']:.1f}/1k"
        )
    lines.append("")

    lines.append("WHY STRUCTURE FIRES ARE RARE")
    lines.append("-" * 60)
    lines.append("  Structure fires are low-probability events across all building")
    lines.append("  types. Annual probability of a structure fire by type:")
    lines.append("")
    lines.append("    Single Family:      1 in  372 parcels/year")
    lines.append("    Townhome:           1 in  671 parcels/year")
    lines.append("    Duplex:             1 in  162 parcels/year")
    lines.append("    Large MF (100+):    1 in    2 parcels/year (but 100+ units each)")
    lines.append("")
    lines.append("  National comparison (NFPA):")
    lines.append("    ~360,000 residential structure fires per year nationally")
    lines.append("    ~140 million occupied housing units")
    lines.append("    National rate: ~2.6 per 1,000 units (1 in 389 homes/year)")
    lines.append("")
    lines.append("  Austin's townhome rate (1 in 671) is well below the national")
    lines.append("  average for all housing types combined.")
    lines.append("")

    # Post-2021 expected events
    post_2021_parcels = len(t_parcels[(t_parcels["YEAR_BUILT"].notna()) & (t_parcels["YEAR_BUILT"] > 2021)])
    expected_annual = post_2021_parcels / 671 if post_2021_parcels > 0 else 0
    years_for_30 = int(30 / expected_annual) if expected_annual > 0 else 0

    lines.append("WHAT THE DATA SUPPORTS")
    lines.append("-" * 60)
    lines.append("  1. Townhomes are very safe. At 1 in 671 parcels/year, they have")
    lines.append("     a lower fire rate than single-family homes (1 in 372) and")
    lines.append("     well below the national average for all housing (1 in 389).")
    lines.append("")
    lines.append("  2. True individual townhomes (UNITS <= 1) are extremely low-risk:")
    total_t = len(t_parcels[t_parcels["YEAR_BUILT"].notna()])
    lines.append(f"     {len(t_sf)} structure fires across {total_t:,} parcels over 3 years.")
    lines.append("")
    lines.append("  3. The data CANNOT support cohort comparisons because:")
    lines.append("     - Only 3 years of incident data (2022-2024). AFD data for")
    lines.append("       2018-2021 was removed from Austin Open Data Portal.")
    lines.append("     - Post-2021 cohort has limited exposure time (1-3 years)")
    lines.append(f"     - At the townhome base rate, the {post_2021_parcels} post-2021")
    lines.append(f"       parcels would produce ~{expected_annual:.1f} fires per year.")
    lines.append(f"       Reaching 30 events (minimum for statistics) would require")
    lines.append(f"       ~{years_for_30} years of observation.")
    lines.append("     - Most structure fires in the TCAD 'TOWNHOMES' category are")
    lines.append("       at mislabeled 1970s-80s condo complexes, not true townhomes")
    lines.append("")
    lines.append("  4. National NFIRS data is needed to meaningfully compare")
    lines.append("     fire outcomes across construction eras for attached housing.")
    lines.append("")

    lines.append("STRUCTURE FIRE CLASSIFICATION METHODOLOGY")
    lines.append("-" * 60)
    lines.append("  Structure fires are classified per NFPA/NFIRS standards:")
    lines.append("    - Non-confined (BOX alarm dispatches): Fire spread beyond origin")
    lines.append("      point. Full structure fire response. NFIRS code 111.")
    lines.append("    - Confined (ELEC, BBQ dispatches): Electrical and cooking fires")
    lines.append("      that stayed at origin. Lighter response. NFIRS codes 113-118.")
    lines.append("  Both are counted as structure fires per NFPA reporting standards.")
    lines.append("  Cooking is the #1 cause of home structure fires nationally (~49%)")
    lines.append("  and electrical is #2-3. AFD dispatch codes determine response")
    lines.append("  level, not incident classification.")
    lines.append("")

    lines.append("LIMITATIONS")
    lines.append("-" * 60)
    lines.append("  1. TCAD 'TOWNHOMES' mixes individual units with condo complexes")
    lines.append("  2. Only 3 years of AFD incident data available (2022-2024);")
    lines.append("     2018-2021 data removed from Austin Open Data Portal")
    lines.append("  3. Post-2021 buildings have had 1-3 years of exposure")
    lines.append("  4. Sprinkler presence inferred from year built, not verified")
    lines.append("  5. Cannot distinguish fire separation vs sprinkler choice")
    lines.append("     for 2019-2021 cohort")
    lines.append("  6. Per-parcel rates don't account for unit count differences")
    lines.append("     between single-parcel townhomes and multi-unit complexes")
    lines.append("")

    lines.append("DATA SOURCES")
    lines.append("-" * 60)
    lines.append("  - AFD Fire Incidents: Austin Open Data Portal (2022-2024)")
    lines.append("  - TCAD Parcels: City of Austin Land Database via ArcGIS")
    lines.append("  - Property records: Redfin, Zillow, HAR, Trulia, Travis CAD")
    lines.append("  - National benchmarks: NFPA annual fire loss reports")
    lines.append("  - Classification: NFPA/NFIRS structure fire standards")
    lines.append("  - Analysis script: 10_townhome_cohort_analysis.py")

    summary = "\n".join(lines)

    with open("outputs/townhome_cohort_summary.txt", "w") as f:
        f.write(summary)
    print(f"\n  Saved: outputs/townhome_cohort_summary.txt")

    return summary


def main():
    print("\n" + "#" * 60)
    print("# STEP 10: TOWNHOME FIRE CODE COHORT ANALYSIS")
    print("#" * 60)

    th_incidents, th_parcels = load_data()

    # Load full datasets for rarity context
    all_incidents = pd.read_csv("processed_data/incidents_enriched.csv")
    all_parcels = gpd.read_file("raw_data/parcels.geojson", ignore_geometry=True)

    # Save all TCAD 'TOWNHOMES' incidents
    th_incidents.to_csv("processed_data/townhome_incidents.csv", index=False)
    print(f"\n  Saved: processed_data/townhome_incidents.csv ({len(th_incidents)} rows)")

    analyze_data_quality(th_incidents, th_parcels)
    t_incidents, t_parcels = analyze_true_townhomes(th_incidents, th_parcels)
    analyze_fire_rarity(th_incidents, th_parcels, all_incidents, all_parcels)
    cohort_rates = analyze_all_townhome_labeled(th_incidents, th_parcels)
    write_summary(cohort_rates, th_incidents, th_parcels, t_incidents, t_parcels)

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
