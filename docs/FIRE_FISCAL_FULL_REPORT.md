# Who Pays for Growth? — The Fire-Fiscal Master Report

### Value, infrastructure, and fire service across the Austin metro

**Prepared by:** Austin Housing & Land Use Working Group — Research Hub
**Date:** June 2026 · **Analysis vintage:** 2025 appraisal values · 2022–2024 fire incidents
**Companion artifacts:** `outputs/fire_fiscal_interactive_map.html` (interactive 3D map) · `outputs/validation_report.csv` (data validation gate)

---

> **How to read this.** It's long, so it's built to be read at whatever depth you have time for:
>
> | Time | Read |
> |---|---|
> | **2 minutes** | §1 |
> | **15 minutes** | §1, §2, §6 |
> | **the whole thing (~45 min)** | everything, including the calculations (§5) and appendices (§10–13) |
>
> The charts use two color keys — one for *value per acre*, one for *fire net balance*. You don't need to memorize them; the key is laid out in [§10](#the-color-key).
>
> The headline figures are machine-reconciled against the source data — §11 is the reconciliation table, and it is explicit about which rows are recomputed and which are sourced constants — and each figure footnotes the exact line of code that produces it.

[TOC]

---

## 1 · Executive summary

The question is simple: **can each part of the metro pay its own way?** Does it bring in enough public revenue to cover the infrastructure and services it uses? We test that three ways — land value per acre, road cost, and fire-service cost — each from a separate dataset.

The three lenses agree. What decides whether an area pays its way is its **value per unit of infrastructure** — not whether you call it a city or a suburb. Dense, high-value land, plus a few wealthy low-density enclaves, brings in far more than it costs to serve. Low-value, low-density development — the unincorporated fringe and the road-heavy growth suburbs — does not, and the dense core covers the gap.

Three unrelated measurements (property value, road-miles, fire standby) point the same way, so the finding doesn't rest on any one method.[^converge]

It is not simply suburb-versus-city. West Lake Hills, Lakeway, and Rollingwood pay their way because their land is valuable enough to clear the bar, even at low density. The areas that fall short are the broad band of **low-value, low-density development** — much of it newer growth suburbs and unincorporated subdivision.

