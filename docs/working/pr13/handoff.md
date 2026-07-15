# Handoff: Working through Eric's PR #13 feedback

## Context
- Eric Kylberg (GitHub `kialburg`) reviewed the Fire-Fiscal report and filed feedback as
  **Issue #14** ("Eric's Feedback on PR13") — NOT as PR comments (the PR itself has none).
- Repo: `open-austin/fire-incident-analysis`. Working branch: **`report-citations`** (this is the
  branch behind **PR #13**; every push updates that PR).
- Files under review: `docs/FIRE_FISCAL_FULL_REPORT.md` (primary) and `docs/FISCAL_PRODUCTIVITY_REPORT.md`.

## Workflow we agreed on (keep using it)
1. Track progress on the **checklist comment on Issue #14** (issue #14, comment id `4974591351`).
   Update it with `gh api -X PATCH repos/open-austin/fire-incident-analysis/issues/comments/4974591351 -F body=@file`.
2. **One focused commit per item**, message ending with `(#14)` so GitHub links it.
3. Push to `report-citations` to update PR #13. Chase is new to git — explain steps, don't do
   big destructive git ops. Don't touch the stale local branches (`productivity_map`,
   `repo-review-cleanup`, `townhome-national-comparison`) — cleanup is a separate later chore.

## DONE this session (commit `53872e7`, pushed)
- §2.6: defined "apparatus"/"company" + added Firefighting-apparatus Wikipedia link in `[^appw]`.
- §5.3: added the missing Herriges/Strong Towns URL to `[^vprm]` (this is rendered citation [23]).
- §5.4: **Confirmed Eric's suspected bug is real.** `coverage_share = 1.0/len(t)` was commented
  `# each zone = one staffed company` — false: there are **765 response areas (~285 served) but
  only 64 AFD stations**, so a zone is not a company. Also confirmed **response areas are AFD's own
  operational dispatch boxes** (`raw_data/afd_response_areas.geojson`), NOT adapted census tracts —
  census demographics are crosswalked ONTO them (`incident_pipeline/03_create_crosswalk.py`).
  Fixed the false label in report prose, the report's "real code excerpts" block, and the notebook
  comment (`notebooks/fire_use_vs_pays.ipynb`). Flat lens now honestly described as an even standby
  *floor*, not one-company-per-area.

## Key facts verified (so next AI doesn't re-derive)
- 765 total AFD response areas; ~285 "served" (filter: prop_value>0 AND weighted calls>0).
- 64 AFD stations.
- Model lives in `notebooks/fire_use_vs_pays.ipynb`. Flat coverage lens = `1/len(t)`.
  Apparatus-weighted lens (cells ~10) maps each area to nearest station and splits the station's
  apparatus weight among its zones (`cov_appar = sw / n_per`) — the more defensible model.
- AFD_BUDGET = 264_000_000 (approved GF requirement is $262.2M).

## STILL TO DO (from Issue #14 checklist)

### Verify (possible bug) — 1 left
- §4.1 — double-check Group A property/value figures; define "post-filter"; reduce cross-county
  description variance (Eric wants inter-compatibility emphasized, differences downplayed).

### Judgment calls — NEED CHASE'S DECISION before implementing
- §2.1–2.2 — Revenue vs. Property Value are commingled; pick one (Eric leans Revenue) or clarify.
- §2.4 — Eric wants "Fiscal productivity & break-even" cut (says it adds no value, clunky).
- §2.6 / study-wide — remove vehicle & trash fires entirely? (recurs in the demand-lens critique too)
- §5.3 / §6.2 — cut the road-mile / Strong Towns cost model? Eric says it reads as data-fishing and
  an unintended "roads are bad" argument. (NOTE: if cut, the [23] link fix above becomes moot.)
- §5.4 — use tax revenue instead of assessed value for the share (accounts for SFH tax breaks)?
- §4.2 — reconsider using Response Areas at all.
- §5.4 — add a data-gaps caveat paragraph (call severity, deployed resources, incident-level damage).

### New analysis (larger)
- Add census income data as a confounding variable (both reports). Eric's prelim work says it
  strengthens the position. Income data is already on hand.
- Address daytime vs. nighttime population density (downtown ~20k census vs ~100k daytime).
- Evaluate Eric's `notebooks/population_per_station.ipynb` coverage model as an alternative/replacement
  for the nearest-station weighting.

### Parked
- Effective tax rate case-by-case (likely skip). Income demographics as an equity angle.

## First suggested next step
Walk Chase through the **judgment calls** (they gate the biggest edits, esp. removing vehicle/trash
fires and the road-mile model). Then §4.1 figure verification. Use AskUserQuestion for the removals.
