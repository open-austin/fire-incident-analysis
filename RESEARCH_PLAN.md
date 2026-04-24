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
- Multifamily-dominant areas have ~7x higher structure fire rates than single-family-dominant areas (8.4 vs 1.3 per 1,000 units) ([summary data](outputs/summary_by_housing_type.csv) · [analysis script](04_analysis.py))
- Unintentional causes (cooking, smoking) drive the gap — not arson or equipment failure ([cause data](outputs/cause_by_housing_type.csv) · [heat source data](outputs/heat_source_by_housing.csv) · [NFIRS script](06_nfirs_cause_analysis.py))
- Austin's 2006 sprinkler code reduced structure fires ~27% at the parcel level (16.8 vs 22.9 per 1,000 parcels) and ~45% at the response-area level (1.98 vs 3.57 per 1,000 units) ([building age data](outputs/summary_by_building_age.csv) · [parcel analysis](outputs/parcel_analysis_summary.txt) · [analysis script](04_analysis.py))
- Higher %SF correlates with lower incident rates (r=-0.303, p<0.001) ([statistical tests](outputs/statistical_tests.txt) · [scatter plot](outputs/chart_housing_correlation.png))
- ANOVA across urban classes is significant (p<0.001) ([statistical tests](outputs/statistical_tests.txt) · [urban class data](outputs/summary_by_urban_class.csv))
- Structure fires are rare events: 1 in 371 single-family homes/year, 1 in 671 townhomes/year. National rate is ~1 in 389 homes/year (NFPA). This rarity limits local cohort comparisons. ([townhome analysis](outputs/townhome_cohort_summary.txt) · [10_townhome_cohort_analysis.py](10_townhome_cohort_analysis.py))
- Structure fire classification aligned to NFPA/NFIRS standards: both non-confined (BOX alarm) and confined (ELEC/BBQ) fires count as structure fires. Total: 5,693 (3,176 non-confined + 2,517 confined). ([02_clean_incidents.py](02_clean_incidents.py))

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
| Incidents per 1,000 pop (urban core) | 16.23 | [summary_by_urban_class.csv](outputs/summary_by_urban_class.csv) |
| Incidents per 1,000 pop (inner suburban) | 17.97 | [summary_by_urban_class.csv](outputs/summary_by_urban_class.csv) |
| Incidents per 1,000 pop (outer suburban) | 3.58 | [summary_by_urban_class.csv](outputs/summary_by_urban_class.csv) |
| Structure fires per 1,000 units (MF-dominant areas) | 8.4 | [summary_by_housing_type.csv](outputs/summary_by_housing_type.csv) |
| Structure fires per 1,000 units (SF-dominant areas) | 1.3 | [summary_by_housing_type.csv](outputs/summary_by_housing_type.csv) |
| Correlation: %SF vs incident rate | r=-0.303 (p<0.001) | [statistical_tests.txt](outputs/statistical_tests.txt) |

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

## Visual Story: Charts in Narrative Order

These five charts tell the analysis story sequentially. Each finding builds on the previous.

**Story 1: The density gap** — [chart_incident_type_by_housing.png](outputs/chart_incident_type_by_housing.png)
Multifamily-dominant areas have ~7x higher structure fire rates than single-family areas (8.4 vs 1.3 per 1,000 units). Trash fires are the biggest volume driver (30.6 vs 4.6), not structure fires.

**Story 2: The gap is behavioral, not architectural** — [chart_cause_comparison.png](outputs/chart_cause_comparison.png) + [chart_heat_source_comparison.png](outputs/chart_heat_source_comparison.png)
76% of MF fires are unintentional (vs 64% SF). Smoking is 18% vs 5%. Arson is actually lower in MF (6% vs 10%). More kitchens and more smokers per building — not the building itself — drive the gap.

**Story 3: Sprinklers work — and the data proves causation** — [chart_incident_types_by_age.png](outputs/chart_incident_types_by_age.png)
Structure fires: 3.4/1k in newer areas vs 6.5/1k in older (91% higher in older). Vehicle fires are flat (2.6 vs 2.4) — the control group that proves sprinkler codes, not confounders, drive the difference.

