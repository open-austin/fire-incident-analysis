#!/usr/bin/env python3
"""
v2 generalized parcel fetcher — Travis + Williamson + Hays
==========================================================
One paginated ArcGIS reader that works for all three counties off the verified
COUNTY_SOURCES config, normalizing native fields to the canonical schema.

Design: the core (`fetch_county_records`) is **stdlib-only** so it runs and can be
smoke-tested anywhere (no geopandas/requests needed). `fetch_county_gdf` is a thin
wrapper that builds a GeoDataFrame when geopandas is installed — that's the call the
v1 helper module / metro notebook will use. Folding this into the v1 helper later is
a rename, not a rewrite.

    python v2_fetch_parcels.py          # live smoke test: ~25 parcels/county
"""
import json
import urllib.parse
import urllib.request

from v2_county_sources import COUNTY_SOURCES, PVS_RATIOS


def _query(url, params):
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{qs}", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def fetch_county_records(county, limit=None, page_size=2000,
                         only_valued=True, with_geometry=True, bbox=None):
    """Paginated fetch of one county's parcels, normalized to the canonical schema.

    Returns a list of dicts: canonical attribute keys + 'county' + (optional)
    'geometry' (GeoJSON geometry). Stdlib only — no geopandas/requests.

    bbox: optional (xmin, ymin, xmax, ymax) in lon/lat (EPSG:4326). When given,
    only parcels intersecting that envelope are returned — used for fast,
    geographically-bounded slices (e.g. downtown) before a full-county pull.
    """
    cfg = COUNTY_SOURCES[county]
    field_map = cfg["field_map"]            # {canonical: native}
    native_fields = list(field_map.values())
    inv = {v: k for k, v in field_map.items()}
    casts = set(cfg.get("casts", []))

    where = "1=1"
    if only_valued:
        where = f"{field_map['market_value']} > 0"

    records, offset = [], 0
    while True:
        params = {
            "where": where,
            "outFields": ",".join(native_fields),
            "outSR": "4326",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page_size,
            "returnGeometry": "true" if with_geometry else "false",
        }
        if bbox is not None:
            xmin, ymin, xmax, ymax = bbox
            params.update({
                "geometry": f"{xmin},{ymin},{xmax},{ymax}",
                "geometryType": "esriGeometryEnvelope",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
            })
        data = _query(cfg["url"], params)
        feats = data.get("features", [])
        if not feats:
            break
        for ft in feats:
            props = ft.get("properties", {})
            rec = {"county": county}
            for native, val in props.items():
                canon = inv.get(native)
                if canon is None:
                    continue
                if canon in casts and val not in (None, ""):
                    try:
                        val = float(val)
                    except (TypeError, ValueError):
                        val = None
                rec[canon] = val
            if with_geometry:
                rec["geometry"] = ft.get("geometry")
            records.append(rec)
            if limit and len(records) >= limit:
                return records
        offset += len(feats)
        if len(feats) < page_size:
            break
    return records


def value_per_acre(rec):
    mv, ac = rec.get("market_value"), rec.get("land_acres")
    if not mv or not ac or ac <= 0:
        return None
    return mv / ac


def value_per_acre_adj(rec):
    """Sales-ratio-normalized $/acre for cross-county comparability."""
    vpa = value_per_acre(rec)
    ratio = PVS_RATIOS.get(rec["county"])
    if vpa is None or not ratio:
        return None
    return vpa / ratio


def fetch_county_gdf(county, **kwargs):
    """GeoDataFrame variant for the pipeline (requires geopandas)."""
    import geopandas as gpd
    from shapely.geometry import shape

    kwargs.setdefault("with_geometry", True)
    recs = fetch_county_records(county, **kwargs)
    for r in recs:
        r["geometry"] = shape(r["geometry"]) if r.get("geometry") else None
    return gpd.GeoDataFrame(recs, geometry="geometry", crs="EPSG:4326")


if __name__ == "__main__":
    print("Live smoke test — fetch + normalize ~25 valued parcels per county\n")
    for county in COUNTY_SOURCES:
        try:
            recs = fetch_county_records(county, limit=25, with_geometry=True)
        except Exception as e:
            print(f"{county}: FAILED — {e}\n")
            continue
        canon_keys = sorted({k for r in recs for k in r if k != "geometry"})
        has_geom = sum(1 for r in recs if r.get("geometry"))
        vpas = [value_per_acre(r) for r in recs]
        vpas = [v for v in vpas if v]
        sample = recs[0]
        print(f"== {county.upper()} ==")
        print(f"  fetched={len(recs)}  geom={has_geom}/{len(recs)}  canonical keys={canon_keys}")
        if vpas:
            print(f"  $/acre: min={min(vpas):,.0f}  median={sorted(vpas)[len(vpas)//2]:,.0f}  max={max(vpas):,.0f}")
        print(f"  sample: pid={sample.get('parcel_id')} mkt=${sample.get('market_value'):,} "
              f"acres={sample.get('land_acres')} adj$/ac={value_per_acre_adj(sample):,.0f}\n")
    print("If all three print sane $/acre values, the config + fetcher are wired correctly.")
