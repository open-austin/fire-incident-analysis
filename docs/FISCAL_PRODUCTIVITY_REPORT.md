# Who Pays for Growth? Value, Infrastructure, and Fire Service Across the Austin Metro

> **Superseded.** This standalone write-up has been folded into the master report: see [FIRE_FISCAL_FULL_REPORT.md](FIRE_FISCAL_FULL_REPORT.md).

**Prepared by:** Austin Housing & Land Use Working Group — Research Hub
**Date:** June 2026
**Analysis vintage:** 2025 appraisal values · 2022–2024 fire incidents

---

## Summary

This report tests a single question three different ways: **does each area generate enough public revenue to pay for the infrastructure and services it consumes?** We measure it through (1) land value per acre, (2) road-infrastructure cost, and (3) fire-service cost — three independent datasets and methods.

**Bottom line.** All three converge on the same answer: **fiscal productivity is governed by *value per unit of infrastructure*, not by the "city vs. suburb" label.** Dense, high-value land — and a handful of wealthy low-density enclaves — generate far more revenue than the infrastructure they occupy costs to build and serve. Low-value, low-density development — the broad unincorporated fringe and road-heavy growth suburbs — does not: it underpays for the roads it requires and the fire coverage it needs, and it is cross-subsidized by the dense core.

Because three unrelated measurements (property value, road-miles, fire standby) point the same direction, the conclusion is robust to the weaknesses of any one method.

---

## 1. The question

The "value-per-acre" / Strong Towns framing holds that public infrastructure cost scales with **land area** (linear feet of road and pipe, geographic coverage), while public revenue scales with **property value**. Where value per acre is high, a parcel more than covers the infrastructure it occupies; where it is low, it does not, and the difference is made up by other parcels.

We apply this to the Austin metro (Travis + Williamson + Hays counties) and then drill into one concrete public service — the Austin Fire Department — to ask the same question with real consumption data.

---

## 2. Data sources

| Domain | Source | Records | Vintage |
|---|---|---|---|
| Parcels — Travis | TCAD public GIS geometry × **2025 Certified Appraisal Roll** (PACS `PROP.TXT`, joined by `PROP_ID`) | 373,471 | 2025 certified |
| Parcels — Williamson | WCAD ArcGIS FeatureServer | 265,506 | current cycle |
| Parcels — Hays | Hays CAD ArcGIS FeatureServer | 85,662 | current cycle |
| Fire incidents | Austin Fire Department (enriched: type, response area, parcel, tract) | 20,920 | 2022–2024 |
| Fire stations | City of Austin `LOCATION_fire_stations` (apparatus in `RESOURCES`) | 64 AFD | current |
| Roads | US Census TIGER/Line 2023 (local roads; interstates excluded) | 14,234 local miles | 2023 |
| City boundaries | US Census cartographic places (TX) | — | 2023 |

**Provenance note.** Travis per-property values are withheld from the statewide StratMap dataset and gated behind the appraisal-district web portal, but the **full certified roll is published free** as a fixed-width PACS export; we parse it directly (`12_parse_tcad_roll.py`). The roll re-certifies every mid-July (Tex. Property Tax Code §26.01), so the pipeline refreshes to a newer year by re-running one parser on the new `PROP.TXT`. All three counties sit at ~2025 vintage, so cross-county comparison is consistent.

---

## 3. Methodology

### 3.1 Value per acre

For every parcel: `value_per_acre = market_value / land_acres`. Acreage is taken from the CAD attribute where present and from the **parcel's geometry footprint** (EPSG:2277) where the CAD leaves it null — which recovers ~60% of suburban platted lots that the CAD acreage field omits. Values are winsorized at the 99th percentile for display, and parcels under 0.01 acre (data-artifact slivers) are dropped. Cross-county comparability uses each district's sales-ratio (Travis 1.00 / Williamson 0.96 / Hays 0.97).

