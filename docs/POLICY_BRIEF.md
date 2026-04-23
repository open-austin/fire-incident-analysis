# Policy Brief: Fire Coverage Impacts of Single-Stair and HOME Development Patterns

**Prepared for:** Timothy Bray, Policy Analyst, District 4
**Prepared by:** Austin Housing & Land Use Working Group Research Hub
**Date:** April 2026

---

## Summary

Austin's single-stair building code expansion (effective July 2025) and HOME initiative are reshaping the city's housing landscape. This brief summarizes what fire incident data tells us about how these changes will affect fire coverage demands — and what the data suggests policymakers should prioritize.

**Bottom line:** Higher-density housing does increase fire call volume, but the drivers are behavioral (cooking, smoking), not architectural. New construction benefits from Austin's 2006 sprinkler code, which has cut structure fire rates by 27% at the parcel level (and up to 45% at the response-area level). The primary infrastructure gap is aerial equipment, not station coverage. Structure fires are rare events -- a typical Austin home has about a 1 in 371 chance per year -- which limits what local data can tell us about code-level comparisons.

---

## Key Findings

### 1. Density increases fire call volume — but the causes are preventable

Multifamily-dominant areas experience **~7x higher structure fire rates** than single-family-dominant areas (8.4 vs 1.3 per 1,000 housing units). However, NFIRS cause data shows this gap is driven by **unintentional factors**:

- **76% of multifamily fires are unintentional** vs. 64% in single-family ([cause data](../outputs/cause_by_housing_type.csv))
- **Cooking** is the top heat source in both housing types (~24%), but **kitchen fires** account for 32% of multifamily origins vs. 20% in single-family ([area of origin data](../outputs/area_origin_by_housing.csv))
- **Smoking** is 4x more common as a heat source in multifamily (18% vs. 5%) ([heat source data](../outputs/heat_source_by_housing.csv))
- **Arson is not driving the gap** — intentional fires are actually lower in multifamily (6%) than single-family (10%)

> Source: [NFIRS cause analysis](../06_nfirs_cause_analysis.py) · [cause comparison chart](../outputs/chart_cause_comparison.png)

### 2. Austin's sprinkler code is working — new construction is significantly safer

Post-2006 buildings have **27% lower structure fire rates** at the parcel level (16.8 vs 22.9 per 1,000 parcels). At the response-area level, areas with newer building stock show an even larger gap — **45% lower** (1.98 vs 3.57 per 1,000 units). Vehicle fires are flat across building eras (2.6 vs 2.4 per 1,000 units), confirming the sprinkler code — not some other factor — drives the reduction.

| Building Stock | Structure Fires per 1,000 Units |
|---|---|
| Newer (50%+ post-2010) | 1.98 |
| Older (<50% post-2010) | 3.57 |

> Source: [building age data](../outputs/summary_by_building_age.csv) · [chart](../outputs/chart_incident_types_by_age.png) · [analysis script](../04_analysis.py)

### 3. Trash and dumpster fires are the biggest volume driver in dense areas

Trash fires account for **46% of all fire incidents** citywide and are heavily concentrated in multifamily areas (30.6 per 1,000 units vs. 4.6 in single-family). These are low-severity but high-volume calls that consume response capacity.

> Source: [housing type data](../outputs/summary_by_housing_type.csv) · [incident type data](../outputs/summary_by_incident_type.csv)

### 4. The aerial equipment gap is the critical infrastructure concern