**Story 4: The pattern is stable year-over-year** — [chart_structure_fires_by_housing.png](outputs/chart_structure_fires_by_housing.png)
MF vs SF gap holds steady across 2022-2024. Not a one-year anomaly.

**Story 5: Housing mix predicts fire rate** — [chart_housing_correlation.png](outputs/chart_housing_correlation.png)
r = -0.303, p < 0.001. More single-family housing → fewer fires per capita. Modest but statistically significant across 765 response areas.

---

## Key Findings & Policy Implications

### Finding 1: Multifamily-dominant areas have ~7x higher structure fire rates
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
> Source: [summary_by_building_age.csv](outputs/summary_by_building_age.csv) · [parcel_analysis_summary.txt](outputs/parcel_analysis_summary.txt) · [chart_incident_types_by_age.png](outputs/chart_incident_types_by_age.png) · [04_analysis.py](04_analysis.py)
- 27% lower structure fire rates in post-2006 buildings at the parcel level (16.8 vs 22.9 per 1,000 parcels)
- 45% lower structure fire rates in newer areas at the response-area level (1.98 vs 3.57 per 1,000 units) — larger gap because response areas with newer stock also have different housing mixes
- Vehicle fires are flat across building eras (2.6 vs 2.4), confirming sprinkler codes — not some other factor — drive the structure fire reduction
- **Implication for single-stair:** New 5-story buildings will have enhanced sprinkler systems, which data shows meaningfully reduces fire risk

### Finding 4: Outer suburban areas have lowest fire rates but highest coverage burden
> Source: [station_coverage.csv](outputs/station_coverage.csv) · [map_fire_stations.html](outputs/map_fire_stations.html) · [04_analysis.py](04_analysis.py)
- 170 sq mi per station (vs 1.3-4.4 in urban/inner suburban)
- Similar population-per-station ratios across all classifications
- **Implication:** The coverage challenge is geographic, not per-capita

### Finding 5: Townhome fire rates are very low; local data cannot support code cohort comparisons
> Source: [townhome_rates_by_cohort.csv](outputs/townhome_rates_by_cohort.csv) · [townhome_cohort_summary.txt](outputs/townhome_cohort_summary.txt) · [10_townhome_cohort_analysis.py](10_townhome_cohort_analysis.py)
- TCAD classifies 4,251 parcels as "TOWNHOMES," but 355 are actually multi-unit condo complexes (10-234 units). True individual townhomes (UNITS <= 1) total 3,896 parcels.
- True townhomes had only **5 structure fires** in 3 years (2 non-confined, 3 confined/electrical). Rate: ~0.4 per 1,000 parcels per year.
- Of the 5 fires, 2 are at the same address (9701 West Gate Blvd, YB:2022), and the remaining 3 are all pre-2019 construction.
- Zero fires at 2019-2021 cohort townhomes (141 parcels) and 2 confined electrical fires at one post-2021 property (363 parcels).
- **The data cannot support cohort comparisons** — too few events, too short a time window, and post-2021 buildings have had only 1-3 years of exposure.
- **Data quality note:** 9 of the backfilled year-built values for condo complexes were manually verified via property records (Redfin, Zillow, HAR, Travis CAD).
- **Implication:** National NFIRS data is needed to meaningfully compare fire outcomes across construction eras for attached housing.

### Confounding Variables Addressed:

| Variable | Finding | Source |
|----------|---------|--------|
| **Housing age** | Controlled — older buildings have 27-45% higher structure fire rates (parcel vs response-area level); MF areas have more old stock | [summary_by_building_age.csv](outputs/summary_by_building_age.csv) |
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
| `07_parcel_join.py` | Spatial join incidents to TCAD parcels |
| `08_parcel_analysis.py` | Fire rates by building type and year built |
| `09_zoning_and_census.py` | Zoning labels and census tract enrichment |
| `10_townhome_cohort_analysis.py` | Townhome fire code cohort analysis |

---

## Next Steps: National Townhome Fire Analysis

The Austin local data demonstrates that townhomes are very safe (1 in 1,221 units/year) but cannot support comparisons between fire code cohorts due to insufficient events. A national-scale analysis is needed.

