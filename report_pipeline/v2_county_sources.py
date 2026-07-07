#!/usr/bin/env python3
"""
v2 metro parcel sources — Travis + Williamson + Hays
====================================================
Verified config for the value-per-acre metro map (v2). Every county exposes a
public ArcGIS FeatureServer/MapServer that bundles market value + geometry +
acreage + land use, so NO appraisal-roll join is needed.

All three endpoints + field names live-verified 2026-06-29 (counts below).
Run this module directly to re-verify counts:  python v2_county_sources.py

The downstream pipeline maps each county's native fields to one canonical schema:
    county, parcel_id, market_value, land_value, improvement_value,
    taxable_value, land_acres, land_use, geometry
"""

# Each entry: the query endpoint, and field_map = {canonical: native}.
# `casts` lists canonical columns whose native field is a STRING and must be
# coerced to float. `notes` flags per-county gotchas.
COUNTY_SOURCES = {
    "travis": {
        # Already pulled in v1 via 07_parcel_join.py (City of Austin Land Database).
        "url": (
            "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/"
            "2023_Land_Database_Dash_View/FeatureServer/93/query"
        ),
        "approx_count": 230_000,
        "field_map": {
            "parcel_id": "PARCEL_ID",
            "market_value": "MARKET_VALUE",
            "taxable_value": "APPRAISED_VAL",
            "land_acres": "LAND_ACRES",
            "land_use": "IMPRV_TYPE",
        },
        "casts": [],
        "notes": "Reuse v1 download; MARKET_VALUE for value map, APPRAISED_VAL for tax map.",
    },
    "williamson": {
        "url": (
            "https://gis.wilco.org/arcgis/rest/services/public/"
            "county_wcad_parcels/MapServer/0/query"
        ),
        "approx_count": 287_057,
        "field_map": {
            "parcel_id": "PARCELID",
            "market_value": "TotalPropMktValue",
            "land_value": "TotalLandMktValue",
            "land_acres": "AssessedAc",   # STRING -> cast
            "land_use": "USEDSCRP",
        },
        "casts": ["land_acres"],
        "notes": "Acres/AssessedAc are strings; LNDVALUE is 0/unreliable, use TotalLandMktValue.",
    },
    "hays": {
        "url": (
            "https://services5.arcgis.com/bVphnK8rPe5MHUSr/arcgis/rest/services/"
            "Hays_County_Parcels/FeatureServer/0/query"
        ),
        "approx_count": 120_913,
        "field_map": {
            "parcel_id": "prop_id",
            "market_value": "market",
            "land_value": "land_val",
            "improvement_value": "imprv_val",
            "land_acres": "legal_acreage",
        },
        "casts": [],
        "notes": (
            "Use the services5 layer (countygis.DBO.Parcels), NOT the stale "
            "urbaneng 'Hays County 2020' geometry-only layer. market != land+imprv "
            "(ag/exemption capping) — use `market` directly."
        ),
    },
}

# TX Comptroller Appraisal District Ratio Study — median appraisal-to-sale ratio,
# Category A (single-family residential). Used for cross-county comparability:
#   value_per_acre_adj = (market_value / pvs_ratio) / land_acres
# Source: comptroller.texas.gov/auto-data/PT2/ratio-study/<YEAR>/<CAD>0000001A.php
# CAD county codes: Travis=227, Williamson=246, Hays=105 (NOT the ratio-study URL's
# Taylor=221 — verify the rendered "NNN-Name" heading, it's JS-injected).
# The ADRS alternates counties biennially, so each is its most recent POPULATED study.
# Category A median level of appraisal. Cross-verified 2026-06-29 by two independent
# methods (XHR scrape + headless Chromium render); page headings confirmed the CAD.
PVS_RATIOS = {
    "travis": 1.00,      # 2024 ADRS, 227-Travis      (Cat A=1.00 / overall=1.00, n=4,732)
    "williamson": 0.96,  # 2024 ADRS, 246-Williamson  (Cat A=0.96 / overall=0.96, n=3,670)
    "hays": 0.97,        # 2022 ADRS, 105-Hays         (Cat A=0.97 / overall=0.97, n=1,706)
}

# Canonical schema the pipeline normalizes every county into.
CANONICAL_COLUMNS = [
    "county", "parcel_id", "market_value", "land_value", "improvement_value",
    "taxable_value", "land_acres", "land_use", "geometry",
]


def _verify():
    """Read-only sanity check: hit each endpoint for a feature count (stdlib only)."""
    import json
    import urllib.parse
    import urllib.request

    for county, cfg in COUNTY_SOURCES.items():
        try:
            qs = urllib.parse.urlencode(
                {"where": "1=1", "returnCountOnly": "true", "f": "json"}
            )
            with urllib.request.urlopen(f"{cfg['url']}?{qs}", timeout=60) as resp:
                count = json.load(resp).get("count", "?")
            flag = "" if count == "?" else ("OK" if abs(count - cfg["approx_count"]) / cfg["approx_count"] < 0.2 else "DRIFT")
            print(f"  {county:11s} count={count:>9} (expected ~{cfg['approx_count']:,})  {flag}")
        except Exception as e:
            print(f"  {county:11s} FAILED: {e}")


if __name__ == "__main__":
    print("Verifying v2 metro parcel sources (Travis + Williamson + Hays)...")
    _verify()
