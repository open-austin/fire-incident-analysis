# Austin Fire Resource Allocation Analysis

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

## Data Setup

**Data files are not included in this repository** due to size (~4.7GB). You must download them before running the analysis.

### Automatic Download (Recommended)

```bash
# Install dependencies first
pip install -r requirements.txt

# Download all required data (~100MB from APIs)
python 01_download_data.py
```

This downloads Austin fire incidents, response area boundaries, and Census data from public APIs.

### NFIRS Data (Optional - for national comparisons)

The NFIRS (National Fire Incident Reporting System) data must be downloaded manually:

1. Visit the [USFA NFIRS Data Center](https://www.usfa.fema.gov/nfirs/data/)
2. Download the annual Public Data Release files (2018-2021)
3. Extract to `raw_data/nfirs/YYYY/` directories

### Note on Historical Data

The AFD Fire Incidents 2018-2021 dataset was removed from the Austin Open Data Portal
and is no longer available for automatic download. This analysis uses 2022-2024 data only.

For historical data, you can file a public records request with the Austin Fire Department.

### Directory Structure After Setup

```
raw_data/
├── afd_incidents_2022_2024.csv    # From download script
├── afd_response_areas.geojson     # From download script
├── zoning.geojson                 # From download script (Austin zoning districts)
├── fire_stations.geojson          # From download script
├── census_population.csv          # From download script
├── census_housing.csv             # From download script
├── census_year_built.csv          # From download script
├── tl_2023_48_tract.zip           # From download script (Census tract boundaries)
└── nfirs/                         # Manual download (optional)
    └── ...
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Download data (see Data Setup above)
python 01_download_data.py

# Run the pipeline
python 02_clean_incidents.py  # Clean incident data
python 03_create_crosswalk.py # Create spatial crosswalk
python 04_analysis.py         # Run analysis
python 05_visualize.py        # Generate maps & charts
```

## Project Structure

```
fire-incident-analysis/
├── 01_download_data.py          # Fetch data from APIs
├── 02_clean_incidents.py        # Clean & classify incidents
├── 03_create_crosswalk.py       # Census tract → response area mapping
├── 04_analysis.py               # Calculate rates & run tests
├── 05_visualize.py              # Generate maps & charts
├── 06_nfirs_cause_analysis.py   # NFIRS cause code analysis
├── raw_data/                    # Downloaded data (not in repo)
├── processed_data/              # Cleaned/merged data (not in repo)
├── outputs/                     # Final results & visualizations (not in repo)
├── docs/                        # Documentation
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Data Sources

| Data | Source |
|------|--------|
| Fire Incidents (2022-2024) | [Austin Open Data Portal](https://data.austintexas.gov/Public-Safety/AFD-Fire-Incidents-2022-2024/v5hh-nyr8) |
| Response Area Boundaries | [City of Austin ArcGIS](https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/BOUNDARIES_afd_response_areas/FeatureServer) |
| Fire Station Locations | [City of Austin ArcGIS](https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/LOCATION_fire_stations/FeatureServer) |
| Population by Tract | [Census ACS 5-Year (B01003)](https://api.census.gov/data/2022/acs/acs5) |
| Housing Units by Type | [Census ACS 5-Year (B25024)](https://api.census.gov/data/2022/acs/acs5) |
| Year Structure Built | [Census ACS 5-Year (B25034)](https://api.census.gov/data/2022/acs/acs5) |
| Zoning Districts | [City of Austin ArcGIS](https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/Current_Zoning_gdb/FeatureServer) |
| Census Tract Boundaries | [TIGER/Line Shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) |
| NFIRS Structure Fires | [USFA NFIRS Data Center](https://www.usfa.fema.gov/nfirs/data/) (manual download) |

## Key Outputs

- `outputs/summary_by_urban_class.csv` - Incident rates by urban/suburban classification
- `outputs/summary_by_housing_type.csv` - Incident rates by housing typology
- `outputs/statistical_tests.txt` - T-tests and ANOVA results
- `outputs/map_incidents_per_capita.html` - Interactive choropleth map
- `outputs/chart_urban_comparison.png` - Bar chart comparison
- `outputs/building_height_analysis.csv` - Fire incidents by building height (NFIRS)
- `outputs/chart_building_height.png` - Building height analysis charts

## Response Area Demographics Data Dictionary

`processed_data/response_area_demographics.csv` contains per-response-area demographics with the following columns:

### Census-derived (area-weighted from tract-level ACS data)

| Column | Description |
|--------|-------------|
| `response_area_id` | AFD response area identifier |
| `population` | Estimated population |
| `total_units` | Total housing units |
| `single_family` | Detached + attached single-family units |
| `duplex` | 2-unit buildings |
| `small_multifamily` | 3-19 unit buildings |
| `large_multifamily` | 20+ unit buildings |
| `multifamily` | All multifamily combined |
| `mobile_other` | Mobile homes and other |
| `yb_total` | Units with known year built |
| `built_2010_plus` | Units built 2010 or later |
| `built_1970_2009` | Units built 1970-2009 |
| `built_pre_1970` | Units built before 1970 |
| `pct_*` | Percentage versions of the above counts |

### Zoning-derived (area-weighted from Austin zoning districts)

| Column | Description |
|--------|-------------|
| `avg_max_stories` | Area-weighted average max stories allowed by zoning |
| `avg_max_height_ft` | Area-weighted average max building height (ft) allowed by zoning |
| `dominant_zone` | Most common zoning code by area (e.g. SF-3, CS, MF-4) |
| `pct_tall_zoning` | % of area zoned for 4+ stories |

**Zoning coverage:** 508 of 711 response areas (71%). The 203 areas without zoning data are in Austin's ETJ (see glossary below) where city zoning does not apply.

**Zoning-to-height mapping:** Each Austin `BASE_ZONE` code is mapped to a max height (ft) and estimated max stories based on Austin's Land Development Code. The mapping is defined in `ZONING_HEIGHT_MAP` in `03_create_crosswalk.py`. Vertical mixed-use overlays (`-V` suffix) are detected and bump the minimum to 6 stories.

**Validation:** Higher multifamily % correlates with higher zoning-permitted stories (r=positive), confirming the spatial join is working correctly. CBD zones show the highest avg stories (~21), SF zones the lowest (~2-3).

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

## Research Context

This analysis supports the Research Hub's investigation into how Austin's fire coverage must adapt to new development patterns, informed by:
- **Single-stair building code** (5-story single-staircase buildings, effective July 2025)
- **HOME initiative** (Phases 1 & 2, allowing 3+ units on SF lots and 1,800 sq ft minimum lots)
- AFD aerial ladder apparatus shortages (13 trucks regionwide, none added since mid-1990s)
- NFPA Standard 1710 response time objectives
- Pew Research report on multifamily building safety
- Austin zoning and budget constraints

### Key Policy References

| Policy | Ordinance | Effective |
|--------|-----------|-----------|
| HOME Phase 1 | 20231207-001 | Feb 5, 2024 |
| HOME Phase 2 | 20240516-006 | Aug-Nov 2024 |
| Single-Stair Expansion (5 stories) | April 10, 2025 vote | July 10, 2025 |
| Site Plan Lite Phase 2 & Infill Plat | March 6, 2025 | June 16, 2025 |

## Contact

Research Hub - Austin Housing & Land Use Working Group