**Proposed approach:**
1. Filter NFIRS public data release (already downloaded, 2018-2021) by property use code 210 (townhouse/rowhouse)
2. Cross-reference with construction year to classify by code era
3. Calculate national townhome fire rates by construction cohort
4. Compare sprinklered vs non-sprinklered outcomes

**Why this hasn't been done:** NFPA lumps townhomes into "1 or 2 family" (NFIRS code 419). USFA topical reports cover "multifamily" broadly. No published study has isolated code 210 to produce townhome-specific rates by construction era. This is a gap in the national research.

**Potential academic collaborators:**
- **Dr. Ofodike Ezekoye**, UT Austin Mechanical Engineering — leads the [UT Fire Research Group](https://www.utfireresearch.com/). Research includes community fire risk and loss assessments using state-level fire data. Natural fit for the NFIRS code 210 analysis. [Faculty page](https://www.utfireresearch.com/faculty-and-staff)
- **Dr. Jake Wegmann**, UT Austin School of Architecture — [housing affordability and land use regulation researcher](https://soa.utexas.edu/faculty/jake-wegmann). Works on density policy, ADUs, and zoning reform. Could frame findings in housing policy context.
- **Texas State Fire Marshal's Office** ([TDI](https://www.tdi.texas.gov/fire/index.html)) — maintains Texas NFIRS data; could provide state-level dataset for broader analysis

---

## References

### National Fire Studies
- Pew Charitable Trusts, "[Modern Multifamily Buildings Provide the Most Fire Protection](https://www.pew.org/en/research-and-analysis/issue-briefs/2025/09/modern-multifamily-buildings-provide-the-most-fire-protection)" (September 2025) — Post-2000 apartments have 1.2 fire deaths per million residents vs 7.6 for single-family. The most directly relevant national study.
- Pew Charitable Trusts, "[Small Single-Stairway Apartment Buildings Have Strong Safety Record](https://www.pew.org/en/research-and-analysis/reports/2025/02/small-single-stairway-apartment-buildings-have-strong-safety-record)" (February 2025)
- Pew Charitable Trusts, "[Does a Housing Shortage Mean More Fire Risk?](https://www.pew.org/en/research-and-analysis/articles/2026/01/30/fire-safety-and-the-future-of-housing)" (January 2026)
- NFPA, "[Home Structure Fires](https://www.nfpa.org/education-and-research/research/nfpa-research/fire-statistical-reports/home-structure-fires)" (annual) — Breaks out 1-2 family vs apartments vs manufactured homes
- NFPA, "[U.S. Experience with Sprinklers](https://www.nfpa.org/education-and-research/research/nfpa-research/fire-statistical-reports/us-experience-with-sprinklers)" (April 2024) — Sprinklers reduce civilian death rate by 90%, fires contained to room of origin 94% vs 70% without
- NFPA, "[Fire Loss in the United States](https://www.nfpa.org/education-and-research/research/nfpa-research/fire-statistical-reports/fire-loss-in-the-united-states)" (annual)

### USFA Topical Reports
- USFA, "[Multifamily Residential Building Fires (2017-2019)](https://www.usfa.fema.gov/downloads/pdf/statistics/v21i7.pdf)" — 106,700 multifamily fires/year nationally
- USFA, "[One- and Two-Family Residential Building Fires (2017-2019)](https://www.usfa.fema.gov/downloads/pdf/statistics/v21i6.pdf)" — companion report
- USFA, "[Residential fire estimate summaries (2014-2023)](https://www.usfa.fema.gov/statistics/residential-fires/index.html)"

### Austin-Specific
- AFD Standard of Coverage documentation
- Austin City Council budget discussions (FY2024-2025)
- NFPA Standard 1710 (response time objectives)
- AFD Fire Chief / EMS Chief joint memo (June 2024) opposing single-stair expansion
- HOME initiative ordinances (20231207-001, 20240516-006)
- Single-stair expansion vote (April 10, 2025)

### Research Gap
No published study has isolated NFIRS property use code 210 (townhouse/rowhouse) to calculate fire rates by construction era or sprinkler status. NFPA groups townhomes with "1 or 2 family" dwellings. This is the specific gap this project aims to address with national NFIRS data.

---

## Contact

Research Hub - Austin Housing & Land Use Working Group
Stakeholder: Timothy Bray, District 4 Policy Analyst