AFD operates **13 ladder trucks** regionwide — none added since the mid-1990s — at a ratio of 1 ladder per 3.8 engines (compared to Seattle's 1:2.7). Five-story single-stair buildings will require aerial access for rescue and fire attack above the third floor. Outer suburban areas already face a geographic coverage burden of **170 sq mi per station**.

> Source: [station coverage data](../outputs/station_coverage.csv) · [station map](../outputs/map_fire_stations.html)

### 5. Townhomes have very low fire rates, but local data cannot evaluate code changes

True individual townhomes (3,896 parcels, UNITS <= 1) had only **5 structure fires** over 3 years -- far too few to compare across code cohorts. TCAD's "TOWNHOMES" classification also includes 355 multi-unit condo complexes (built 1971-1985) that accounted for 14 of 19 total structure fires; these were identified and separated via property records verification.

| Segment | Parcels | Structure Fires (3yr) | Rate per 1,000 |
|---|---|---|---|
| True townhomes (UNITS <= 1) | 3,896 | 5 | 1.3 |
| Condo complexes mislabeled as townhomes | 355 | 14 | 39.4 |

Of the 5 true townhome fires: 1 at a 2017-built unit, 2 electrical fires at the same 2022-built unit, 1 at a 1981-built unit, and 1 at a 2014-built unit. No fires occurred at the 141 parcels in the 2019-2021 code cohort.

> Source: [townhome cohort data](../outputs/townhome_rates_by_cohort.csv) · [analysis script](../10_townhome_cohort_analysis.py) · [full summary](../outputs/townhome_cohort_summary.txt)

**What this means:** Austin's local data shows townhomes are very safe but cannot tell us whether sprinklers or fire separations are the reason. National NFIRS data is needed for meaningful code-effectiveness comparisons.

---

## Implications by Policy

### Single-Stair Expansion (5 stories, effective July 10, 2025)

| Factor | Assessment |
|---|---|
| **Fire risk from building type** | Low — causes are behavioral (cooking, smoking), not related to stairwell count |
| **Sprinkler protection** | Strong — new buildings require enhanced sprinklers; data shows 27-45% reduction in structure fires |
| **Aerial access** | Concern — 13 ladder trucks for the region; 28-36 month delivery times at ~$2M each |
| **Shelter-in-place reliance** | Moderate concern — residents above a fire must shelter rather than evacuate via second stairwell |

**Recommendation:** The fire risk of single-stair buildings is mitigated by sprinkler requirements, but the **aerial equipment shortfall** should be addressed proactively. Budget planning for additional ladder trucks should account for multi-year procurement timelines.

### HOME Initiative (increased density on SF lots)

| Factor | Assessment |
|---|---|
| **Shift in fire demand** | Expected — areas transitioning from SF to higher density will see increased call volume |
| **Cause profile shift** | Likely — cooking and smoking incidents will increase proportionally with unit count |
| **Current SF fire rates** | Low baseline — single-family-dominant areas average 1.3 structure fires per 1,000 units vs. 8.4 in multifamily-dominant |
| **New construction benefit** | Strong — new units will have sprinklers; older converted structures may not |

**Recommendation:** Scale **fire prevention education** (cooking safety, smoking policies) in neighborhoods experiencing HOME-driven densification. Monitor whether conversions of existing structures maintain sprinkler code compliance.

### Townhome Sprinkler Requirements

| Factor | Assessment |
|---|---|
| **Local fire data** | 5 structure fires in 3,896 true townhome parcels over 3 years -- too few for any cohort comparison |
| **Code evolution** | Progressive -- from 2hr walls only (pre-2019) to sprinklers required (post-2021) |
| **Townhome baseline rate** | Very low -- 1.3 structure fires per 1,000 true townhome parcels vs 8.0 for single-family parcels |
| **Data quality** | TCAD mislabels 355 condo complexes as "TOWNHOMES"; year-built manually verified via property records |

**Recommendation:** Local data demonstrates townhomes are low-risk but **cannot evaluate whether sprinklers or fire separations are more effective**. Supplement with **national NFIRS townhome fire data** for a sample large enough to draw conclusions.

---

## Structure Fires Are Rare Events

An important context for interpreting all findings in this brief: structure fires are low-probability events across all building types.

| Building Type | Annual Probability | Odds |
|---|---|---|
| Single Family | 0.27% | 1 in 371 homes/year |
| Townhome | 0.15% | 1 in 671 homes/year |
| Duplex | 0.62% | 1 in 162 parcels/year |
| Large Multifamily (100+) | 47.7% | 1 in 2 parcels/year* |

*\*Large MF parcels contain 100+ units each, so the per-unit rate is much lower.*

Nationally, NFPA reports ~360,000 residential structure fires per year across ~140 million occupied housing units -- about **1 in 389 homes per year** (0.26%). Austin's rates are broadly consistent with national averages.

**Why this matters for policy:** When the base rate is this low, meaningful comparisons between code cohorts require either very large populations or many years of observation. For Austin's 363 post-2021 townhome parcels, at the townhome base rate, you would expect ~0.5 structure fires per year. **Reaching 30 events (minimum for statistical analysis) would require approximately 55 years of data.** Austin currently has 3 years.

This is not a failure of the analysis -- it reflects the reality that fire codes are working. The question of *which* code approach works best (sprinklers vs. fire separations) requires national-scale data, not city-level incident counts.

> Source: [NFPA Fire Loss in the United States](https://www.nfpa.org/education-and-research/research/nfpa-research/fire-statistical-reports/fire-loss-in-the-united-states) · [townhome analysis](../outputs/townhome_cohort_summary.txt) · [analysis script](../10_townhome_cohort_analysis.py)

---

## What the Data Does Not Address

- **Townhome code cohort effectiveness** — with only 5 structure fires across 3,896 true townhome parcels in 3 years, local data cannot determine whether sprinklers or fire separations produce better outcomes. Would require ~55 years of data or national-scale analysis.
- **Historical trend** — AFD incident data for 2018-2021 was removed from the Austin Open Data Portal. Only 3 years (2022-2024) are available. A public records request could potentially recover 2018-2021 data.
- **Income as a confounding variable** — median income data has been collected but not yet integrated as a control variable. Low-income areas may independently correlate with higher fire rates. (Integration in progress on the `census_to_incidents` branch.)
- **Individual building-level analysis** — rates are calculated at the response-area and census-tract level, not per-building. We cannot isolate fire rates in single-stair buildings specifically (none exist yet at 5 stories).
- **Response time impacts** — this analysis covers incident rates and causes, not response time degradation from increased call volume.
- **NFIRS time period mismatch** — cause data is from 2018-2021; incident rate data is from 2022-2024.
- **TCAD classification accuracy** — TCAD's "TOWNHOMES" improvement type includes both individual townhome units and multi-unit condo complexes. Analysis must filter on UNITS field to distinguish them.

---

## Data Sources & Methodology

| Source | Period | Records |
|---|---|---|
| AFD Fire Incidents (Austin Open Data Portal) | 2022-2024 | 20,933 incidents |
| NFIRS Public Data Release (TX FDID WP801) | 2018-2021 | Austin structure fires |
| US Census ACS 5-Year Estimates | 2022 | Population, housing, building age |
| City of Austin ArcGIS | Current | 711 AFD response areas, zoning districts |
| TCAD Parcel Data (ArcGIS) | Current | 229,695 parcels with building type, year built |

Incident rates are calculated per 1,000 housing units using area-weighted census-to-response-area allocation. Structure fire classification follows NFPA/NFIRS standards: both **non-confined** fires (BOX alarm dispatches, NFIRS code 111) and **confined** fires (electrical and cooking dispatches, NFIRS codes 113-118) are counted as structure fires. AFD dispatch codes determine response level, not incident classification. Full methodology, data, and analysis code are available in the [project repository](../README.md).

> Analysis scripts: [data pipeline](../01_download_data.py) · [crosswalk](../03_create_crosswalk.py) · [analysis](../04_analysis.py) · [NFIRS analysis](../06_nfirs_cause_analysis.py) · [townhome analysis](../10_townhome_cohort_analysis.py) · [full report](../outputs/REPORT_Austin_Fire_Analysis.md)

### National Studies Referenced

- Pew Charitable Trusts, "[Modern Multifamily Buildings Provide the Most Fire Protection](https://www.pew.org/en/research-and-analysis/issue-briefs/2025/09/modern-multifamily-buildings-provide-the-most-fire-protection)" (2025) — post-2000 multifamily fire death rate is 1.2 per million vs 7.6 for single-family
- Pew Charitable Trusts, "[Small Single-Stairway Apartment Buildings Have Strong Safety Record](https://www.pew.org/en/research-and-analysis/reports/2025/02/small-single-stairway-apartment-buildings-have-strong-safety-record)" (2025)
- NFPA, "[U.S. Experience with Sprinklers](https://www.nfpa.org/education-and-research/research/nfpa-research/fire-statistical-reports/us-experience-with-sprinklers)" (2024) — sprinklers reduce civilian death rate by 90%
- USFA, "[Multifamily Residential Building Fires (2017-2019)](https://www.usfa.fema.gov/downloads/pdf/statistics/v21i7.pdf)"
- USFA, "[One- and Two-Family Residential Building Fires (2017-2019)](https://www.usfa.fema.gov/downloads/pdf/statistics/v21i6.pdf)"
