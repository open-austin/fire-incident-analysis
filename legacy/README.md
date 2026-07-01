# Legacy scripts

Earlier analysis passes that the current pipelines superseded. Kept for reference —
nothing in `incident_pipeline/`, `report_pipeline/`, the notebooks, or the docs
imports or invokes them.

| Script | What it was | Superseded by |
|---|---|---|
| `03b_join_census_to_incidents.py` | Alternate census→incident join | `incident_pipeline/03_create_crosswalk.py` |
| `04b_analysis_by_census_tract.py` | Tract-level variant of the main analysis | `incident_pipeline/04_analysis.py` |
| `07_parcel_join.py` | Spatial join of incidents to parcels | `report_pipeline/12`–`13` parcel pipeline |
| `08_parcel_analysis.py` | Per-parcel fire rates by building type | fiscal notebooks |
| `09_zoning_and_census.py` | Zoning + census enrichment | `incident_pipeline/03_create_crosswalk.py` |
| `10_townhome_cohort_analysis.py` | Townhome code-era cohort analysis | — (analysis complete; see note) |

**Note on `10_townhome_cohort_analysis.py`:** the townhome analysis still has open
follow-ups (national NFIRS comparison and expert outreach — PROJECT_TASKS.md tasks 5
and 7), so this script may come back into service; that's why it lives here rather
than being deleted.

These scripts expect the pre-reorganization flat layout and may need path tweaks
if resurrected.
