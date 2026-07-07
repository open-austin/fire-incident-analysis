#!/usr/bin/env python3
"""Parse a TCAD certified appraisal roll (PACS fixed-width PROP.TXT) -> prop_id values.

The full certified roll is published free by TCAD as a fixed-width PACS export
(the per-property values behind the web portal are gated, but the bulk roll is not).
Download it, point this at its PROP.TXT, and it writes processed_data/tcad_<year>_values.parquet
with one row per property: prop_id, market_value, appraised_val, legal_acreage.

Layout (1-based, PACS export ~8.0.0.x): prop_id 1-12, legal_acreage 1660-1675 (4 implied
decimals), appraised_val 1916-1930, assessed_val 1946-1960, market_value 4214-4227.
ALWAYS validate against APPR_HDR.TXT (year + version) and a known parcel — PACS versions
can shift byte offsets. Re-certifies every mid-July (Tex. Property Tax Code 26.01); use the
CERTIFIED roll, not the spring preliminary.

Usage:  python 12_parse_tcad_roll.py "/path/to/PROP.TXT" 2025
"""
import sys
from pathlib import Path
import pandas as pd

# 0-based slices derived from the 1-based PACS layout
SLICES = {
    "prop_id": (0, 12),
    "legal_acreage": (1659, 1675),   # /10000 for acres
    "appraised_val": (1915, 1930),
    "market_value": (4213, 4227),
}


def parse(path):
    rows = {}
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("latin-1")
            pid = line[0:12].strip()
            if not pid.isdigit():
                continue
            pid = int(pid)
            if pid in rows:                 # one row per property+owner; values repeat
                continue
            mv = line[4213:4227].strip()
            ap = line[1915:1930].strip()
            ac = line[1659:1675].strip()
            rows[pid] = (
                int(mv) if mv.isdigit() else 0,
                int(ap) if ap.isdigit() else 0,
                (int(ac) / 10000.0) if ac.isdigit() else 0.0,
            )
    return pd.DataFrame(
        [(k, *v) for k, v in rows.items()],
        columns=["prop_id", "market_value", "appraised_val", "legal_acreage"],
    )


if __name__ == "__main__":
    prop_txt = sys.argv[1]
    year = sys.argv[2] if len(sys.argv) > 2 else "latest"
    out = Path(__file__).resolve().parent.parent / "processed_data" / f"tcad_{year}_values.parquet"
    df = parse(prop_txt)
    df.to_parquet(out)
    valued = df[df.market_value > 0]
    print(f"{len(df):,} properties; market>0={len(valued):,}; median market=${valued.market_value.median():,.0f}")
    print(f"wrote {out}")
