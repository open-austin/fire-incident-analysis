# Fire Resource Analysis: Task Tracker

## Project Overview

**Goal:** Analyze how Austin's fire coverage demands relate to housing density, building typology, and zoning — with focus on implications of the single-stair building code and HOME initiative.

**Stakeholder:** District 4 Policy Analyst Timothy Bray
**Output:** Data-backed brief for Research Hub + supporting visualizations
**Status:** Core analysis complete; NFIRS cause analysis complete; zoning/height integration in progress

---

## Phase 1: Data Acquisition ✅

### Task 1.1: Download Fire Incident Data
**Output:** `raw_data/afd_incidents_2022_2024.csv`

**Checklist:**
- [x] Download 2022-2024 incidents via `01_download_data.py`
- [x] ~~Download 2018-2021 incidents~~ — Dataset removed from Austin Open Data Portal; not available
- [x] 2022-2024 data used as primary dataset

**Note:** 2018-2021 historical data would require a public records request with AFD.

---

### Task 1.2: Download Response Area Boundaries
**Output:** `raw_data/afd_response_areas.geojson`

**Checklist:**
- [x] Download GeoJSON (711 response areas)
- [x] Verified geometry via interactive maps

---

### Task 1.3: Download Census Data
**Output:** `raw_data/census_population.csv`, `raw_data/census_housing.csv`, `raw_data/census_year_built.csv`, `raw_data/tl_2023_48_tract.zip`

**Checklist:**
- [x] Download population (B01003)
- [x] Download housing typology (B25024)
- [x] Download year built (B25034)
- [x] Download tract boundaries (TIGER/Line 2023)
- [x] Filter to Travis County

---

### Task 1.4: Download Supporting Data
**Checklist:**
- [x] Download fire station locations → `raw_data/fire_stations.geojson`
- [x] Download zoning districts → `raw_data/zoning.geojson` (~22k polygons)

---

## Phase 2: Data Cleaning ✅

### Task 2.1: Clean & Classify Incident Data
**Script:** `02_clean_incidents.py`
**Output:** `processed_data/incidents_clean.csv`

**Checklist:**
- [x] Parse and clean incident records
- [x] Classify incident types (structure, vehicle, outdoor, trash, other)
- [x] Validate date ranges and coordinates

---

## Phase 3: Spatial Joins & Crosswalk ✅

### Task 3.1: Build Tract → Response Area Crosswalk
**Script:** `03_create_crosswalk.py`
**Output:** `processed_data/tract_to_response_area_crosswalk.csv`

**Checklist:**
- [x] Area-weighted interpolation (chosen over centroid method)
- [x] Build crosswalk
- [x] Validate population totals

---

### Task 3.2: Aggregate Census to Response Areas
**Output:** `processed_data/response_area_demographics.csv`, `processed_data/response_areas_with_demographics.geojson`

**Checklist:**
- [x] Allocate population
- [x] Allocate housing units (SF, duplex, small MF, large MF, mobile/other)
- [x] Allocate year-built categories (pre-1970, 1970-2009, 2010+)
- [x] Calculate % SF, % MF, % new construction per area
- [x] Sanity check totals

---

### Task 3.3: Zoning-to-Height Integration (feature/building-height-data)
**Script:** `03_create_crosswalk.py` (new functions)

**Checklist:**
- [x] Map 44 Austin BASE_ZONE codes to max height/stories
- [x] Detect vertical mixed-use (`-V`) overlays → 6-story minimum
- [x] Area-weighted allocation of zoning to response areas
- [x] Census housing mix fallback for 203 ETJ areas
- [x] Coverage: 508/711 areas with zoning, 203 with census estimates, 0 with no data
- [ ] Commit changes on `feature/building-height-data`

---

## Phase 4: Classification ✅

### Task 4.1: Urban/Suburban Classification
**Checklist:**
- [x] Calculate population density per response area
- [x] Apply 3-tier classification (urban core ≥10k, inner suburban 3-10k, outer suburban <3k)
- [x] Validate via interactive map (`outputs/map_urban_classification.html`)
- [x] Cross-tab with housing typology

---

## Phase 5: Core Analysis ✅

### Task 5.1: Incident Rates
**Script:** `04_analysis.py`
**Outputs:** `outputs/summary_by_urban_class.csv`, `outputs/summary_by_housing_type.csv`

**Checklist:**
- [x] Count incidents by response area and type
- [x] Calculate per-capita and per-unit rates
- [x] Break down by incident type (structure, vehicle, outdoor, trash)
- [x] Year-over-year trends (2022, 2023, 2024)

---

### Task 5.2: Statistical Tests
**Output:** `outputs/statistical_tests.txt`

**Checklist:**
- [x] T-tests: urban vs suburban (ANOVA p=0.001, significant)
- [x] Correlation: %SF vs incident rate (r=-0.306, p<0.001)
- [x] Building age analysis (141% higher structure fire rate in older stock)

**Key Results:**
- Urban core mean: 18.78 incidents/1,000 pop
- Inner suburban mean: 21.92/1,000
- Outer suburban mean: 10.84/1,000
- Multifamily areas: 4-6x higher fire rates than single-family areas
- Negative correlation between %SF and incident rate

---