[^converge]: The convergence argument is developed in full in [§8](#8--why-the-data-support-the-conclusion). A bias in any single method (e.g. the blended tax rate, the uniform-cost assumption) cannot explain agreement across three different agencies, units, and methods.

---

## 2 · Key concepts

A short definition of each idea the report uses, with a picture. The full [glossary](#12--glossary) at the end covers every term.

### 2.1 Land value, and market vs. assessed/appraised value

- **Market value** — what an appraisal district estimates a property would sell for. This is the figure we use for revenue, because property tax is levied against value.
- **Appraised / assessed value** — market value after caps and exemptions (e.g. the 10% homestead cap). Taxes are actually levied on this; we use it for the tax-per-acre lens and market value for the value lens.

So "value" throughout is the appraisal district's estimate of what the land and buildings are worth — the number the tax rate gets multiplied against.

### 2.2 Value per acre

The central idea, borrowed from the Strong Towns / Urban3 framing: **public infrastructure cost scales with land *area*** (linear feet of road and pipe, geographic coverage to patrol and serve), while **public revenue scales with property *value***. So the meaningful productivity ratio is value **per acre**.

![Two parcels of identical size produce vastly different revenue per acre](../outputs/fig_concept_value_per_acre.png)

Two parcels can sit on the same acre — same road, same pipe, same area to cover — yet one brings in 80× the tax. Value per acre is what makes that visible.

### 2.3 Effective tax rate

Revenue is `value × an effective tax rate`. The **effective** rate blends every overlapping jurisdiction — City of Austin, the county, the school district (AISD), the community college (ACC), and special districts — into one number applied to market value. We use a blended **~2.1%**.[^rate] A uniform rate **cancels** in any relative (above/below average) comparison, so the *pattern* does not depend on getting the rate exactly right — only the absolute dollars do.

[^rate]: `EFFECTIVE_TAX_RATE = 0.021` is defined once at `13_build_metro_parcels.py:22` and reused everywhere. Validated against published City/county/AISD/ACC rates — see [§11](#11--validation-appendix).

### 2.4 Fiscal productivity & break-even

An area **breaks even** when its revenue equals its cost-to-serve. Above the line it is a **net contributor**; below it, it is **cross-subsidized** by other areas.

![Revenue rises with value; cost-to-serve is roughly flat per acre — they cross at the break-even value per acre](../outputs/fig_concept_breakeven.png)

Plot what an area pays in against what it costs to serve. Where the two lines cross is break-even. The whole report is really about who sits above that line and who sits below.

### 2.5 Fire coverage vs. fire demand

A fire department's cost is mostly **standby**, not response. Roughly **90%** of a fire budget pays to keep a staffed company ready 24/7 within response-time reach of every zone — whether or not that zone calls often.[^standby] So there are two very different ways to measure "use":

- **Demand** — how many (cost-weighted) calls a zone generates.
- **Coverage** — the fixed cost of keeping a first-due company able to reach that zone in time.

[^standby]: The ~90% is the fixed-readiness share of a fire budget — overwhelmingly the personnel cost of keeping companies staffed around the clock regardless of call volume. "As public safety is a labor-intensive service model, typically more than 90% of the budget is accounted for by personnel costs" — Steven Knight, PhD (Fitch & Associates), [FireRescue1](https://www.firerescue1.com/fire-chief/articles/doing-more-with-less-fire-department-budgets-fiscal-responsibility-GTj33j3axJ2tfshe/); for a worked line-item example (>90% non-discretionary once payroll, stations and apparatus are counted) see this [budget breakdown](https://www.firerescue1.com/fire-products/administration-billing/articles/budget-breakdown-the-real-cost-of-operating-a-fire-department-uB62rUFtPgUf8ZpZ/).

![Call volume falls with density, but staffed standby stays roughly fixed per zone](../outputs/fig_concept_coverage_demand.png)

A quiet outer zone still needs a station that can reach it in time. Most of the cost is being ready, not running calls — so which area "uses the most" depends entirely on which lens you pick.

### 2.6 Apparatus weighting

Not every call or company costs the same. A full first-alarm structure fire commits far more crew and equipment than a trash fire, and a ladder/quint company costs more to staff than a single engine. We weight incidents by type[^weights] and stations by their actual apparatus[^appw] so the cost lens reflects real resource intensity.

[^weights]: `WEIGHTS = {structure fire 10, confined 5, vehicle/outdoor 2, trash 1}` — `notebooks/fire_use_vs_pays.ipynb` cell 2. Applied at cell 4. Validated: 20,920 incidents → 65,166 weighted ([§11](#11--validation-appendix)).
[^appw]: `APP_W = {ENG 1.0, LAD 1.0, QNT 1.2, RES 0.8}`, battalion units 0.5 — `notebooks/fire_use_vs_pays.ipynb` cell 10.

---

## 3 · The data inputs

The analysis draws on three groups of sources, feeding three models, producing three findings. The grouping is by **function**: what each source measures.

![Data inputs grouped by function, flowing into the three models and three findings](../outputs/fig_data_inputs_flow.png)

- **Group A · Property & Value** — the appraisal rolls and parcel geometry that tell us what land is worth and how big it is. Feeds the value-per-acre and fiscal models.
- **Group B · Fire Operations** — AFD's incidents, stations, and response areas: the real consumption data for the fire model.
- **Group C · Geography & Infrastructure** — the federal road network, city boundaries, and Census demographics that supply the cost basis (road-miles) and the equity overlay.

---

## 4 · The data sources, in detail

For each source: what the agency is, what the dataset is, its vintage, why it's the authoritative source, and what we use it for.

### 4.1 Property & value (Group A)

**What we use it for:** every dollar figure in the report — the value-per-acre map, the fiscal break-even (both cost models), and each area's fire pays-in. Without it there is no revenue side to the ledger.

| Source | Agency | What it is | Records | Vintage | Why authoritative |
|---|---|---|---|---|---|
| **Travis parcels** | **TCAD** (Travis Central Appraisal District) | Public parcel GIS geometry joined to the **2025 Certified Appraisal Roll** (PACS `PROP.TXT` fixed-width export), by `PROP_ID` | 373,471 | 2025 certified | TCAD is the *statutory* appraiser for Travis County (Tex. Property Tax Code). The certified roll is the legal basis for every tax bill in the county.[^tcad] |
| **Williamson parcels** | **WCAD** via Williamson County GIS ArcGIS FeatureServer | Parcels bundling `TotalPropMktValue` + geometry + `AssessedAc` + use | 265,506 | current cycle | WCAD is the statutory appraiser for Williamson County; the county GIS republishes its certified values. |
| **Hays parcels** | **Hays CAD** ArcGIS FeatureServer (`countygis.DBO.Parcels`) | Parcels with `market`, `land_val`, `imprv_val`, `legal_acreage` | 85,662 | current cycle | Hays CAD is the statutory appraiser for Hays County. |
| **Cross-county comparability** | **Texas Comptroller** Property Value Study / Appraisal District Ratio Study | Median appraisal-to-sale ratio, Category A | — | 2022–2024 ADRS | The Comptroller independently audits each district's level of appraisal; we divide by these ratios so a dollar of "market value" means the same across counties.[^pvs] |

[^tcad]: **Provenance note.** Travis per-property values are withheld from the statewide StratMap dataset and gated behind the appraisal-district web portal, but the **full certified roll is published free** as a fixed-width PACS export; we parse it directly with `12_parse_tcad_roll.py`. The roll re-certifies every mid-July (Tex. Property Tax Code §26.01), so the pipeline refreshes to a newer year by re-running one parser on the new `PROP.TXT`.
[^pvs]: `PVS_RATIOS = {travis 1.00, williamson 0.96, hays 0.97}` with the per-county ADRS citations in `v2_county_sources.py`. Applied as `value_per_acre_adj = (market_value / pvs_ratio) / land_acres` at `13_build_metro_parcels.py`.

### 4.2 Fire operations (Group B)

**What we use it for:** the fire model — which areas generate calls (demand), where the stations actually are (coverage and distance), and the response-area zones we balance "use" against "pays-in."

| Source | Agency | What it is | Records | Vintage | Why authoritative |
|---|---|---|---|---|---|
| **Fire incidents** | **Austin Fire Department**, via the [Austin Open Data Portal](https://data.austintexas.gov/Public-Safety/AFD-Fire-Incidents-2022-2024/v5hh-nyr8) | Per-incident type, response area, location — enriched here with parcel + tract | 20,920 | 2022–2024 | AFD is the dispatching authority; this is its own operational record of every fire call. |
| **Fire stations** | City of Austin `LOCATION_fire_stations` ArcGIS FeatureServer | Station points with apparatus in `RESOURCES` | 64 AFD | current | The City's authoritative facilities layer (apparatus assignments included). |
| **Response areas** | City of Austin `BOUNDARIES_afd_response_areas` ArcGIS FeatureServer | First-due operational zones | 765 (285 served) | current | The operational unit AFD itself uses to assign first-due companies. |

### 4.3 Geography & infrastructure (Group C)

**What we use it for:** the road-cost model (Model B) needs the road network; the city boundaries put each parcel in the right jurisdiction; the Census demographics supply the density and housing-age context.

| Source | Agency | What it is | Vintage | Why authoritative |
|---|---|---|---|---|
| **Roads** | **US Census Bureau** TIGER/Line | Local road network (interstates excluded) | 2023 | The federal standard geographic road network; consistent nationwide. |
| **City boundaries** | US Census Bureau cartographic "places" | Incorporated-place polygons (TX) | 2023 | Authoritative municipal boundaries. |
| **Demographics** | US Census Bureau **ACS 5-year** (B01003 population, B25024 units, B25034 year-built) | Tract-level housing & population | 2022 5-yr | The standard small-area demographic estimates, area-weighted to response areas. |

---

## 5 · Calculations and methodology

Every formula is written out, with a worked example and a footnote pointing to the exact code that runs it.

### 5.1 Value per acre

```
value_per_acre = market_value / land_acres
```

Acreage comes from the CAD attribute where present and from the **parcel geometry footprint** (projected to EPSG:2277, Texas Central State Plane) where the CAD leaves it null — which fills in the **13.8%** of Travis parcels (about 18% of platted-lot-size parcels) whose CAD acreage field is empty.[^acres] Values are winsorized at the 99th percentile for display, and parcels under 0.01 acre (data-artifact slivers) are dropped.

> **Worked example.** A downtown parcel worth $40,000,000 on 1.0 acre → **$40,000,000/acre**. A suburban house worth $500,000 on 1.0 acre → **$500,000/acre**. Same footprint; 80× the productivity.

[^acres]: Acreage fallback (CAD acres where positive, else parcel-geometry area in EPSG:2277) is implemented in `build_travis()`, `13_build_metro_parcels.py`. The roll's `legal_acreage` field sits between the two in the code but in practice fills none of the missing rows — the geometry footprint covers all 51,545 of them.

### 5.2 Revenue

```
revenue = market_value × EFFECTIVE_TAX_RATE        (EFFECTIVE_TAX_RATE = 0.021)
```

Summed across all 724,639 metro parcels this yields **≈ $12.56 billion/yr** in modeled property-tax revenue on **≈ $597.9 billion** of market value.[^rev]

[^rev]: `tax_per_acre = taxable_value × EFFECTIVE_TAX_RATE / land_acres` — `13_build_metro_parcels.py`. The $597.9B / $12.56B totals are reconciled in [§11](#11--validation-appendix). Note the revenue model applies the rate to **market** value; actual bills are levied on taxable value after caps and exemptions, so $12.56B is the model's calibration total, not a collections forecast — the relative pattern is what carries.

### 5.3 Fiscal break-even — two cost models

Each model is **calibrated so the metro breaks even in aggregate**, so the output is *who is above/below average*, independent of the exact budget.

- **Model A — cost ∝ land area.** `break_even_per_acre = total_levy / total_acres`; `net_per_acre = tax_per_acre − break_even_per_acre`. The metro-wide break-even is **$8,421/acre**.[^modelA]
- **Model B — cost ∝ local road-miles** (the Strong Towns "value per road-mile"). Cost is allocated by the local road network each area carries (TIGER roads, excluding state-maintained interstates). This is the better proxy, since public infrastructure cost follows linear feet of road and pipe more closely than raw acreage.

> **Worked example (Model A).** A parcel paying $12,000/acre in tax sits **+$3,579/acre above** the $8,421 break-even — a net contributor. One paying $4,000/acre sits **−$4,421/acre below** — cross-subsidized.

[^modelA]: Break-even computed in `notebooks/fiscal_productivity.ipynb`; the all-land figure ($8,421/acre) is a validation check in [§11](#11--validation-appendix).

### 5.4 Fire service — use vs. pays-in

AFD is funded city-wide from one pot, so every area's property tax helps fund all fire service. Per AFD **response area**:

```
pays_in   = (area_property_value / total_city_value) × AFD_BUDGET
```

with `AFD_BUDGET ≈ $264M`.[^budget] **Use** is measured three ways:

```
value_share     = prop_value / Σ prop_value
callcost_share  = weighted_calls / Σ weighted_calls          # demand lens
coverage_share  = 1 / N_served_areas                          # flat coverage lens
net_demand    = (value_share − callcost_share)  × AFD_BUDGET
net_coverage  = (value_share − coverage_share)  × AFD_BUDGET
```

The **apparatus-weighted** coverage lens scales each zone's `coverage_share` by its first-due station's apparatus weight. We also compute each zone's **distance to the nearest AFD station** (a `sjoin_nearest` in EPSG:2277) as a direct measure of coverage stretch.[^net]

> **Worked example.** A downtown zone holding 3% of citywide value but generating 1% of weighted calls has `net_demand = (0.03 − 0.01) × $264M = +$5.3M` — it pays in far more than its call volume "uses." Under the **coverage** lens, a spread-out outer zone holding 0.2% of value but consuming `1/285 = 0.35%` of standby has `net_coverage = (0.002 − 0.0035) × $264M = −$0.4M` — a net drain on coverage.

[^budget]: `AFD_BUDGET = 264_000_000` — `notebooks/fire_use_vs_pays.ipynb` cell 2. Validated against the FY2024-25 City of Austin adopted budget in [§11](#11--validation-appendix). It scales the fire dollars only; the relative pattern is budget-invariant.
[^net]: Net-balance assembly: `notebooks/fire_use_vs_pays.ipynb` cells 6–10. **Conservation** (`Σ value_share = 1`, each cost share sums to 1, net columns sum ≈ 0) is asserted as a validation check.

---

## 6 · Results

### 6.1 Value per acre — the Urban3 pattern holds

Across **724,639 metro parcels**, value per acre spans four orders of magnitude. Downtown Austin H3 hexes top the metro at **$17–43 million per acre**; the old-town cores of the suburbs (Georgetown Square, Round Rock, San Marcos) stand out as local peaks above their surroundings; the rural fringe and big-lot tracts sit at the bottom. The highest value-per-acre parcels are downtown high-rise office, condos, and hotels; the lowest are large, low-value or undeveloped tracts.

*The value-per-acre surface is best read interactively: it is the extruded "Value per acre (3D)" layer in the companion `outputs/fire_fiscal_interactive_map.html` (and visible in the [§7 map preview](#7--places-you-know)). It regenerates from `parcels_value_per_acre_metro.parquet` via `notebooks/value_per_acre_metro.ipynb`.*

### 6.2 Fiscal productivity — the cost model changes the verdict

Model A charges every area by its land area; Model B charges by the local road-miles it actually carries. Model B is the better proxy, because public infrastructure cost follows linear feet of road and pipe more closely than raw acreage. Switching from A to B sharpens the picture and **flips the verdict for 11 cities** — the deciding variable becomes value per road-mile.

What decides a flip is value **per road-mile**, not home value alone. Four road-heavy growth suburbs flip to net drains (Buda, Georgetown, Kyle, Wells Branch); seven flip the other way, to contributor — most of them high-value (Bee Cave, Point Venture, Shady Hollow), but also modest Elgin, which clears the bar because it carries barely five road-miles. The familiar names:[^verdicts]

| City | Median home value | Land-cost model (A) → road-cost model (B) |
|---|---|---|
| West Lake Hills | ~$1.74M | contributor under both — strengthens (high value, few road-miles) |
| Bee Cave | ~$835k | **flips to contributor** |
| Lakeway | ~$740k | contributor under both — strengthens |
| *Austin (reference)* | ~$495k | contributor under both |
| Buda | ~$404k | **flips to net drain** |
| Georgetown | ~$375k | **flips to net drain** |
| San Marcos | ~$327k | net drain under **both** models |
| Kyle | ~$315k | **flips to net drain** |

The unincorporated county runs a deficit of about **−$2 billion/yr under both models**, so that gap is genuinely road-heavy, lower-value subdivision — not an artifact of how Model A assumes cost.

[^verdicts]: The full 46-city ledger — revenue, acres, road-miles, both nets, median home value, and verdict — is exported by `notebooks/fiscal_productivity.ipynb` to `outputs/city_fiscal_verdicts.csv`. The 11 verdict-changers: Bee Cave, Elgin, Liberty Hill, Manor, Point Venture, Shady Hollow, Woodcreek (→ contributor); Buda, Georgetown, Kyle, Wells Branch (→ net drain).

![Fiscal productivity by city — land-cost (Model A) vs road-cost (Model B); 11 cities change verdict](../outputs/fiscal_land_vs_road.png)

*Median home value = the median market value of residential-sized parcels (0.05–1.5 acres) in each city, computed from the parcel roll and exported with the verdicts to `outputs/city_fiscal_verdicts.csv`.*

### 6.3 Fire service — the same shape, with consumption data

This breaks the 285 served AFD response areas ($263B property value; 20,136 of the 20,920 citywide fire calls) into three area types by density:

- **Urban core** — the dense central-city zones (downtown and the older grid).
- **Inner suburban** — the established neighborhoods ringing the core: moderate density, mostly older housing.
- **Outer suburban** — the spread-out, newer edge: large lots, long roads, low density.

Depending on which cost lens you use, two of those three switch sign — and that switch is the whole point:

| Area type | Demand (cost ∝ calls) | Coverage flat | Coverage apparatus-wtd |
|---|---|---|---|
| Inner suburban | −$22M (subsidized) | +$45M | **+$32M** |
| Outer suburban | +$21M (contributes) | −$51M | **−$33M** |
| Urban core | +$2M | +$8M | +$4M |

*Two zones with no ACS density classification are omitted from the table (−$0.2M demand, −$1.6M coverage); including them, each column sums to ≈0 — the conservation check in [§11](#11--validation-appendix).*

- **Demand lens:** busy older inner areas generate the most calls, so they look like they "use" the most.
- **Coverage lens:** this is the lens that matches how a fire budget actually works — about 90% of it is the fixed cost of keeping a staffed company ready, not running calls. On that basis the result **flips**: every spread-out outer-suburban zone still needs its own staffed station but holds only about half the taxable value per zone, so **low-density outer development is the net drain on fire coverage**.
- **Apparatus-weighting** softens the gap but doesn't close it — outer suburbs are mostly single-engine houses, while inner areas carry the costly ladder/quint companies. The direction holds.
- **Distance** adds a second penalty: outer-suburban zones sit a median **1.2 miles** from the nearest station versus **0.8** for inner ones (worst cases over 5 miles) — costlier to cover *and* slower to reach.

You can see this zone by zone on the map in [§7](#7--places-you-know), and interactively in the companion `fire_fiscal_interactive_map.html`.

![Fire: three cost models (demand, coverage, apparatus-weighted) and coverage stretch (distance to nearest station)](../outputs/fire_apparatus_distance.png)

![Fire net balance vs. area characteristics — value, density, and housing age](../outputs/fire_equity_scatter.png)

### 6.4 AFD in the context of the full City budget

To read the fire dollars correctly, it helps to see AFD inside the whole City of Austin budget. In **FY2024-25** the City adopted a **$5.9 billion** all-funds budget, of which the tax-supported **General Fund is $1.4 billion**. The four public-safety departments (Police, Fire, EMS, Forensics) together are **64.8%** of the General Fund. AFD's **≈$264M** is roughly **19% of the General Fund** — the second-largest department after police.[^budgetfig]

![Austin Fire Department in the context of the City of Austin FY2024-25 budget](../outputs/fig_afd_vs_city_budget.png)

[^budgetfig]: Figures confirmed via the FY2024-25 City of Austin adopted budget (City Council adoption, Aug 2024). See [§11](#11--validation-appendix) for sources. Built in `15_build_report_figures.py` (`fig_afd_vs_city_budget`).

---

## 7 · Places you know

The numbers are easier to trust against places you can actually picture. The companion **[interactive 3D map](../outputs/fire_fiscal_interactive_map.html)** lets you toggle four layers — value-per-acre (extruded), fire net balance, fire stations, and these landmark pins — and click any zone for its value, pays-in, and net.

![Static preview of the interactive 3D map — response-area choropleth with colloquial landmark pins (bluebonnet = high value / contributor, burnt-orange = net drain); pins are shown for landmarks inside AFD's service extent — the outer-metro cities in the table below sit beyond the map edge](../outputs/fig_interactive_map_preview.png)

| Landmark | Colloquial read | Productivity signal |
|---|---|---|
| **Downtown Austin** | high-rise office, condo, hotel core | metro **peak** value/acre ($17–43M/acre); biggest fire subsidizer |
| **The Domain** | dense north mixed-use "second downtown" | very high value/acre; net contributor |
| **Mueller** | redeveloped airport, dense urbanism | high value/acre; net contributor |
| **West Lake Hills** | wealthy low-density enclave | pays its way — high value clears the bar despite low density |
| **Lakeway / Bee Cave** | big-lot high-value Hill Country | strengthen under the road-cost model (few road-miles) |
| **Round Rock** | growth suburb; historic square | old-town square is a local value peak; surrounds are mixed |
| **Northland / north-central** | older north-central corridor | mixed — demand-heavy under the call lens |
| **Georgetown** | growth suburb, large footprint | **flips to net drain** under the road-cost model |
| **Kyle / Buda** | fast-growing outer suburbs | **net drains** — lots of pavement per dollar of value |
| **San Marcos** | outer-metro college town | net drain under **both** cost models; local square is a peak |

Below the named landmarks sits the **exact ranking** — the AFD response areas (by their operational zone code and urban class) that contribute and drain the most under the coverage lens, with each zone's measured value per acre. The pattern is strong though not airtight: the top four contributors are very high-value zones ($20–46M/acre), led by the downtown zone, while the fifth is a populous low-value outer zone — and every one of the biggest drains is a low-value outer/inner-suburban zone. The drains cluster near **−$0.93M** because that is the floor — a zone holding almost no taxable value still consumes one zone's share of standby (`1/285 × $264M`).

![Ranked inventory — AFD response areas by value-per-acre and fire net balance (coverage lens)](../outputs/fig_colloquial_inventory.png)

*Full 285-area ranking in `outputs/colloquial_inventory.csv`; regenerates from the parquet + `fire_net_balance.geojson` via `15_build_report_figures.py` (`fig_colloquial_inventory`).*

---

## 8 · Why the data support the conclusion

The finding holds because three independent measurements point the same way:

1. **Property value per acre** — from appraisal rolls — shows low-density land produces less value (and so less tax) per acre.
2. **Road-miles** — from the federal road network — shows low-density land needs more pavement per dollar of value.
3. **Fire incidents + station standby** — from dispatch and facility data — shows low-density land needs more fire coverage per dollar of value, and sits farther from it.

These come from **different agencies, in different units, by different methods**, yet they agree. A bias in any one — the blended tax rate, say, or the uniform-cost assumption — can't explain why all three line up. Two checks back this up: the fiscal result survives swapping the cost basis from acres to road-miles, and the fire result survives swapping flat-per-zone standby for apparatus-weighted standby. Each time the size of the gap changes; the direction doesn't.

---

## 9 · Limitations

- **Calibration, not budgets.** Both fiscal cost models are calibrated to break even metro-wide, not to actual municipal expenditure; absolute dollars are first-order. The AFD budget figure scales the fire dollars only — it does not affect the relative pattern.
- **Tax rate.** A blended ~2.1% effective rate is used; real per-jurisdiction rates vary, but a uniform rate cancels in the relative comparison.
- **Fire scope.** AFD / City of Austin only. Suburban **ESD** fire departments run separate departments with no comparable open incident data, so they are stated as out of scope rather than silently dropped; **fire calls only — EMS/medical excluded**; three years (2022–2024). Pays-in denominators count **Travis parcels only**, so the few served zones spilling into Williamson/Hays have their value — and hence pays-in — modestly understated.
- **Infrastructure proxy.** Road-miles omit water/sewer line-miles and service frequency; apparatus weighting omits crew-shift detail. Coverage cost allocated per first-due zone.
- **Vintage mix.** Travis values are 2025 certified; Williamson/Hays are their current published cycle. All ~2025; not identically dated.

Each of these affects how big the numbers are, not which way they point — which is why the three-way agreement still carries the conclusion.

---

## 10 · Master appendix — figures & tables

| Figure | File | Status |
|---|---|---|
| Data-inputs flow diagram | `outputs/fig_data_inputs_flow.png` | built |
| Concept: value per acre | `outputs/fig_concept_value_per_acre.png` | built |
| Concept: fiscal break-even | `outputs/fig_concept_breakeven.png` | built |
| Concept: coverage vs demand | `outputs/fig_concept_coverage_demand.png` | built |
| Palette swatch | `outputs/fig_palette_swatch.png` | built |
| AFD vs City budget | `outputs/fig_afd_vs_city_budget.png` | built |
| Interactive-map preview | `outputs/fig_interactive_map_preview.png` | built |
| Validation reconciliation | `outputs/validation_summary.png` | built |
| Fiscal: land vs road model | `outputs/fiscal_land_vs_road.png` | built (embedded §6.2) |
| Fire: 3 models + distance | `outputs/fire_apparatus_distance.png` | built (embedded §6.3) |
| Fire: net balance vs characteristics | `outputs/fire_equity_scatter.png` | built (embedded §6.3) |
| Ranked inventory by zone | `outputs/fig_colloquial_inventory.png` | built (embedded §7) |

![The Austin civic palette and how to read each scale](../outputs/fig_palette_swatch.png)

#### The color key

Two scales do all the work. The **sequential** one (`#1d3557 → #457b9d → #a8dadc → #e9c46a → #bc6c25`) means *value per acre, low → high*. The **diverging** one (burnt-orange `#9c4221` ↔ limestone `#efe9dd` ↔ bluebonnet `#2a6f97`) means *fire net balance*, centered on break-even. Both are defined once in `viz_palette.py` and reused by the explainer diagrams, the map preview, and the interactive map, so a color means the same thing wherever you see it. The three analytical charts in §6.2–6.3 come straight from the analysis notebooks and keep their own coloring, spelled out in each caption.

Color is a shortcut, not the only signal: the two ends of the diverging scale can be hard to tell apart in print or for colorblind readers, so every chart and table also carries the actual numbers. (A grayscale-legible version of the map is in the Kindle/e-ink build.)

---

## 11 · Validation appendix

The headline numbers pass a machine-generated reconciliation (`notebooks/validation.ipynb` → `outputs/validation_report.csv`). **All 24 checks are green.** The table has two kinds of row and is explicit about which is which: the **recomputed checks** re-derive their numbers from the source files on every run — incident and parcel counts, totals, the break-even, the fire net-balance (rebuilt from scratch rather than read from the analysis notebook), the §6.2 city verdicts, the §6.3 class table, and station distances, all against the full 724,639-parcel roll — while the five **citation-log rows** record the externally sourced constants (budget figures, tax rate) with their sources rather than measuring them. The net-balance conservation check holds to machine precision (`1.1e-16`), and the run also exports `processed_data/fire_net_balance.geojson` that feeds the interactive map's fire layer.

![Validation reconciliation table](../outputs/validation_summary.png)

**External-constant sources (independently confirmed via web, June 2026):**

- City of Austin FY2024-25 adopted budget **$5.9B all funds** ([KUT](https://www.kut.org/austin/2024-08-14/austin-texas-city-council-5-9-billion-budget-2024-2025-fiscal-year)), **General Fund $1.4B** ($1,404.5M base expenditures; [City of Austin Budget Office](https://www.austintexas.gov/budget-excellence/city-budget)). Public-safety departments (Police + Fire + EMS + Forensics) ≈ **mid-60s % of the General Fund** (the report uses 64.8%).
- AFD budget **≈$263–264M** for FY2024-25 ([ATXtoday budget breakdown](https://atxtoday.6amcity.com/city/austins-2024-2025-budget)) — the second-largest General Fund department, ≈19% of the GF.
- Blended effective property-tax rate **≈2.1%** — City of Austin + Travis/Williamson/Hays counties + AISD + ACC + special districts, combined effective rate. Used uniformly, so it cancels in every relative comparison.

---

## 12 · Glossary

Extends the 21-term glossary in `docs/RESEARCH_CONTEXT.md` with the financial concepts this report adds.

| Term | Definition |
|---|---|
| **Value per acre** | Market value ÷ land acres — productivity of land normalized to the unit infrastructure scales with. |
| **Market value** | Appraisal district's estimate of sale price; the base for property-tax revenue here. |
| **Appraised / assessed value** | Market value after caps/exemptions; the legal tax base (used for the tax-per-acre lens). |
| **Effective tax rate** | Blended rate across all overlapping jurisdictions applied to market value (~2.1% here). |
| **Fiscal productivity / break-even** | Whether an area's revenue covers its cost-to-serve; above = net contributor, below = subsidized. |
| **Cost-to-serve** | Modeled public cost of an area, allocated either by land area (Model A) or local road-miles (Model B). |
| **Value per road-mile** | Strong Towns metric: property value divided by the local road network an area carries. |
| **Pays-in (fire)** | An area's share of citywide property value × the AFD budget — what its taxes contribute to fire. |
| **Demand lens** | Fire "use" measured as cost-weighted call volume. |
| **Coverage lens** | Fire "use" measured as the fixed standby cost of keeping a first-due company per zone — the cost that dominates a fire budget. |
| **Apparatus weighting** | Scaling cost by the actual equipment/crew committed (ladder/quint > engine; structure fire > trash). |
| **Net balance** | pays-in − use, in $/yr; positive = net contributor, negative = net drain. |
| **PVS / sales ratio** | Comptroller's median appraisal-to-sale ratio, used to make values comparable across counties. |
| **Winsorize** | Cap a distribution at a percentile (99th here) so extreme outliers don't distort display scales. |
| **H3 hexagon** | Uber's hexagonal spatial index; parcels are aggregated to H3 res-8 cells for the metro value map. |
| **Response area** | AFD's first-due operational zone (765 total, 285 served by ≥1 call + value). |
| **EPSG:2277** | Texas Central State Plane (feet) — the projected CRS used for areas and distances. |

*(See `docs/RESEARCH_CONTEXT.md` for AFD, ETJ, ACS, NFIRS, urban-core/inner/outer thresholds, single-stair, HOME, WUI, zoning codes, and more.)*

---

## 13 · Code & pseudo-code appendix

### Pseudo-code — the three models

```
MODEL 1 — value per acre
  for each parcel:
      acres = CAD_acres or legal_acreage or geometry_area(EPSG:2277)
      value_per_acre = market_value / acres
  winsorize at p99 for display; drop acres < 0.01
  value_per_acre_adj = (market_value / pvs_ratio[county]) / acres

MODEL 2 — fiscal break-even
  revenue        = Σ market_value × 0.021
  # Model A: cost ∝ area
  break_even/ac  = revenue / Σ acres
  net/ac         = value × 0.021 / acres − break_even/ac
  # Model B: cost ∝ local road-miles (TIGER, no interstates)
  cost_share     = area_road_miles / Σ road_miles
  net            = value_share − cost_share

MODEL 3 — fire use vs pays-in
  weighted_calls = Σ incident × WEIGHTS[type]
  value_share    = area_value / Σ value
  pays_in        = value_share × AFD_BUDGET
  net_demand     = (value_share − weighted_calls/Σ) × AFD_BUDGET
  net_coverage   = (value_share − 1/N_served) × AFD_BUDGET
  net_coverage_apparatus = scale coverage_share by nearest-station apparatus weight
  dist_mi        = distance(area_centroid, nearest_station)   # EPSG:2277
```

### Real code excerpts

**Revenue & cross-county adjustment** — `13_build_metro_parcels.py`:

```python
g["value_per_acre"] = g["market_value"] / g["land_acres"]
g["pvs_ratio"] = g["county"].map(PVS)                      # 1.00 / 0.96 / 0.97
g["value_per_acre_adj"] = g["value_per_acre"] / g["pvs_ratio"]
g["tax_per_acre"] = g["taxable_value"] * EFFECTIVE_TAX_RATE / g["land_acres"]
```

**Fire net balance** — `notebooks/fire_use_vs_pays.ipynb` cell 8:

```python
t['value_share']    = t['prop_value'] / t['prop_value'].sum()
t['callcost_share'] = t['wcalls']     / t['wcalls'].sum()
t['coverage_share'] = 1.0 / len(t)     # each zone = one staffed company
t['net_demand_M']   = (t['value_share'] - t['callcost_share']) * AFD_BUDGET / 1e6
t['net_coverage_M'] = (t['value_share'] - t['coverage_share']) * AFD_BUDGET / 1e6
```

### Reproducibility runbook

Every figure and number regenerates from committed code over public data:

1. `12_parse_tcad_roll.py` → parse a certified TCAD roll (`PROP.TXT`) to per-parcel values.
2. `13_build_metro_parcels.py` → Travis geometry + roll values + Williamson/Hays → metro parcel set.
3. `notebooks/value_per_acre_metro.ipynb` · `fiscal_productivity.ipynb` · `fire_use_vs_pays.ipynb` → the three models.
4. `notebooks/validation.ipynb` → the validation gate (`outputs/validation_report.csv`).
5. `15_build_report_figures.py` → the explainer/diagram figures (+ data-charts when the parquet is present).
6. `notebooks/interactive_map.ipynb` → `outputs/fire_fiscal_interactive_map.html`.
7. `14_build_report_pdf.py` → this document as a styled PDF.

**On a fresh clone**, the large data files (`parcels_value_per_acre_metro.parquet`, `fire_stations.geojson`, `metro_highways.geojson`) aren't tracked in git. Rebuild the parcels first (`12_parse_tcad_roll.py` → `13_build_metro_parcels.py`), then run the steps above in order. Each notebook and script checks whether its data is present and simply skips the parts it can't run yet, so nothing errors — the missing figures and map layers fill in once the data is there.

---

## 14 · References & cross-links

For policy context (single-stair building code, HOME initiative, WUI, NFPA 1710, zoning codes) and the operational glossary (AFD, ETJ, ACS, NFIRS, urban-core/inner/outer density thresholds), see **`docs/RESEARCH_CONTEXT.md`**. For the per-field data dictionary, see **`docs/DATA_DICTIONARY.md`**.

---

*Generated by the Austin Housing & Land Use Working Group — Research Hub. Charts and the interactive map share a single color module (`viz_palette.py`); every headline number is reconciled in `outputs/validation_report.csv`.*
