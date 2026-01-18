# Fire Resource Analysis: Execution Plan

## Overview

**Goal:** Test whether suburban areas consume disproportionate fire resources per capita compared to urban areas.

**Timeline:** 2-3 weeks (part-time)

**Your Stack:** Python + pandas/geopandas, potentially Tableau for visualization

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run scripts in order
python scripts/01_download_data.py
python scripts/02_clean_incidents.py
python scripts/03_create_crosswalk.py
python scripts/04_analysis.py
python scripts/05_visualize.py
```

---

## Phase 1: Data Acquisition (Days 1-2)

| Task | Script | Output |
|------|--------|--------|
| Download fire incidents | `01_download_data.py` | `raw_data/afd_incidents_*.csv` |
| Download response area boundaries | `01_download_data.py` | `raw_data/afd_response_areas.geojson` |
| Download census data | `01_download_data.py` | `raw_data/census_*.csv` |
| Download tract boundaries | `01_download_data.py` | `raw_data/tl_2023_48_tract.*` |

**Checkpoint:** Verify all files downloaded successfully

---

## Phase 2: Data Preparation (Days 3-5)

| Task | Script | Output |
|------|--------|--------|
| Clean & combine incidents | `02_clean_incidents.py` | `processed_data/incidents_clean.csv` |
| Classify incident types | `02_clean_incidents.py` | `outputs/incident_type_summary.csv` |
| Create tract→response area crosswalk | `03_create_crosswalk.py` | `processed_data/tract_to_response_area_crosswalk.csv` |
| Allocate demographics | `03_create_crosswalk.py` | `processed_data/response_areas_with_demographics.geojson` |

**Checkpoint:** Review urban/suburban classification on a map

---

## Phase 3: Analysis (Days 6-8)

| Task | Script | Output |
|------|--------|--------|
| Join incidents to response areas | `04_analysis.py` | `processed_data/incidents_with_demographics.csv` |
| Calculate per-capita rates | `04_analysis.py` | `processed_data/response_areas_final.geojson` |
| Summary by urban class | `04_analysis.py` | `outputs/summary_by_urban_class.csv` |
| Summary by housing type | `04_analysis.py` | `outputs/summary_by_housing_type.csv` |
| Statistical tests | `04_analysis.py` | `outputs/statistical_tests.txt` |

**Checkpoint:** Do findings support Tim's hypothesis?

---

## Phase 4: Visualization (Days 9-10)

| Task | Script | Output |
|------|--------|--------|
| Choropleth: incidents per capita | `05_visualize.py` | `outputs/map_incidents_per_capita.html` |
| Choropleth: urban classification | `05_visualize.py` | `outputs/map_urban_classification.html` |
| Bar chart comparison | `05_visualize.py` | `outputs/chart_urban_comparison.png` |
| Scatter: housing vs incidents | `05_visualize.py` | `outputs/chart_housing_correlation.png` |

---

## Key Decision Points

1. **Which incidents to include?**
   - All fire calls (broader resource question)
   - Structure fires only (safety question)
   - Recommendation: Do both analyses

2. **Urban/suburban thresholds?**
   - Urban core: >10,000 people/sq mi
   - Inner suburban: 3,000-10,000/sq mi
   - Outer suburban: <3,000/sq mi
   - Adjust based on Austin context if needed

3. **How to handle edge cases?**
   - Low-population areas: Exclude or flag as unreliable
   - Areas outside city limits: Check jurisdiction field

---

## Data Sources

| Data | Source | API/URL |
|------|--------|---------|
| Fire Incidents 2022-2024 | Austin Open Data | `data.austintexas.gov/resource/v5hh-nyr8.json` |
| Fire Incidents 2018-2021 | Austin Open Data | `data.austintexas.gov/resource/j9w8-x2vu.json` |
| Response Area Boundaries | City of Austin ArcGIS | `services.arcgis.com/0L95CJ0VTaxqcmED/...` |
| Census Population | Census API | Table B01003 |
| Housing Units by Type | Census API | Table B25024 |
| Census Tract Boundaries | Census TIGER/Line | 2023 vintage |

---

## Expected Outputs

### Primary Finding
*"Suburban areas have X% more/fewer fire incidents per capita than urban areas"*

### Supporting Evidence
- Statistical test results (t-test, ANOVA)
- Correlation between % single-family and incident rate
- Maps showing spatial patterns

### Policy Implications
- If suburban > urban: Sprawl imposes hidden fire service costs
- If suburban ≤ urban: Density concerns may be overstated