### 3.2 Fiscal break-even — two cost models

Revenue per area = property value × a blended ~2.1% effective tax rate. We then compare it to **cost-to-serve** under two models, each calibrated so the metro breaks even in aggregate (so the result is *who is above/below average*, independent of the exact budget):

- **Model A — cost ∝ land area.** Break-even = total levy ÷ total acres. `net/acre = tax/acre − break-even`.
- **Model B — cost ∝ local road-miles.** The Strong Towns "value per road-mile." Cost is allocated by the local road network each area carries (TIGER roads, excluding state-maintained interstates). This is the more defensible model because public infrastructure cost tracks *linear feet of road and pipe*, not raw acreage.

A uniform tax rate cancels in the relative comparison, so the *pattern* is robust even though the absolute dollars are first-order.

### 3.3 Fire service — use vs. pays-in

AFD is funded city-wide from one pot, so every area's property tax helps fund all fire service. Per AFD **response area** (the operational first-due unit): **pays-in** = its share of citywide property value × AFD's ~$264M budget; **use** is measured three ways:

- **Demand** — cost-weighted calls (structure fire ×10, confined structure ×5, vehicle/outdoor ×2, trash ×1 — reflecting apparatus and crew committed).
- **Coverage (flat)** — every zone needs a staffed first-due company within response-time reach, regardless of call volume. ~90% of a fire budget is this fixed 24/7 standby, so coverage is the realistic cost driver.
- **Coverage (apparatus-weighted)** — each zone's standby cost scaled by its first-due station's actual apparatus (a ladder/quint company costs more than a single engine).

We also compute each zone's **distance to the nearest AFD station** as a direct measure of coverage quality (response time) and stretch.

---

## 4. Results

### 4.1 Value per acre — the Urban3 pattern holds

Across 724,639 metro parcels, value per acre spans four orders of magnitude. Downtown Austin H3 hexes top the metro at **$17–43 million per acre**; suburban old-town cores (Georgetown Square, Round Rock, San Marcos) register as local peaks well above their surroundings; the rural fringe and big-lot tracts bottom the distribution. Top parcels by value/acre are downtown high-rise office, condo, and hotel; the bottom are large low-value and undeveloped tracts — exactly the textbook result.

### 4.2 Fiscal productivity — the cost model changes the verdict

Under **Model A** (cost ∝ acres), the deciding variable is land value: Austin and the wealthy enclaves clear break-even; the largest deficit is rural/unincorporated land.

Under **Model B** (cost ∝ road-miles — the defensible model), the picture **sharpens and 11 cities change verdict**. The deciding variable becomes *value per road-mile*:

- **Road-heavy growth suburbs flip to net drains:** Kyle, Buda, Georgetown, and San Marcos all move below break-even — lots of pavement per dollar of value.
- **Big-lot, high-value enclaves strengthen:** West Lake Hills, Bee Cave, and Lakeway gain — few road-miles, high value.
- **The unincorporated-county deficit (~−$2 billion/yr) persists under both models** — confirming it is genuinely road-heavy, lower-value subdivision, not an artifact of assuming uniform per-acre cost.

![Fiscal productivity by city — land-cost vs road-cost model](../outputs/fiscal_land_vs_road.png)

### 4.3 Fire service — the same shape, with consumption data

Across 285 served AFD response areas ($263B property value, 20,920 fire calls), the two cost lenses tell opposite stories — and that contrast *is* the finding:

| Area type | Demand (cost ∝ calls) | Coverage flat | Coverage apparatus-wtd |
|---|---|---|---|
| Inner suburban | −$22M (subsidized) | +$45M | **+$32M** |
| Outer suburban | +$21M (contributes) | −$51M | **−$33M** |
| Urban core | +$2M | +$8M | +$4M |

