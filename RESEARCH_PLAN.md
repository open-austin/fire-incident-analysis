# Fire Department Resource Allocation Analysis
## Research Hub: Austin Housing & Land Use Working Group

---

## Executive Summary

**Research Question:** How can Austin expect fire coverage demands to change as the city's single-stair building code and HOME initiative drive new development patterns — particularly taller single-staircase residential buildings and increased housing density in formerly single-family neighborhoods?

**Stakeholder:** District 4 Policy Analyst Timothy Bray

**Policy Relevance:**
- Informs the single-stair/mid-rise building debate (5-story expansion effective July 2025)
- Addresses fire department concerns about aerial equipment needs (13 ladder trucks, none added since mid-1990s)
- Provides data for budget and zoning discussions
- Connects to HOME initiative impacts on residential density
- Relates to Pew report on multifamily building safety

**Core Findings (analysis complete):**
- Multifamily areas have 4-6x higher fire incident rates than single-family areas ([summary data](outputs/summary_by_housing_type.csv) · [analysis script](04_analysis.py))
- Unintentional causes (cooking, smoking) drive the gap — not arson or equipment failure ([cause data](outputs/cause_by_housing_type.csv) · [heat source data](outputs/heat_source_by_housing.csv) · [NFIRS script](06_nfirs_cause_analysis.py))
- Austin's 2006 sprinkler code reduced structure fires 141% in newer buildings ([building age data](outputs/summary_by_building_age.csv) · [analysis script](04_analysis.py))
- Higher %SF correlates with lower incident rates (r=-0.306, p<0.001) ([statistical tests](outputs/statistical_tests.txt) · [scatter plot](outputs/chart_housing_correlation.png))
- ANOVA across urban classes is significant (p=0.001) ([statistical tests](outputs/statistical_tests.txt) · [urban class data](outputs/summary_by_urban_class.csv))

---

## Data Sources

### 1. Austin Fire Department Data

| Dataset | Source | Status |
|---------|--------|--------|
| **AFD Fire Incidents 2022-2024** | Austin Open Data Portal | ✅ Downloaded |
| **AFD Fire Incidents 2018-2021** | Austin Open Data Portal | ❌ Removed from portal |
| **Fire Stations** | City of Austin ArcGIS | ✅ Downloaded |
| **AFD Response Areas** | City of Austin ArcGIS | ✅ Downloaded (711 areas) |

### 2. Census / American Community Survey Data

| Table | Variables | Status |
|-------|-----------|--------|
| **B01003** | Total Population | ✅ Downloaded |
| **B25024** | Units in Structure (housing typology) | ✅ Downloaded |
| **B25034** | Year Structure Built | ✅ Downloaded |
| **TIGER/Line** | Census Tract Boundaries (2023) | ✅ Downloaded |

### 3. Additional Data

| Dataset | Source | Status |
|---------|--------|--------|
| Zoning Districts | City of Austin ArcGIS | ✅ Downloaded (~22k polygons) |
| NFIRS Structure Fires | USFA (2018-2021) | ✅ Downloaded (manual) |

---

## Methodology

### Phase 1: Data Collection & Preparation ✅

1. **Download fire incident data** (2022-2024)
   - Automated via `01_download_data.py`
   - Cleaned and classified via `02_clean_incidents.py`

2. **Retrieve AFD response area boundaries**
   - Downloaded as GeoJSON from ArcGIS (paginated for large datasets)

3. **Pull Census demographics at tract level**
   - Population (B01003), housing units by type (B25024), housing age (B25034)

4. **Spatial crosswalk: Census tracts → Response areas**
   - Area-weighted interpolation via `03_create_crosswalk.py`
   - Validated population totals

5. **Zoning data integration** (added 2026-03-31)
   - 44 Austin BASE_ZONE codes mapped to max height/stories
   - Area-weighted allocation to response areas
   - Census-based fallback for 203 ETJ areas without zoning

### Phase 2: Classification ✅

**Urban/Suburban Classification (implemented):**

| Classification | Density (people/sq mi) |
|----------------|------------------------|
| Urban Core | ≥ 10,000 |
| Inner Suburban | 3,000 - 10,000 |
| Outer Suburban | < 3,000 |

**Housing Typology Classification (implemented):**

| Category | % Single-Family |
|----------|----------------|
| Multifamily dominant | < 25% SF |
| Mixed-low | 25-50% SF |
| Mixed-high | 50-75% SF |
| Single-family dominant | > 75% SF |

### Phase 3: Analysis ✅

**Core Metrics Calculated:** ([analysis script](04_analysis.py) · [statistical tests](outputs/statistical_tests.txt))

| Metric | Result | Source |
|--------|--------|--------|
| Incidents per 1,000 pop (urban core) | 18.78 | [summary_by_urban_class.csv](outputs/summary_by_urban_class.csv) |
| Incidents per 1,000 pop (inner suburban) | 21.92 | [summary_by_urban_class.csv](outputs/summary_by_urban_class.csv) |
| Incidents per 1,000 pop (outer suburban) | 10.84 | [summary_by_urban_class.csv](outputs/summary_by_urban_class.csv) |
| Structure fires per 1,000 units (MF areas) | 8.8 | [summary_by_housing_type.csv](outputs/summary_by_housing_type.csv) |
| Structure fires per 1,000 units (SF areas) | 2.0 | [summary_by_housing_type.csv](outputs/summary_by_housing_type.csv) |
| Correlation: %SF vs incident rate | r=-0.306 (p<0.001) | [statistical_tests.txt](outputs/statistical_tests.txt) |

