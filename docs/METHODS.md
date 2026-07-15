# Methods & data provenance

**The rule:** no number ships without its provenance. Every quantitative claim in any deliverable — report, handout, README, issue comment, chart caption — must be traceable to (1) the source data, (2) the exact transformation, and (3) a way to reproduce it. A figure a reader can't trace is a claim they can't check, and we don't publish those.

This file is both the **standard** (how to document a claim) and the **ledger** (the documented claims). When you add or change a number in a deliverable, add or update its ledger entry here and link to it.

---

## The standard — what every claim must carry

For each claim, record these four things:

| Field | What it means |
|---|---|
| **Claim** | The number/statement as it appears in the deliverable (verbatim). |
| **Source** | The input file(s) and the specific columns used. Pin the version if it matters (e.g. "2025 certified roll"). |
| **Formula** | The transformation from source rows to the number — as a formula and/or the notebook cell / script line that computes it. Include filters, weights, and defaults (what happens to nulls/unknowns). |
| **Reproduce** | A copy-paste snippet or an exact `notebook.ipynb → cell N` / `script.py:line` pointer that regenerates the number. |

**Conventions**
- State **units** and **denominators** explicitly (per acre? per 1,000 pop? share of what total?).
- State the **filter** that defines the population ("developed parcels ≤ 5 acres", "served response areas with value>0 and calls>0").
- State how **unknowns/nulls** are handled (dropped? defaulted?). These silently move totals.
- If a number is an **assumption or external constant** (a tax rate, a budget), cite the external source, not a computation.
- Prefer numbers that a **validation check** re-derives on every run (see `notebooks/validation.ipynb` → `outputs/validation_report.csv`).

**Definition of done for a claim:** a reader can open the Source, run the Reproduce step, and get the Claim — without asking the author anything.

---

## Ledger

### Weighted fire demand by category
*(used in: `docs/working/pr13/handout.md` §A, `docs/FIRE_FISCAL_FULL_REPORT.md` §2.6 / §5.4)*

- **Claim.** Vehicle+outdoor+trash fires are 31.9% of weighted demand (65,166 total) though 73% of the 20,920 incident records; category shares 48.7 / 19.3 / 14.8 / 10.4 / 6.7 / 0.0%.
- **Source.** `processed_data/incidents_enriched.csv`, column `incident_category` (one row per incident; `responsearea` used when aggregating per area).
- **Formula.** Each incident gets a weight from `WEIGHTS = {Structure non-confined 10, Structure confined 5, Vehicle 2, Outdoor/Vegetation 2, Trash/Dumpster 1, Other 1}`; unknown categories default to 1. `weighted(cat) = count(cat) × weight(cat)`; `total = Σ weighted = 65,166`; `% of demand = weighted(cat) / total`. The weight is a severity/resource proxy (a structure fire commits ~10× the crew/equipment of a trash fire), so this measures resource *load*, not call *count*.
- **Reproduce.**
  ```bash
  .venv/bin/python - <<'PY'
  import pandas as pd
  W={'Structure Fire (non-confined)':10,'Structure Fire (confined)':5,'Vehicle Fire':2,
     'Outdoor/Vegetation Fire':2,'Trash/Dumpster Fire':1,'Other':1}
  inc=pd.read_csv('processed_data/incidents_enriched.csv', usecols=['incident_category'])
  inc['w']=inc['incident_category'].map(W).fillna(1)
  g=inc.groupby('incident_category')['w'].agg(count='count', weighted='sum')
  g['pct']=(100*g['weighted']/g['weighted'].sum()).round(1)
  print(g.sort_values('weighted',ascending=False)); print('total weighted', g['weighted'].sum())
  PY
  ```
  Canonical definition: `notebooks/fire_use_vs_pays.ipynb` cells 2 (weights) and 4 (applied).

### Cost-model verdict agreement (road-mile vs land)
*(used in: `docs/working/pr13/handout.md` §B)*

- **Claim.** 35 of 46 cities (76%) keep the same verdict under both cost models; 11 flip; correlation r = 0.85; unincorporated county −16,098 (land) vs −15,999 (road) per acre.
- **Source.** `outputs/city_fiscal_verdicts.csv`, columns `net_land`, `net_road`, `city`.
- **Formula.** A city "keeps its verdict" when `sign(net_land) == sign(net_road)`. Agreement = keepers / 46. `r = corr(net_land, net_road)`. net_* are per-acre net dollars (revenue-minus-cost), computed in `notebooks/fiscal_productivity.ipynb`.
- **Reproduce.**
  ```bash
  .venv/bin/python - <<'PY'
  import pandas as pd, numpy as np
  v=pd.read_csv('outputs/city_fiscal_verdicts.csv')
  keep=(np.sign(v.net_land)==np.sign(v.net_road)).sum()
  print(f'{keep}/{len(v)} keep verdict | r={v.net_land.corr(v.net_road):.3f}')
  print(v[v.city.str.contains("nincorp")][['city','net_land','net_road']])
  PY
  ```

### Non-structure demand by area type
*(used in: `docs/working/pr13/handout.md` §A)*

- **Claim.** Non-structure fires are 23.9% of urban_core demand, 31.4% inner_suburban, 36.4% outer_suburban; removing them shifts urban_core's share of total demand 3.4→3.8% and outer_suburban 21.4→20.0%.
- **Source.** `processed_data/incidents_enriched.csv` (`responsearea`, `incident_category`) joined to `processed_data/response_areas_final.geojson` (`response_area_id`, `urban_class`).
- **Formula.** Per response area, sum weighted demand (as above) for all fires vs. structure-only (excluding Vehicle/Outdoor/Trash); group by `urban_class`; compare each class's share of the all-fires total vs the structure-only total.
- **Reproduce.** See `docs/working/pr13/handout.html` methods note, or the snippet in the decision-memo journal note.

### Revenue definition
*(used throughout the fiscal report and handout §C)*

- **Claim.** `revenue = market_value × 0.021`; a uniform rate means value-per-acre and revenue-per-acre rank identically.
- **Source / constant.** `EFFECTIVE_TAX_RATE = 0.021`, defined once at `report_pipeline/13_build_metro_parcels.py:22`. This is an **external assumption** (blended jurisdiction rate), not a computed value — see `docs/FIRE_FISCAL_FULL_REPORT.md` footnote `[^rate]` for the sourcing.
- **Formula.** Constant multiplier ⇒ `rank(value/acre) ≡ rank(revenue/acre)`. An exemption-sensitive version needs per-parcel `taxable_value` (populated Travis-only, `13_build_metro_parcels.py:66`).

---

## Adding a new claim
1. Compute it in a notebook/script (not by hand).
2. Add a ledger entry above with the four fields.
3. In the deliverable, keep a short pointer (e.g. "see `docs/METHODS.md` → *Weighted fire demand*").
4. If it can be re-derived cheaply, add it to `notebooks/validation.ipynb` so it's checked on every run.
