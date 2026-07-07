#!/usr/bin/env python3
"""
Step 9: Human-Readable Zoning + Census Tract Enrichment
=========================================================
Adds human-readable zoning descriptions and joins each incident
to its census tract, bringing in population and housing data.

Usage:
    python 09_zoning_and_census.py

Input:
    processed_data/incidents_with_parcels.csv
    raw_data/tl_2023_48_tract/tl_2023_48_tract.shp  (TIGER census tracts)
    raw_data/census_population.csv
    raw_data/census_housing.csv
    raw_data/census_year_built.csv

Output:
    processed_data/incidents_enriched.csv
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import warnings

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Austin zoning base code → human-readable name
# Source: City of Austin Land Development Code, Title 25
# ---------------------------------------------------------------------------
ZONING_BASE_LABELS = {
    "SF":  "Single Family Residential",
    "MF":  "Multifamily Residential",
    "GR":  "Community Commercial",
    "CS":  "General Commercial Services",
    "P":   "Public",
    "LI":  "Limited Industrial",
    "PUD": "Planned Unit Development",
    "ERC": "East Riverside Corridor",
    "CBD": "Central Business District",
    "LR":  "Neighborhood Commercial",
    "LO":  "Limited Office",
    "NBG": "North Burnet/Gateway",
    "GO":  "General Office",
    "RR":  "Rural Residential",
    "TOD": "Transit Oriented Development",
    "CH":  "Commercial Highway",
    "AV":  "Aviation Services",
    "MH":  "Manufactured Housing",
    "DR":  "Development Reserve",
    "UNZ": "Unzoned",
    "DMU": "Downtown Mixed Use",
    "IP":  "Industrial Park",
    "MI":  "Major Industry",
    "AG":  "Agricultural",
    "LA":  "Lake Austin Residential",
    "NO":  "Neighborhood Office",
    "W/LO": "Waterfront/Limited Office",
}

# Zoning modifier suffixes → short description
ZONING_MODIFIERS = {
    "NP":  "Neighborhood Plan",
    "CO":  "Conditional Overlay",
    "MU":  "Mixed Use",
    "V":   "Vertical Mixed Use",
    "PDA": "Planned Development Area",
}

# Broader zoning category for analysis grouping
ZONING_CATEGORY_MAP = {
    "SF":  "Residential",
    "MF":  "Residential",
    "RR":  "Residential",
    "MH":  "Residential",
    "LA":  "Residential",
    "GR":  "Commercial",
    "CS":  "Commercial",
    "LR":  "Commercial",
    "CH":  "Commercial",
    "CBD": "Commercial",
    "LO":  "Office",
    "GO":  "Office",
    "NO":  "Office",
    "W/LO": "Office",
    "LI":  "Industrial",
    "IP":  "Industrial",
    "MI":  "Industrial",
    "P":   "Public/Institutional",
    "AV":  "Public/Institutional",
    "PUD": "Mixed/Planned",
    "ERC": "Mixed/Planned",
    "NBG": "Mixed/Planned",
    "TOD": "Mixed/Planned",
    "DMU": "Mixed/Planned",
    "DR":  "Other",
    "UNZ": "Other",
    "AG":  "Other",
}

# ACS table B25024: Units in Structure
HOUSING_COLS = {
    "B25024_001E": "housing_total_units",
    "B25024_002E": "housing_1_detached",
    "B25024_003E": "housing_1_attached",
    "B25024_004E": "housing_2_units",
    "B25024_005E": "housing_3_4_units",
    "B25024_006E": "housing_5_9_units",
    "B25024_007E": "housing_10_19_units",
    "B25024_008E": "housing_20_49_units",
    "B25024_009E": "housing_50plus_units",
    "B25024_010E": "housing_mobile_home",
    "B25024_011E": "housing_boat_rv_van",
}

# ACS table B25034: Year Structure Built
YEAR_BUILT_COLS = {
    "B25034_001E": "yrbuilt_total",
    "B25034_002E": "yrbuilt_2020_later",
    "B25034_003E": "yrbuilt_2010_2019",
    "B25034_004E": "yrbuilt_2000_2009",
    "B25034_005E": "yrbuilt_1990_1999",
    "B25034_006E": "yrbuilt_1980_1989",
    "B25034_007E": "yrbuilt_1970_1979",
    "B25034_008E": "yrbuilt_1960_1969",
    "B25034_009E": "yrbuilt_1950_1959",
    "B25034_010E": "yrbuilt_1940_1949",
    "B25034_011E": "yrbuilt_1939_earlier",
}


def build_zoning_label(ztype, base):
    """Build a human-readable label from ZONING_ZTYPE and ZONING_BASE."""
    if pd.isna(base):
        return None

    base = str(base).strip()

    # Handle interim zoning (I- prefix)
    interim = False
    effective_base = base
    if base.startswith("I-"):
        interim = True
        effective_base = base[2:]

    label = ZONING_BASE_LABELS.get(effective_base, effective_base)
    if interim:
        label = f"Interim {label}"

    # Parse modifiers from ZONING_ZTYPE
    if pd.notna(ztype):
        ztype_str = str(ztype).strip()
        modifiers = []
        for code, desc in ZONING_MODIFIERS.items():
            if f"-{code}" in ztype_str:
                modifiers.append(desc)
        if modifiers:
            label += f" ({', '.join(modifiers)})"

    return label


def add_zoning_labels(df):
    """Add human-readable zoning columns to the dataframe."""
    print("\nAdding human-readable zoning labels...")

    df["zoning_label"] = df.apply(
        lambda r: build_zoning_label(r["ZONING_ZTYPE"], r["ZONING_BASE"]), axis=1
    )

    # Strip I- prefix for category lookup
    def get_base(b):
        if pd.isna(b):
            return None
        b = str(b).strip()
        if b.startswith("I-"):
            b = b[2:]
        return b

    df["zoning_category"] = df["ZONING_BASE"].apply(
        lambda b: ZONING_CATEGORY_MAP.get(get_base(b)) if pd.notna(b) else None
    )

    labeled = df["zoning_label"].notna().sum()
    print(f"  Labeled {labeled:,} / {len(df):,} incidents with zoning descriptions")

    print("\n  Zoning category distribution:")
    print(df["zoning_category"].value_counts().to_string(header=False))

    return df


def join_census_tracts(df):
    """Spatially join incidents to census tracts."""
    print("\nJoining incidents to census tracts...")

    # Load TIGER tract boundaries
    tracts = gpd.read_file("raw_data/tl_2023_48_tract/tl_2023_48_tract.shp")

    # Filter to Travis County (453) plus Hays (209) and Williamson (491)
    # to catch incidents near county borders
    tracts = tracts[tracts["COUNTYFP"].isin(["453", "209", "491"])].copy()
    tracts = tracts[["GEOID", "TRACTCE", "COUNTYFP", "NAME", "ALAND", "geometry"]]
    print(f"  Loaded {len(tracts):,} census tracts (Travis/Hays/Williamson)")

    # Ensure same CRS
    if tracts.crs.to_epsg() != 4326:
        tracts = tracts.to_crs("EPSG:4326")

    # Create incident points
    valid = df.dropna(subset=["latitude", "longitude"])
    geometry = [Point(lon, lat) for lon, lat in zip(valid["longitude"], valid["latitude"])]
    incidents_gdf = gpd.GeoDataFrame(valid, geometry=geometry, crs="EPSG:4326")

    # Spatial join
    joined = gpd.sjoin(incidents_gdf, tracts, how="left", predicate="within")
    if "index_right" in joined.columns:
        joined = joined.drop(columns=["index_right"])

    matched = joined["GEOID"].notna().sum()
    print(f"  Matched {matched:,} / {len(joined):,} incidents to census tracts")

    # Rename tract columns for clarity
    joined = joined.rename(columns={
        "GEOID": "census_tract_geoid",
        "NAME": "census_tract_name",
        "COUNTYFP": "census_county_fips",
        "ALAND": "census_tract_land_area_sqm",
    })
    joined = joined.drop(columns=["TRACTCE", "geometry"], errors="ignore")

    # Merge back rows that had no coordinates
    no_coords = df[df["latitude"].isna() | df["longitude"].isna()]
    if len(no_coords) > 0:
        for col in ["census_tract_geoid", "census_tract_name",
                     "census_county_fips", "census_tract_land_area_sqm"]:
            no_coords[col] = None
        joined = pd.concat([pd.DataFrame(joined), pd.DataFrame(no_coords)], ignore_index=True)

    return pd.DataFrame(joined)


def join_census_demographics(df):
    """Join census population, housing, and year-built data by tract."""
    print("\nJoining census demographic data...")

    # Build GEOID from census CSV columns: state(2) + county(3) + tract(6)
    def load_census(path, col_map):
        raw = pd.read_csv(path, dtype={"state": str, "county": str, "tract": str})
        raw["census_tract_geoid"] = raw["state"] + raw["county"] + raw["tract"]
        rename = {k: v for k, v in col_map.items() if k in raw.columns}
        raw = raw.rename(columns=rename)
        keep = ["census_tract_geoid"] + list(rename.values())
        return raw[keep]

    # Population
    pop = pd.read_csv(
        "raw_data/census_population.csv",
        dtype={"state": str, "county": str, "tract": str},
    )
    pop["census_tract_geoid"] = pop["state"] + pop["county"] + pop["tract"]
    pop = pop.rename(columns={"B01003_001E": "census_population"})
    pop = pop[["census_tract_geoid", "census_population"]]
    print(f"  Population data: {len(pop)} tracts")

    # Housing (units in structure)
    housing = load_census("raw_data/census_housing.csv", HOUSING_COLS)
    print(f"  Housing data: {len(housing)} tracts")

    # Year built
    year_built = load_census("raw_data/census_year_built.csv", YEAR_BUILT_COLS)
    print(f"  Year built data: {len(year_built)} tracts")

    # Merge all census data together
    census = pop.merge(housing, on="census_tract_geoid", how="outer")
    census = census.merge(year_built, on="census_tract_geoid", how="outer")

    # Join to incidents
    before_cols = len(df.columns)
    df = df.merge(census, on="census_tract_geoid", how="left")
    new_cols = len(df.columns) - before_cols
    matched = df["census_population"].notna().sum()
    print(f"  Added {new_cols} census columns")
    print(f"  {matched:,} incidents matched to census demographics")

    return df


def main():
    print("\n" + "#" * 60)
    print("# STEP 9: ZONING LABELS + CENSUS TRACT ENRICHMENT")
    print("#" * 60)

    # Load parcel-joined incidents
    print("\nLoading incidents with parcel data...")
    df = pd.read_csv("processed_data/incidents_with_parcels.csv")
    print(f"  {len(df):,} incidents loaded")

    # 1. Human-readable zoning
    df = add_zoning_labels(df)

    # 2. Census tract spatial join
    df = join_census_tracts(df)

    # 3. Census demographics
    df = join_census_demographics(df)

    # 4. Save
    output_path = "processed_data/incidents_enriched.csv"
    print(f"\nSaving to {output_path}...")
    df.to_csv(output_path, index=False)
    print(f"  {len(df):,} rows, {len(df.columns)} columns")

    # 5. Summary
    print("\n" + "=" * 60)
    print("ENRICHMENT SUMMARY")
    print("=" * 60)

    print(f"\nTotal incidents: {len(df):,}")

    zoned = df["zoning_label"].notna().sum()
    print(f"With zoning labels: {zoned:,} ({zoned/len(df)*100:.1f}%)")

    tract_matched = df["census_tract_geoid"].notna().sum()
    print(f"Matched to census tract: {tract_matched:,} ({tract_matched/len(df)*100:.1f}%)")

    pop_matched = df["census_population"].notna().sum()
    print(f"With census demographics: {pop_matched:,} ({pop_matched/len(df)*100:.1f}%)")

    print("\nSample zoning labels:")
    sample = df[df["zoning_label"].notna()][
        ["ZONING_ZTYPE", "ZONING_BASE", "zoning_label", "zoning_category"]
    ].drop_duplicates(subset=["ZONING_ZTYPE"]).head(15)
    print(sample.to_string(index=False))

    print("\nCensus tract population stats (for matched incidents):")
    pop_stats = df["census_population"].describe()
    print(pop_stats.to_string())

    print(f"\nDone! Output: {output_path}")


if __name__ == "__main__":
    main()
