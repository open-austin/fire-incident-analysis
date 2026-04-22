# Research Context

**Research Question:** How can Austin expect fire coverage demands to change as the city's single-stair building code and HOME initiative drive new development patterns — particularly taller single-staircase residential buildings and increased housing density in formerly single-family neighborhoods?

**Stakeholder:** District 4 Policy Analyst Timothy Bray

## Policy Background

### Single-Stair Building Code

Austin's single-stair policy allows multi-family residential buildings to be constructed with only one central staircase instead of the two traditionally required by U.S. building codes. This building typology — common throughout Europe and Asia — enables apartments with windows on two sides, construction on smaller lots, and more family-sized units.

**Timeline:**
- **2021:** Austin removed its local prohibition on single-stair buildings, aligning with the IBC allowance for buildings up to 3 stories. The first project permitted was the Ashram Multifamily complex (6 units on a 4,400 sq ft lot).
- **May 2024:** Council unanimously directed staff to draft amendments expanding single-stair to 6 stories.
- **June 2024:** Fire Chief Joel Baker and EMS Chief Robert Luckritz issued a memo recommending against the expansion, citing "significant potential safety risks to occupants and first responders."
- **April 10, 2025:** Council approved expansion to **5 stories** (10-1 vote, championed by CM Chito Vela). Effective July 10, 2025.

**Approved specifications:** Max 5 stories, max 4 units per floor (~20 total), enhanced sprinkler systems, protected/enclosed stairwell, separate enclosure between apartments and stairway.

**Fire safety concerns:** AFD has only **13 ladder trucks** regionwide and has not added a new aerial apparatus since the mid-1990s (ratio of 1 ladder per 3.8 engines vs. Seattle's 1:2.7). In single-stair buildings, residents above a fire must shelter in place rather than evacuate via an alternate stairwell, and the single stairwell used for fire attack is exposed to heat and combustion products. NFPA Standard 1710 sets an 8-minute response objective; budget staff estimated new ladder trucks by FY2026-27, but manufacturers quote 28-36 month delivery times at ~$2M per truck.

### HOME Initiative (Home Options for Mobility and Equity)

The HOME initiative is a series of Land Development Code amendments expanding housing options in single-family zoned areas — one of the most significant zoning reforms in Austin's history.

**HOME Phase 1** (Ordinance 20231207-001, effective Feb 5, 2024):
- Allows up to **3 housing units** (including tiny homes) on any SF-1, SF-2, or SF-3 lot
- Max building coverage 40%, max impervious cover 45%
- Subchapter F 32-ft height limit applies only to single-family use, not duplexes/triplexes

**HOME Phase 2** (Ordinance 20240516-006, effective Aug-Nov 2024):
- Reduces minimum lot size from **5,750 sq ft to 1,800 sq ft** in SF districts
- Potentially allows 4-5 homes per original lot
- Each unit must have at least 1,650 sq ft of lot area

**Results:** From 2015-2024, Austin added 120,000 housing units (30% increase, 3x the national rate). Austin experienced the steepest rent declines of any large U.S. city from 2021-2026.

### Combined Impact on Fire Coverage

Both policies increase housing density and building complexity across Austin. Single-stair allows taller buildings (up to 5 stories) with a single means of egress in areas that may lack adequate ladder truck coverage. HOME increases the number of residential structures in neighborhoods previously limited to single-family homes. Together, they intensify demands on fire response infrastructure that AFD leadership has described as already insufficient. This analysis uses zoning data and fire incident history to quantify these impacts.

## Key Policy References

| Policy | Ordinance | Effective |
|--------|-----------|-----------|
| HOME Phase 1 | 20231207-001 | Feb 5, 2024 |
| HOME Phase 2 | 20240516-006 | Aug-Nov 2024 |
| Single-Stair Expansion (5 stories) | April 10, 2025 vote | July 10, 2025 |
| Site Plan Lite Phase 2 & Infill Plat | March 6, 2025 | June 16, 2025 |

## Glossary

| Term | Definition |
|------|-----------|
| **AFD** | Austin Fire Department |
| **Response area** | Geographic zone assigned to a fire station; the area a specific unit is first-due to respond to |
| **ETJ** | Extraterritorial Jurisdiction — area outside Austin city limits where AFD responds but the city does not apply zoning regulations |
| **ACS** | American Community Survey — Census Bureau survey that provides annual demographic estimates (this project uses the 5-year estimates) |
| **Census tract** | Small geographic area defined by the Census Bureau, typically 1,200-8,000 people; the smallest unit at which ACS housing data is available |
| **Area-weighted allocation** | Method used to distribute census data to response areas: if 40% of a census tract's area falls within a response area, 40% of that tract's population and housing are allocated to it |
| **NFIRS** | National Fire Incident Reporting System — national database of fire incidents maintained by USFA; contains per-incident building characteristics like number of stories |
| **USFA** | United States Fire Administration |
| **TIGER/Line** | Topologically Integrated Geographic Encoding and Referencing — Census Bureau shapefiles that provide geographic boundaries for census areas |
| **Urban core** | Response areas with population density >= 10,000 persons/sq mi |
| **Inner suburban** | Response areas with population density 3,000-10,000 persons/sq mi |
| **Outer suburban** | Response areas with population density < 3,000 persons/sq mi |
| **Single-stair building** | Multi-family residential building with one central staircase instead of the two traditionally required; allowed up to 5 stories in Austin as of July 2025 |
| **HOME initiative** | Home Options for Mobility and Equity — Land Development Code amendments allowing increased housing density on single-family lots |
| **WUI** | Wildland-Urban Interface — areas where development meets undeveloped wildland, subject to additional fire-hardening requirements; over half of Austin falls in a WUI zone |
| **IBC** | International Building Code — model building code adopted (with local amendments) by Austin and most U.S. jurisdictions |
| **NFPA 1710** | National Fire Protection Association standard for fire department response times; sets an 8-minute response objective |
| **BASE_ZONE** | The underlying Austin zoning district code (e.g. SF-3, MF-4, CS) without overlays |
| **Combining districts** | Zoning overlays appended to the base zone: `-NP` (Neighborhood Plan), `-MU` (Mixed Use), `-CO` (Conditional Overlay), `-V` (Vertical Mixed Use) |
| **Dominant zone** | The zoning district that covers the largest area within a response area |
| **pct_tall_zoning** | Percentage of a response area's land zoned for buildings of 4+ stories (mid-rise and above) |

### Austin Zoning Code Quick Reference

| Code(s) | Category | Max Height | Est. Stories |
|----------|----------|-----------|-------------|
| SF-1 through SF-6 | Single-family residential | 35 ft | 2-3 |
| MF-1, MF-2 | Small multifamily | 35 ft | 3 |
| MF-3, MF-4 | Mid multifamily | 40-50 ft | 4-5 |
| MF-5, MF-6 | Large multifamily | 60 ft | 6 |
| LO, LR, NO, CS-1 | Limited commercial/office | 40 ft | 3 |
| GR, CR, CS, GO, CH | General commercial/office | 60 ft | 5 |
| DMU | Downtown mixed use | 120 ft | 12 |
| CBD | Central business district | Unlimited | 40+ |
| `-V` overlay | Vertical mixed use | Varies | 6 min |

## Contact

Research Hub - Austin Housing & Land Use Working Group
