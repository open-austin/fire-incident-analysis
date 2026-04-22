# Policy Brief: Fire Coverage Impacts of Single-Stair and HOME Development Patterns

**Prepared for:** Timothy Bray, Policy Analyst, District 4
**Prepared by:** Austin Housing & Land Use Working Group Research Hub
**Date:** April 2026

---

## Summary

Austin's single-stair building code expansion (effective July 2025) and HOME initiative are reshaping the city's housing landscape. This brief summarizes what fire incident data tells us about how these changes will affect fire coverage demands — and what the data suggests policymakers should prioritize.

**Bottom line:** Higher-density housing does increase fire call volume, but the drivers are behavioral (cooking, smoking), not architectural. New construction benefits from Austin's 2006 sprinkler code, which has cut structure fire rates by 141%. The primary infrastructure gap is aerial equipment, not station coverage.

---

## Key Findings

### 1. Density increases fire call volume — but the causes are preventable

Multifamily-dominant areas experience **4-6x higher fire incident rates** than single-family areas across all incident types. However, NFIRS cause data shows this gap is driven by **unintentional factors**:

- **76% of multifamily fires are unintentional** vs. 64% in single-family ([cause data](../outputs/cause_by_housing_type.csv))
- **Cooking** is the top heat source in both housing types (~24%), but **kitchen fires** account for 32% of multifamily origins vs. 20% in single-family ([area of origin data](../outputs/area_origin_by_housing.csv))
- **Smoking** is 4x more common as a heat source in multifamily (18% vs. 5%) ([heat source data](../outputs/heat_source_by_housing.csv))
- **Arson is not driving the gap** — intentional fires are actually lower in multifamily (6%) than single-family (10%)

> Source: [NFIRS cause analysis](../06_nfirs_cause_analysis.py) · [cause comparison chart](../outputs/chart_cause_comparison.png)

### 2. Austin's sprinkler code is working — new construction is significantly safer

Areas with newer building stock (50%+ built after 2010, subject to the 2006 sprinkler code) have **141% lower structure fire rates** than areas with older buildings. Vehicle and outdoor fires — which aren't affected by building codes — show minimal difference, confirming the sprinkler code as the key factor.

| Building Stock | Structure Fires per 1,000 Units |
|---|---|
| Newer (50%+ post-2010) | 2.3 |
| Older (<50% post-2010) | 5.6 |

> Source: [building age data](../outputs/summary_by_building_age.csv) · [chart](../outputs/chart_incident_types_by_age.png) · [analysis script](../04_analysis.py)

### 3. Trash and dumpster fires are the biggest volume driver in dense areas

Trash fires account for **46% of all fire incidents** citywide and are heavily concentrated in multifamily areas (30.6 per 1,000 units vs. 4.6 in single-family). These are low-severity but high-volume calls that consume response capacity.

> Source: [housing type data](../outputs/summary_by_housing_type.csv) · [incident type data](../outputs/summary_by_incident_type.csv)

### 4. The aerial equipment gap is the critical infrastructure concern

AFD operates **13 ladder trucks** regionwide — none added since the mid-1990s — at a ratio of 1 ladder per 3.8 engines (compared to Seattle's 1:2.7). Five-story single-stair buildings will require aerial access for rescue and fire attack above the third floor. Outer suburban areas already face a geographic coverage burden of **170 sq mi per station**.

> Source: [station coverage data](../outputs/station_coverage.csv) · [station map](../outputs/map_fire_stations.html)

---

## Implications by Policy

### Single-Stair Expansion (5 stories, effective July 10, 2025)

| Factor | Assessment |
|---|---|
| **Fire risk from building type** | Low — causes are behavioral (cooking, smoking), not related to stairwell count |
| **Sprinkler protection** | Strong — new buildings require enhanced sprinklers; data shows 141% reduction in structure fires |
| **Aerial access** | Concern — 13 ladder trucks for the region; 28-36 month delivery times at ~$2M each |
| **Shelter-in-place reliance** | Moderate concern — residents above a fire must shelter rather than evacuate via second stairwell |

**Recommendation:** The fire risk of single-stair buildings is mitigated by sprinkler requirements, but the **aerial equipment shortfall** should be addressed proactively. Budget planning for additional ladder trucks should account for multi-year procurement timelines.

### HOME Initiative (increased density on SF lots)

| Factor | Assessment |
|---|---|
| **Shift in fire demand** | Expected — areas transitioning from SF to higher density will see increased call volume |
| **Cause profile shift** | Likely — cooking and smoking incidents will increase proportionally with unit count |
| **Current SF fire rates** | Low baseline — single-family areas average 2.0 structure fires per 1,000 units vs. 8.8 in multifamily |
| **New construction benefit** | Strong — new units will have sprinklers; older converted structures may not |

**Recommendation:** Scale **fire prevention education** (cooking safety, smoking policies) in neighborhoods experiencing HOME-driven densification. Monitor whether conversions of existing structures maintain sprinkler code compliance.

---

## What the Data Does Not Address

- **Income as a confounding variable** — median income data has been collected but not yet integrated as a control variable. Low-income areas may independently correlate with higher fire rates. (Integration in progress on the `census_to_incidents` branch.)
- **Individual building-level analysis** — rates are calculated at the response-area and census-tract level, not per-building. We cannot isolate fire rates in single-stair buildings specifically (none exist yet at 5 stories).
- **Response time impacts** — this analysis covers incident rates and causes, not response time degradation from increased call volume.
- **NFIRS time period mismatch** — cause data is from 2018-2021; incident rate data is from 2022-2024.

---

## Data Sources & Methodology

| Source | Period | Records |
|---|---|---|
| AFD Fire Incidents (Austin Open Data Portal) | 2022-2024 | 20,933 incidents |
| NFIRS Public Data Release (TX FDID WP801) | 2018-2021 | Austin structure fires |
| US Census ACS 5-Year Estimates | 2022 | Population, housing, building age |
| City of Austin ArcGIS | Current | 711 AFD response areas, zoning districts |

Incident rates are calculated per 1,000 housing units using area-weighted census-to-response-area allocation. Full methodology, data, and analysis code are available in the [project repository](../README.md).

> Analysis scripts: [data pipeline](../01_download_data.py) · [crosswalk](../03_create_crosswalk.py) · [analysis](../04_analysis.py) · [NFIRS analysis](../06_nfirs_cause_analysis.py) · [full report](../outputs/REPORT_Austin_Fire_Analysis.md)
