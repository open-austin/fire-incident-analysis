#!/usr/bin/env python3
"""Build the metro parcel set for the value-per-acre + fiscal-productivity analyses.

Travis = TCAD public GIS geometry (PROP_ID, situs_city, tcad_acres) joined to the parsed
certified-roll values (12_parse_tcad_roll.py) by PROP_ID. Williamson + Hays come from their
CAD ArcGIS FeatureServers (v2_fetch_parcels). Output: processed_data/parcels_value_per_acre_metro.parquet
(one row per parcel: county, parcel_id, market_value, taxable_value, land_acres, land_use,
situs_city, value_per_acre, value_per_acre_adj, tax_per_acre, geometry).

Prereqs (all gitignored, fetched once):
  - processed_data/tcad_gis_travis.parquet     (TCAD_public/MapServer/0, ~386k parcels)
  - processed_data/tcad_<year>_values.parquet  (from 12_parse_tcad_roll.py)
  - the prior metro parquet, for the Williamson + Hays rows (or re-fetch via v2_fetch_parcels)
"""
import os, sys, warnings
warnings.filterwarnings("ignore")
import geopandas as gpd
import pandas as pd

PROC = os.path.join(os.path.dirname(__file__), "processed_data")
MIN_ACRES = 0.01
EFFECTIVE_TAX_RATE = 0.021
PVS = {"travis": 1.00, "williamson": 0.96, "hays": 0.97}   # sales ratios for cross-county adj
COLS = ["county", "parcel_id", "market_value", "taxable_value", "land_acres",
        "land_use", "situs_city", "geometry"]


def build_travis(values_parquet):
    gis = gpd.read_parquet(f"{PROC}/tcad_gis_travis.parquet")
    gis["parcel_id"] = pd.to_numeric(gis["parcel_id"], errors="coerce")
    vals = pd.read_parquet(values_parquet).rename(columns={"prop_id": "parcel_id"})
    tr = gis.merge(vals, on="parcel_id", how="inner")
    tr["tcad_acres"] = pd.to_numeric(tr["tcad_acres"], errors="coerce")
    geom_ac = (tr.to_crs(2277).geometry.area / 43560.0).values
    acres = tr["tcad_acres"].where(tr["tcad_acres"] > 0)
    acres = acres.fillna(pd.Series(tr["legal_acreage"].where(tr["legal_acreage"] > 0).values, index=tr.index))
    acres = acres.fillna(pd.Series(geom_ac, index=tr.index))
    tr["land_acres"] = acres
    tr["county"] = "travis"
    tr["market_value"] = pd.to_numeric(tr["market_value"], errors="coerce")
    tr["taxable_value"] = pd.to_numeric(tr["appraised_val"], errors="coerce")
    tr["land_use"] = None
    return tr[COLS]


def main(values_parquet, prior_metro):
    travis = build_travis(values_parquet)
    print(f"travis: {len(travis):,}")
    wh = gpd.read_parquet(prior_metro)
    wh = wh[wh["county"].isin(["williamson", "hays"])].copy()
    for c in COLS:
        if c not in wh.columns:
            wh[c] = None
    wh = wh[COLS]
    print(f"williamson+hays: {len(wh):,}")

    g = gpd.GeoDataFrame(pd.concat([travis, wh], ignore_index=True), crs="EPSG:4326")
    g = g[g.geometry.notna()].copy()
    g["land_acres"] = pd.to_numeric(g["land_acres"], errors="coerce")
    g["market_value"] = pd.to_numeric(g["market_value"], errors="coerce")
    g = g[(g["land_acres"] >= MIN_ACRES) & (g["market_value"] > 0)]
    g["value_per_acre"] = g["market_value"] / g["land_acres"]
    g = g[g["value_per_acre"].between(1, 1e12)]
    g["pvs_ratio"] = g["county"].map(PVS)
    g["value_per_acre_adj"] = g["value_per_acre"] / g["pvs_ratio"]
    g["tax_per_acre"] = pd.to_numeric(g["taxable_value"], errors="coerce") * EFFECTIVE_TAX_RATE / g["land_acres"]
    g["parcel_id"] = g["parcel_id"].astype(str)

    out = f"{PROC}/parcels_value_per_acre_metro.parquet"
    g.to_parquet(out)
    print(f"clean total: {len(g):,}")
    print(g.groupby("county").size().to_string())
    print(f"wrote {out} ({os.path.getsize(out)/1e6:.0f} MB)")


if __name__ == "__main__":
    # argv: <tcad_values.parquet> <prior_metro.parquet>
    vp = sys.argv[1] if len(sys.argv) > 1 else f"{PROC}/tcad_2025_values.parquet"
    pm = sys.argv[2] if len(sys.argv) > 2 else f"{PROC}/parcels_value_per_acre_metro.parquet"
    main(vp, pm)