- **Demand lens:** busy older inner areas generate the most calls, so they appear to "use" the most.
- **Coverage lens** (the realistic one): it **flips** — every spread-out outer-suburban zone still needs a staffed station, but holds roughly half the taxable value per zone, so **low-density outer development is the net drain on fire coverage.**
- **Apparatus-weighting moderates but does not overturn it** — outer suburbs are mostly single-engine houses (cheaper than flat-per-zone assumed), inner areas carry the costly ladder/quint companies. Direction holds.
- **Distance confirms a double penalty:** outer-suburban zones sit a median **1.2 miles** from the nearest station vs. **0.8** inner (worst cases >5 miles) — costlier to cover *and* slower-served.

![Fire: three cost models and coverage stretch](../outputs/fire_apparatus_distance.png)

The equity overlay shows the demand-subsidized areas skew toward older housing and higher density (more calls); under the coverage lens it is **low value-per-zone** that drives the deficit, with high-value commercial/downtown zones the biggest subsidizers.

![Fire net balance vs area characteristics](../outputs/fire_equity_scatter.png)

---

## 5. Why the data support the conclusion

The strength of the finding is **convergence across three independent measurements**:

1. **Property value per acre** — derived from appraisal rolls — shows low-density land underproduces value (hence tax).
2. **Road-miles** — derived from the federal road network — shows low-density land requires more pavement per dollar of value.
3. **Fire incidents + station standby** — derived from operational dispatch and facility data — shows low-density land requires more fire coverage capacity (and is farther from it) per dollar of value.

These three use **different source agencies, different units, and different methods**, yet point the same direction. A bias in any one (e.g., the blended tax rate, the uniform-cost assumption) cannot explain agreement across all three. Two deliberate robustness checks reinforce this: the fiscal result survives swapping the cost basis from acres to road-miles, and the fire result survives swapping flat-per-zone standby for apparatus-weighted standby. In both cases the *magnitude* softens but the *direction* is unchanged.

The honest qualifier is the one the data *also* show: it is **not** "suburb vs. city." Wealthy low-density enclaves (West Lake Hills, Lakeway, Rollingwood) pay their way precisely because their land value is high enough to clear the infrastructure bar. The subsidized party is the broad band of **low-value, low-density development** — much of it newer growth suburbs and unincorporated subdivision.

---

## 6. Limitations

- **Calibration, not budgets.** Both fiscal cost models are calibrated to break even metro-wide, not to actual municipal expenditure; absolute dollars are first-order. The AFD budget figure scales the fire dollars only — it does not affect the relative pattern.
- **Tax rate.** A blended ~2.1% effective rate is used; real per-jurisdiction rates vary, but a uniform rate cancels in the relative comparison.
- **Fire scope.** AFD / City of Austin only (suburban ESDs run separate departments with no comparable open incident data); **fire calls only — EMS/medical excluded**; three years (2022–2024).
- **Infrastructure proxy.** Road-miles omit water/sewer line-miles and service frequency; apparatus weighting omits crew-shift detail. Coverage cost allocated per first-due zone.
- **Vintage mix.** Travis values are 2025 certified; Williamson/Hays are their current published cycle. All ~2025; not identically dated.

These are accuracy-of-magnitude caveats, not direction-of-finding caveats — which is why the convergence argument carries the conclusion.

---

## 7. Reproducibility

Every figure and number regenerates from committed code over public data:

- `12_parse_tcad_roll.py` → parse a certified TCAD roll (`PROP.TXT`) to per-parcel values.
- `13_build_metro_parcels.py` → join Travis geometry + roll values + Williamson/Hays → metro parcel set.
- `notebooks/value_per_acre_metro.ipynb` → value-per-acre maps.
- `notebooks/fiscal_productivity.ipynb` → fiscal break-even, both cost models, per-city.
- `notebooks/fire_use_vs_pays.ipynb` → fire use-vs-pays-in, all lenses, apparatus + distance.

To refresh to a newer year, download the new certified roll and re-run the parser; the pipeline updates end-to-end.