### Task 5.3: NFIRS Cause Analysis ✅
**Script:** `06_nfirs_cause_analysis.py`
**Outputs:** `outputs/cause_by_housing_type.csv`, `outputs/heat_source_by_housing.csv`, `outputs/area_origin_by_housing.csv`, `outputs/sprinkler_by_housing.csv`

**Checklist:**
- [x] Extract Austin fire incidents from NFIRS (TX FDID WP801, 2018-2021)
- [x] Cause of ignition by housing type (76% unintentional in MF vs 64% in SF)
- [x] Heat source breakdown (cooking #1 in both; smoking 18% in MF vs 5% in SF)
- [x] Area of origin (kitchen 32% in MF vs 20% in SF)
- [x] Sprinkler analysis (no sprinklers recorded as "present" in either type)

---

### Task 5.4: Building Height Analysis (in progress)
**Script:** `06_nfirs_cause_analysis.py` (new functions)

**Checklist:**
- [x] Extract NFIRS building characteristics (BLDG_ABOVE, STRUC_TYPE, etc.)
- [x] Categorize fires by building height (1-2, 3-4, 5-7, 8+ stories)
- [x] Cross-tab with fire spread, cause, sprinklers, property loss
- [ ] Generate outputs (requires NFIRS data download)
- [ ] Suburban vs urban contrast analysis

---

## Phase 6: Visualization ✅

### Task 6.1: Interactive Maps
**Script:** `05_visualize.py`

- [x] `map_incidents_per_capita.html` — Incident rates choropleth
- [x] `map_building_age.html` — Building age distribution
- [x] `map_fire_stations.html` — Station locations
- [x] `map_housing_typology.html` — Housing type distribution
- [x] `map_urban_classification.html` — Urban/suburban classification

---

### Task 6.2: Charts

- [x] `chart_urban_comparison.png` — Incident rates by urban class
- [x] `chart_incident_type_by_housing.png` — Incident types by housing classification
- [x] `chart_incident_types_by_age.png` — Incident types by building age
- [x] `chart_structure_fires_by_housing.png` — Structure fire trends by housing type
- [x] `chart_structure_fires_by_urban.png` — Structure fire trends by urban class
- [x] `chart_cause_comparison.png` — NFIRS cause comparison (MF vs SF)
- [x] `chart_heat_source_comparison.png` — Heat source comparison
- [x] `chart_housing_correlation.png` — Housing type correlation
- [x] `table_summary.png` — Summary statistics table

---

## Phase 7: Write-Up (partially complete)

### Task 7.1: Draft Key Findings
**Output:** `outputs/REPORT_Austin_Fire_Analysis.md`

**Checklist:**
- [x] Main finding stated (multifamily 4-6x higher rates)
- [x] Specific numbers included
- [x] Limitations noted
- [x] Sprinkler code effectiveness documented (141% reduction)
- [ ] Update report with NFIRS cause analysis findings
- [ ] Update report with zoning/building height context
- [ ] Policy implications for single-stair and HOME

---

### Task 7.2: Review with Tim
- [ ] Schedule meeting
- [ ] Share draft beforehand
- [ ] Incorporate feedback

---

### Task 7.3: Finalize Deliverables
- [x] Summary stats (CSV) — multiple output CSVs
- [x] Maps (HTML interactive) — 5 maps
- [x] Charts (PNG) — 9+ charts
- [x] Analysis report (Markdown + HTML)
- [ ] 1-2 page policy brief (PDF)
- [ ] Methodology appendix

---

## Time Summary

| Phase | Est. Hours | Status |
|-------|-----------|--------|
| 1. Data Acquisition | 4-6 | ✅ Complete |
| 2. Data Cleaning | 2-3 | ✅ Complete |
| 3. Spatial Joins & Crosswalk | 6-8 | ✅ Complete |
| 4. Classification | 2-3 | ✅ Complete |
| 5. Core Analysis + NFIRS | 8-10 | ✅ Complete |
| 6. Visualization | 3-5 | ✅ Complete |
| 7. Write-Up & Review | 5-6 | 🔄 In progress |
| **Total** | **30-41** | |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| — | Use 2022-2024 data only | 2018-2021 dataset removed from Austin Open Data Portal |
| — | Area-weighted interpolation over centroid | More accurate for response areas spanning multiple census tracts |
| — | 3-tier urban classification (10k/3k thresholds) | Simple, defensible, validated by visual inspection |
| — | Use 2006 sprinkler code as age threshold | Austin adopted residential sprinkler requirement Jan 1, 2006; ~2010 construction lag |
| 2026-03-31 | Zoning codes as building height proxy | Current data, full city coverage, maps to what can be built under LDC |
| 2026-03-31 | Census B25024 housing mix as ETJ height fallback | 203/711 response areas lack zoning; housing type mix is reasonable proxy |
| 2026-03-31 | Flag estimated vs zoning-derived height data | `height_data_source` column distinguishes data quality for downstream analysis |
| 2026-03-31 | Area-weighted allocation over centroid assignment | More accurate for large response areas spanning multiple zoning districts |
| 2026-03-31 | Vertical mixed-use overlay → 6-story minimum | `-V` overlay explicitly permits taller buildings regardless of base zone |

---

## Next Action

**Remaining work:**
1. Commit zoning/height changes on `feature/building-height-data`
2. Update analysis report with NFIRS cause findings and zoning context
3. Draft policy brief connecting findings to single-stair and HOME implications
4. Review with Timothy Bray
