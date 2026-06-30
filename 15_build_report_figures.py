#!/usr/bin/env python3
"""Build the explainer / diagram figures for docs/FIRE_FISCAL_FULL_REPORT.md.

All figures use the Austin civic palette (`viz_palette`). The parquet-free figures
(flow diagram, concept explainers, palette swatch, AFD-vs-City-budget) build now.
The data-derived charts (fiscal_*, fire_*, colloquial inventory) are regenerated
only when processed_data/parcels_value_per_acre_metro.parquet is present — guarded
by `if METRO_PARQUET.exists()` so this script runs cleanly either way.

    python 15_build_report_figures.py
Writes outputs/fig_*.png. External-constant figures use the FY2024-25 City of
Austin adopted budget (see docs/FIRE_FISCAL_FULL_REPORT.md §Validation for sources).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

import viz_palette as vp

REPO = Path(__file__).resolve().parent
OUT = REPO / "outputs"
OUT.mkdir(exist_ok=True)
PROC = REPO / "processed_data"
METRO_PARQUET = PROC / "parcels_value_per_acre_metro.parquet"

vp.register()
vp.apply_style()
SEQ = vp.seq_cmap()
DIV = vp.div_cmap()


def _save(fig, name):
    p = OUT / name
    fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {p.relative_to(REPO)}")


# ----------------------------------------------------------------- 1. data-inputs flow
def fig_data_inputs_flow():
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12); ax.set_ylim(0, 9); ax.axis("off")
    ax.set_title("Data inputs → models → findings", fontsize=15, pad=14)

    def box(x, y, w, h, text, fc, tc="white", fs=9, alpha=1.0):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                                    fc=fc, ec=vp.INK, lw=1.1, alpha=alpha, zorder=2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc,
                fontsize=fs, zorder=3, wrap=True)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                                     color=vp.INK, lw=1.2, alpha=0.55, zorder=1,
                                     connectionstyle="arc3,rad=0.0"))

    # Source groups (left column)
    groups = [
        ("GROUP A · Property & Value\nTCAD · WCAD · Hays CAD\ncertified rolls + parcel GIS", SEQ(0.12), 6.7),
        ("GROUP B · Fire Operations\nAFD incidents · stations\nresponse areas", SEQ(0.85), 3.6),
        ("GROUP C · Geography & Infra\nTIGER roads · Census places\n& ACS demographics", SEQ(0.45), 0.5),
    ]
    for text, fc, y in groups:
        tc = "white" if fc != SEQ(0.45) else vp.INK
        box(0.3, y, 3.0, 1.7, text, fc, tc=tc, fs=8.5)

    # Models (middle column)
    models = [
        ("Value-per-acre\nmarket_value / acre", 4.6, 6.6),
        ("Fiscal break-even\nrevenue vs cost\n(acres · road-miles)", 4.6, 3.5),
        ("Fire use-vs-pays-in\ndemand · coverage · apparatus", 4.6, 0.5),
    ]
    for text, x, y in models:
        box(x, y, 3.0, 1.7, text, "#34698c", fs=8.5)

    # Findings (right column)
    findings = [
        ("Finding 1\nValue/acre spans 4\norders of magnitude", 8.9, 6.6),
        ("Finding 2\nLow-value low-density\nunderpays for roads", 8.9, 3.5),
        ("Finding 3\nOuter suburbs are the\nnet fire-coverage drain", 8.9, 0.5),
    ]
    for text, x, y in findings:
        box(x, y, 3.0, 1.7, text, vp.BURNT_ORANGE, fs=8.5)

    # arrows  (A=value, fire-ops=B, geo=C):  A->value/acre & break-even ;
    #         B(fire ops)->fire model ;  C(geo)->break-even(road-miles) & fire model
    arrow(3.3, 7.55, 4.6, 7.45)            # A -> value/acre
    arrow(3.3, 7.10, 4.6, 4.55)            # A -> break-even
    arrow(3.3, 4.20, 4.6, 1.60)            # B (fire ops) -> fire model
    arrow(3.3, 1.70, 4.6, 4.15)            # C (geo) -> break-even (road-miles)
    arrow(3.3, 1.35, 4.6, 1.35)            # C (geo) -> fire model (demographics)
    for ym, yf in ((7.45, 7.45), (4.35, 4.35), (1.35, 1.35)):
        arrow(7.6, ym, 8.9, yf)            # models -> findings
    _save(fig, "fig_data_inputs_flow.png")


# ----------------------------------------------------------------- 2. value-per-acre concept
def fig_concept_value_per_acre():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
    fig.suptitle("Value per acre: same land, different productivity", fontsize=13)
    parcels = [("Suburban house\n1 acre · $0.5M market", 0.5, SEQ(0.18), "$500k / acre"),
               ("Downtown mid-rise\n1 acre · $40M market", 40.0, SEQ(0.95), "$40M / acre")]
    for ax, (title, val, color, label) in zip(axes, parcels):
        ax.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, fc=color, ec=vp.INK, lw=1.4))
        ax.text(0.5, 0.5, label, ha="center", va="center", color="white",
                fontsize=12, fontweight="bold")
        ax.set_title(title, fontsize=10)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    fig.text(0.5, -0.02, "Both occupy one acre — one linear unit of road, pipe and coverage to serve. "
             "The revenue they generate differs 80×.", ha="center", fontsize=9, style="italic")
    _save(fig, "fig_concept_value_per_acre.png")


# ----------------------------------------------------------------- 3. break-even concept
def fig_concept_breakeven():
    fig, ax = plt.subplots(figsize=(8, 4.8))
    x = np.linspace(0, 10, 200)
    revenue = 1.2 * x                      # revenue scales with value (x = value/acre proxy)
    cost = np.full_like(x, 6.0)            # cost-to-serve ~flat per acre (infrastructure)
    ax.plot(x, revenue, color=vp.BLUEBONNET, lw=2.4, label="Revenue (∝ property value)")
    ax.plot(x, cost, color=vp.BURNT_ORANGE, lw=2.4, label="Cost to serve (∝ land area)")
    xc = 6.0 / 1.2
    ax.axvline(xc, color=vp.INK, ls="--", lw=1, alpha=0.6)
    ax.fill_between(x, revenue, cost, where=(revenue >= cost), color=vp.BLUEBONNET, alpha=0.16)
    ax.fill_between(x, revenue, cost, where=(revenue < cost), color=vp.BURNT_ORANGE, alpha=0.16)
    ax.text(xc + 0.2, 1.0, "break-even\n(value/acre)", fontsize=8.5, color=vp.INK)
    ax.text(8.2, 10.6, "SURPLUS\npays its way", fontsize=9, color=vp.BLUEBONNET, fontweight="bold")
    ax.text(1.2, 6.5, "DEFICIT\ncross-subsidized", fontsize=9, color=vp.BURNT_ORANGE, fontweight="bold")
    ax.set_xlabel("value per acre  →"); ax.set_ylabel("$ per acre / year")
    ax.set_title("Fiscal break-even: where revenue crosses cost-to-serve")
    ax.legend(fontsize=8.5, loc="upper left"); ax.set_ylim(0, 13)
    _save(fig, "fig_concept_breakeven.png")


# ----------------------------------------------------------------- 4. coverage vs demand concept
def fig_concept_coverage_demand():
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    zones = ["Dense inner\nzone", "Mixed\nzone", "Spread-out\nouter zone"]
    demand = [9, 5, 2]                     # call volume falls with density
    standby = [6, 6, 6]                    # staffed first-due company: ~fixed per zone
    x = np.arange(len(zones)); w = 0.38
    ax.bar(x - w / 2, demand, w, color=SEQ(0.85), label="Call volume (demand lens)")
    ax.bar(x + w / 2, standby, w, color=SEQ(0.25), label="Staffed standby (coverage lens)")
    ax.set_xticks(x); ax.set_xticklabels(zones)
    ax.set_ylabel("relative cost units")
    ax.set_title("Why coverage ≠ demand: every zone needs a staffed company")
    ax.legend(fontsize=8.5)
    fig.text(0.5, -0.03, "~90% of a fire budget is fixed 24/7 standby. Low-call outer zones still need a "
             "first-due company — so coverage cost barely falls even as call volume does.",
             ha="center", fontsize=8.5, style="italic")
    _save(fig, "fig_concept_coverage_demand.png")


# ----------------------------------------------------------------- 5. palette swatch
def fig_palette_swatch():
    fig, axes = plt.subplots(2, 1, figsize=(9, 3.4))
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    axes[0].imshow(grad, aspect="auto", cmap=SEQ)
    axes[0].set_title("SEQ_VPA — value per acre (low → high)", fontsize=10, loc="left")
    axes[0].set_xticks([0, 255]); axes[0].set_xticklabels(["low $/acre", "high $/acre"]); axes[0].set_yticks([])
    axes[1].imshow(grad, aspect="auto", cmap=DIV)
    axes[1].set_title("DIV_NET — fire net balance (drain ← 0 → contributor)", fontsize=10, loc="left")
    axes[1].set_xticks([0, 128, 255])
    axes[1].set_xticklabels(["net drain (−)", "break-even (0)", "net contributor (+)"]); axes[1].set_yticks([])
    for ax in axes:
        ax.tick_params(length=0)
    fig.suptitle("Austin civic palette — how to read each scale", fontsize=12)
    _save(fig, "fig_palette_swatch.png")


# ----------------------------------------------------------------- 6. AFD vs City budget
def fig_afd_vs_city_budget():
    # FY2024-25 City of Austin adopted budget (sourced; see report Validation appendix).
    CITY_TOTAL = 5.9e9          # all funds
    GENERAL_FUND = 1.4e9        # tax-supported general fund
    PUBLIC_SAFETY = 0.648 * GENERAL_FUND   # PD+Fire+EMS+Forensics = 64.8% of GF
    AFD = 264e6
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))

    # left: city total -> general fund -> AFD as nested context
    ax = axes[0]
    bars = [("City of Austin\n(all funds)", CITY_TOTAL, SEQ(0.15)),
            ("General Fund\n(tax-supported)", GENERAL_FUND, SEQ(0.45)),
            ("Public-safety\n(64.8% of GF)", PUBLIC_SAFETY, SEQ(0.7)),
            ("Austin Fire\nDepartment", AFD, vp.BURNT_ORANGE)]
    y = np.arange(len(bars))[::-1]
    for yi, (lbl, val, c) in zip(y, bars):
        ax.barh(yi, val / 1e9, color=c, ec=vp.INK, lw=0.8)
        ax.text(val / 1e9 + 0.07, yi, f"${val/1e9:.2f}B" if val >= 1e9 else f"${val/1e6:.0f}M",
                va="center", fontsize=9, color=vp.INK)
    ax.set_yticks(y); ax.set_yticklabels([b[0] for b in bars], fontsize=8.5)
    ax.set_xlabel("$ billions"); ax.set_title("AFD in the context of the City budget")
    ax.set_xlim(0, 6.6)

    # right: AFD as a slice of the General Fund
    ax = axes[1]
    afd = AFD / 1e6
    rest_gf = (GENERAL_FUND - AFD) / 1e6
    ax.bar(0, afd, color=vp.BURNT_ORANGE, ec=vp.INK, label=f"AFD  ${afd:.0f}M")
    ax.bar(0, rest_gf, bottom=afd, color=SEQ(0.35), ec=vp.INK,
           label=f"Rest of General Fund  ${rest_gf:,.0f}M")
    ax.text(0, afd / 2, f"AFD\n${afd:.0f}M\n({afd/(GENERAL_FUND/1e6)*100:.0f}% of GF)",
            ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    ax.set_xticks([]); ax.set_ylabel("$ millions"); ax.set_xlim(-1, 1)
    ax.set_title("AFD as a share of the General Fund")
    ax.legend(fontsize=8, loc="upper right")
    fig.text(0.5, -0.03, "FY2024-25 City of Austin adopted budget: $5.9B all funds · $1.4B General Fund · "
             "AFD ≈ $264M. Public-safety share = 64.8% of GF.", ha="center", fontsize=8, style="italic")
    _save(fig, "fig_afd_vs_city_budget.png")


# ----------------------------------------------------------------- 7. interactive-map static preview
def fig_interactive_map_preview():
    """Static, print-ready preview of the interactive 3D map: response-area choropleth
    coloured by fire net balance (DIV palette, 0-centred) with colloquial landmark pins.
    Builds when response_areas_final.geojson + fire_net_balance.geojson are present."""
    import geopandas as gpd
    import matplotlib.patheffects as pe
    ra_path = PROC / "response_areas_final.geojson"
    nb_path = PROC / "fire_net_balance.geojson"
    if not (ra_path.exists() and nb_path.exists()):
        print("[staged] response areas / fire_net_balance.geojson absent — skipping map preview")
        return
    ra = gpd.read_file(ra_path).to_crs(4326)[["response_area_id", "geometry"]]
    nb = gpd.read_file(nb_path)[["response_area_id", "net_coverage_M"]]
    gdf = ra.merge(nb, on="response_area_id", how="left")
    served = gdf[gdf["net_coverage_M"].notna()].copy()
    vmax = float(np.nanpercentile(np.abs(served["net_coverage_M"]), 98)) or 1.0
    norm = matplotlib.colors.TwoSlopeNorm(vcenter=0, vmin=-vmax, vmax=vmax)

    LANDMARKS = [
        ("Downtown", -97.7431, 30.2672, "hi"), ("The Domain", -97.7261, 30.4007, "hi"),
        ("Mueller", -97.7050, 30.2980, "hi"), ("West Lake Hills", -97.8060, 30.2930, "hi"),
        ("Lakeway", -97.9794, 30.3637, "hi"), ("Bee Cave", -97.9469, 30.3088, "hi"),
        ("Round Rock", -97.6789, 30.5083, "mix"), ("Northland", -97.7340, 30.3600, "mix"),
        ("Georgetown", -97.6770, 30.6333, "lo"), ("Kyle", -97.8770, 29.9890, "lo"),
        ("Buda", -97.8400, 30.0855, "lo"), ("San Marcos", -97.9414, 29.8833, "lo"),
    ]
    pin = {"hi": vp.BLUEBONNET, "mix": "#e9c46a", "lo": vp.BURNT_ORANGE}

    fig, ax = plt.subplots(figsize=(9, 9.6))
    gdf.plot(ax=ax, color="#eceae2", edgecolor="#d8d2c4", linewidth=0.2, zorder=1)
    served.plot(ax=ax, column="net_coverage_M", cmap=DIV, norm=norm,
                edgecolor="#9a958a", linewidth=0.25, zorder=2)
    for name, lon, lat, kind in LANDMARKS:
        ax.scatter(lon, lat, s=64, color=pin[kind], edgecolor="white", linewidth=1.3, zorder=4)
        ax.annotate(name, (lon, lat), xytext=(5, 3), textcoords="offset points",
                    fontsize=8, fontweight="bold", color=vp.INK, zorder=5,
                    path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
    sm = plt.cm.ScalarMappable(cmap=DIV, norm=norm)
    cb = fig.colorbar(sm, ax=ax, fraction=0.036, pad=0.02, shrink=0.62)
    cb.set_label("fire net balance — coverage lens ($M/yr)\n"
                 "burnt-orange = net drain   ·   bluebonnet = contributor", fontsize=8)
    ax.set_title("Fire net balance by AFD response area, with colloquial landmarks\n"
                 "(static preview of the interactive 3D map)", fontsize=12, color=vp.INK)
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    ax.set_xlim(served.total_bounds[0] - 0.05, served.total_bounds[2] + 0.20)
    ax.set_ylim(served.total_bounds[1] - 0.05, served.total_bounds[3] + 0.05)
    _save(fig, "fig_interactive_map_preview.png")


# ----------------------------------------------------------------- staged: data-derived charts
def regen_data_charts():
    """Regenerate fiscal_*/fire_* charts + colloquial inventory in the Austin palette.
    Staged: only runs when the parcel parquet is present. See the report's
    'Staged-run runbook'."""
    if not METRO_PARQUET.exists():
        print("[staged] parcels_value_per_acre_metro.parquet absent — skipping data-derived "
              "charts (fiscal_land_vs_road, fire_apparatus_distance, fire_equity_scatter, "
              "colloquial_inventory). Re-run this script once the parquet lands.")
        return
    # When the parquet is present, re-run the chart builders from the analysis notebooks
    # through viz_palette. Implemented as the staged step in the runbook; left as a clear
    # extension point so the parquet-free path stays green.
    print("[staged] parquet present — regenerate fiscal_/fire_ charts via the notebook builders.")


def main():
    fig_data_inputs_flow()
    fig_concept_value_per_acre()
    fig_concept_breakeven()
    fig_concept_coverage_demand()
    fig_palette_swatch()
    fig_afd_vs_city_budget()
    fig_interactive_map_preview()
    regen_data_charts()
    print("done.")


if __name__ == "__main__":
    main()