**NFIRS Cause Analysis (completed):** ([NFIRS script](06_nfirs_cause_analysis.py))

| Finding | Detail | Source |
|---------|--------|--------|
| Dominant cause in MF | Unintentional (76%), primarily cooking (24%) and smoking (18%) | [cause_by_housing_type.csv](outputs/cause_by_housing_type.csv) · [heat_source_by_housing.csv](outputs/heat_source_by_housing.csv) |
| Dominant cause in SF | Unintentional (64%), with more equipment failure (16%) and heating (20%) | [cause_by_housing_type.csv](outputs/cause_by_housing_type.csv) |
| Kitchen origin | 32% of MF fires vs 20% of SF fires | [area_origin_by_housing.csv](outputs/area_origin_by_housing.csv) |
| Intentional (arson) | 6% in MF vs 10% in SF — arson is NOT driving the gap | [cause_by_housing_type.csv](outputs/cause_by_housing_type.csv) |

### Phase 4: Deliverables (in progress)

1. **Summary Statistics** ✅ — Multiple CSV outputs
2. **Interactive Maps** ✅ — 5 HTML maps (incidents, housing, stations, age, urban class)
3. **Charts** ✅ — 9+ PNG charts
4. **Analysis Report** ✅ — `outputs/REPORT_Austin_Fire_Analysis.md` (needs update with NFIRS findings)
5. **Policy Brief** — Not yet started

---

## Key Findings & Policy Implications

### Finding 1: Multifamily areas have 4-6x higher fire rates
> Source: [summary_by_housing_type.csv](outputs/summary_by_housing_type.csv) · [chart_incident_type_by_housing.png](outputs/chart_incident_type_by_housing.png) · [04_analysis.py](04_analysis.py)
- **Implication for single-stair:** Higher density development will likely increase fire call volume, but the risk is driven by cooking and smoking behavior, not building type per se
- **Implication for HOME:** Increasing density on SF lots will shift fire demand profiles

### Finding 2: Cooking and smoking drive the multifamily gap
> Source: [cause_by_housing_type.csv](outputs/cause_by_housing_type.csv) · [heat_source_by_housing.csv](outputs/heat_source_by_housing.csv) · [area_origin_by_housing.csv](outputs/area_origin_by_housing.csv) · [chart_cause_comparison.png](outputs/chart_cause_comparison.png) · [06_nfirs_cause_analysis.py](06_nfirs_cause_analysis.py)
- 76% of MF fires are unintentional (vs 64% SF)
- Kitchen fires: 32% of MF fire origins (vs 20% SF)
- Smoking: 18% of MF heat sources (vs 5% SF)
- **Implication:** Prevention programs (cooking safety, smoking policies) may be more impactful than building code changes

### Finding 3: Austin's 2006 sprinkler code is working
> Source: [summary_by_building_age.csv](outputs/summary_by_building_age.csv) · [chart_incident_types_by_age.png](outputs/chart_incident_types_by_age.png) · [04_analysis.py](04_analysis.py)
- 141% lower structure fire rates in post-2010 buildings
- **Implication for single-stair:** New 5-story buildings will have enhanced sprinkler systems, which data shows meaningfully reduces fire risk

### Finding 4: Outer suburban areas have lowest fire rates but highest coverage burden
> Source: [station_coverage.csv](outputs/station_coverage.csv) · [map_fire_stations.html](outputs/map_fire_stations.html) · [04_analysis.py](04_analysis.py)
- 170 sq mi per station (vs 1.3-4.4 in urban/inner suburban)
- Similar population-per-station ratios across all classifications
- **Implication:** The coverage challenge is geographic, not per-capita

### Confounding Variables Addressed:

| Variable | Finding | Source |
|----------|---------|--------|
| **Housing age** | Controlled — older buildings have 141% higher rates; MF areas have more old stock | [summary_by_building_age.csv](outputs/summary_by_building_age.csv) |
| **Income** | Not yet controlled (B19013 not yet integrated) | — |
| **Commercial uses** | Partially addressed — trash fires dominate in mixed-use areas | [incident_rates_by_housing_and_type.csv](outputs/incident_rates_by_housing_and_type.csv) |

---

## Tools & Environment

**Stack:**
- Python 3.14 with pandas, geopandas, shapely, folium, matplotlib, seaborn, scipy
- Virtual environment (`.venv/`)

**Scripts:**
| Script | Purpose |
|--------|---------|
| `01_download_data.py` | Fetch data from APIs |
| `02_clean_incidents.py` | Clean & classify incidents |
| `03_create_crosswalk.py` | Census → response area mapping + zoning integration |
| `04_analysis.py` | Calculate rates & statistical tests |
| `05_visualize.py` | Generate maps & charts |
| `06_nfirs_cause_analysis.py` | NFIRS cause code & building height analysis |

---

## References

- Pew Research Center report on multifamily building safety
- AFD Standard of Coverage documentation
- Austin City Council budget discussions (FY2024-2025)
- NFPA Fire Incident Data Organization (FIDO) guidelines
- NFPA Standard 1710 (response time objectives)
- AFD Fire Chief / EMS Chief joint memo (June 2024) opposing single-stair expansion
- HOME initiative ordinances (20231207-001, 20240516-006)
- Single-stair expansion vote (April 10, 2025)

---

## Contact

Research Hub - Austin Housing & Land Use Working Group
Stakeholder: Timothy Bray, District 4 Policy Analyst
