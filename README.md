# Austin Fire Resource Allocation Analysis

Analyzes fire incident patterns across Austin Fire Department's 711 response areas by housing typology, urban classification, building age, and zoning. Uses AFD incident data (2022-2024), Census demographics, NFIRS cause codes, and Austin zoning districts.

For policy background (single-stair building code, HOME initiative) and glossary, see [docs/RESEARCH_CONTEXT.md](docs/RESEARCH_CONTEXT.md).

## Quick Start

```bash
# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download data (~100MB from public APIs)
python incident_pipeline/01_download_data.py

# Run the pipeline (from the repo root)
python incident_pipeline/02_clean_incidents.py    # Clean & classify incidents
python incident_pipeline/03_create_crosswalk.py   # Census tract → response area mapping + zoning
python incident_pipeline/04_analysis.py           # Calculate rates & statistical tests
python incident_pipeline/05_visualize.py          # Generate maps & charts

# Or run everything in one go
python incident_pipeline/run_all.py

# Optional: NFIRS cause analysis (requires manual data download)
python incident_pipeline/06_nfirs_cause_analysis.py
```

## Fire-Fiscal Report

A second analysis line — the fiscal-productivity / fire-fiscal report — asks whether each area of the Austin metro generates enough tax revenue to pay for the infrastructure and fire service it consumes. Its pipeline lives in `report_pipeline/` (TCAD roll parsing → metro parcel build → report figures → PDF), with the three models in `notebooks/` (`value_per_acre_metro.ipynb`, `fiscal_productivity.ipynb`, `fire_use_vs_pays.ipynb`) and a 24-check validation gate (`notebooks/validation.ipynb` → `outputs/validation_report.csv`).

The master report is [docs/FIRE_FISCAL_FULL_REPORT.md](docs/FIRE_FISCAL_FULL_REPORT.md) (rendered to `outputs/FIRE_FISCAL_FULL_REPORT.pdf` by `report_pipeline/14_build_report_pdf.py`); see its §13 runbook for the full rebuild order.

## Data Setup

**Data files are not included in this repository** due to size. Run `incident_pipeline/01_download_data.py` to fetch them from public APIs.

### Automatic Download

`incident_pipeline/01_download_data.py` downloads:
- AFD fire incidents (2022-2024) from Austin Open Data Portal
- AFD response area boundaries from ArcGIS FeatureServer
- Fire station locations from ArcGIS FeatureServer
- Austin zoning districts from ArcGIS FeatureServer (~22k polygons, paginated)
- Census population (B01003), housing units (B25024), year built (B25034)
- Census tract boundaries (TIGER/Line 2023)

### NFIRS Data (optional)

The NFIRS cause analysis (`incident_pipeline/06_nfirs_cause_analysis.py`) requires a manual download:

1. Visit the [USFA NFIRS Data Center](https://www.usfa.fema.gov/nfirs/data/)
2. Download the annual Public Data Release files (2018-2021)
3. Extract to `raw_data/nfirs/YYYY/` directories

### Note on Historical Data

The AFD Fire Incidents 2018-2021 dataset was removed from the Austin Open Data Portal. This analysis uses 2022-2024 data only. For historical data, file a public records request with AFD.

### Directory Structure

```
raw_data/
├── afd_incidents_2022_2024.csv    # AFD incidents
├── afd_response_areas.geojson     # 711 response area boundaries
├── zoning.geojson                 # Austin zoning districts
├── fire_stations.geojson          # Station locations
├── census_population.csv          # B01003
├── census_housing.csv             # B25024
├── census_year_built.csv          # B25034
├── tl_2023_48_tract.zip           # TIGER/Line tract boundaries
└── nfirs/                         # Manual download (optional)
    └── YYYY/
        ├── basicincident.txt
        ├── fireincident.txt
        └── structurefire.txt
```

## Pipeline Scripts

| Script | Input | Output | Description |
|--------|-------|--------|-------------|
| `incident_pipeline/01_download_data.py` | Public APIs | `raw_data/*` | Fetches all data; handles ArcGIS pagination for large datasets |
| `incident_pipeline/02_clean_incidents.py` | `raw_data/afd_incidents_2022_2024.csv` | `processed_data/incidents_clean.csv` | Parses dates, classifies incident types (structure, vehicle, outdoor, trash) |
| `incident_pipeline/03_create_crosswalk.py` | `raw_data/*` | `processed_data/tract_to_response_area_crosswalk.csv`, `response_area_demographics.csv`, `response_areas_with_demographics.geojson` | Area-weighted census allocation + zoning height mapping |
| `incident_pipeline/04_analysis.py` | `processed_data/*` | `outputs/summary_*.csv`, `outputs/statistical_tests.txt` | Per-capita rates, t-tests, ANOVA, correlations |
| `incident_pipeline/05_visualize.py` | `processed_data/*` | `outputs/map_*.html`, `outputs/chart_*.png` | Interactive Folium maps + matplotlib charts |
| `incident_pipeline/06_nfirs_cause_analysis.py` | `raw_data/nfirs/*` | `outputs/cause_*.csv`, `outputs/chart_cause_*.png` | Cause/heat source/origin analysis by housing type |

## Data Sources

| Data | Source |
|------|--------|
| Fire Incidents (2022-2024) | [Austin Open Data Portal](https://data.austintexas.gov/Public-Safety/AFD-Fire-Incidents-2022-2024/v5hh-nyr8) |
| Response Area Boundaries | [City of Austin ArcGIS](https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/BOUNDARIES_afd_response_areas/FeatureServer) |
| Fire Station Locations | [City of Austin ArcGIS](https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/LOCATION_fire_stations/FeatureServer) |
| Zoning Districts | [City of Austin ArcGIS](https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/Current_Zoning_gdb/FeatureServer) |
| Population by Tract | [Census ACS 5-Year (B01003)](https://api.census.gov/data/2022/acs/acs5) |
| Housing Units by Type | [Census ACS 5-Year (B25024)](https://api.census.gov/data/2022/acs/acs5) |
| Year Structure Built | [Census ACS 5-Year (B25034)](https://api.census.gov/data/2022/acs/acs5) |
| Census Tract Boundaries | [TIGER/Line Shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) |
| NFIRS Structure Fires | [USFA NFIRS Data Center](https://www.usfa.fema.gov/nfirs/data/) (manual download) |

## Key Outputs

### Summary Data
- `outputs/summary_by_urban_class.csv` - Incident rates by urban/suburban classification
- `outputs/summary_by_housing_type.csv` - Incident rates by housing typology
- `outputs/summary_by_building_age.csv` - Incident rates by building age
- `outputs/summary_by_incident_type.csv` - Incident counts by category
- `outputs/statistical_tests.txt` - T-tests and ANOVA results
- `outputs/station_coverage.csv` - Fire station coverage by urban class

### NFIRS Cause Analysis
- `outputs/cause_by_housing_type.csv` - Cause of ignition by housing type
- `outputs/heat_source_by_housing.csv` - Heat source breakdown by housing type
- `outputs/area_origin_by_housing.csv` - Area of origin by housing type
- `outputs/sprinkler_by_housing.csv` - Sprinkler presence by housing type

### Visualizations
- `outputs/map_incidents_per_capita.html` - Incident rates choropleth
- `outputs/map_building_age.html` - Building age distribution
- `outputs/map_fire_stations.html` - Fire station locations
- `outputs/map_housing_typology.html` - Housing type distribution
- `outputs/map_urban_classification.html` - Urban/suburban classification
- `outputs/chart_urban_comparison.png` - Incident rates by urban class
- `outputs/chart_cause_comparison.png` - NFIRS cause comparison (MF vs SF)
- `outputs/chart_heat_source_comparison.png` - Heat source comparison
- `outputs/REPORT_Austin_Fire_Analysis.md` - Full analysis report

## Response Area Demographics Data Dictionary

`processed_data/response_area_demographics.csv` — per-response-area demographics (711 rows).

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

**Zoning coverage:** 508 of 711 response areas (71%). The 203 areas without zoning data are in Austin's ETJ where city zoning does not apply.

**Zoning-to-height mapping:** Each Austin `BASE_ZONE` code is mapped to a max height (ft) and estimated max stories based on the Land Development Code. The mapping is defined in `ZONING_HEIGHT_MAP` in `incident_pipeline/03_create_crosswalk.py`. Vertical mixed-use overlays (`-V` suffix) bump the minimum to 6 stories.

**Validation:** Higher multifamily % correlates with higher zoning-permitted stories (r=positive). CBD zones show highest avg stories (~21), SF zones lowest (~2-3).

### Census-estimated height (fallback for ETJ areas)

| Column | Description |
|--------|-------------|
| `census_est_stories` | Weighted average stories inferred from B25024 housing type mix |
| `height_data_source` | `'zoning'`, `'census_estimate'`, or `'none'` |
| `height_category` | `'low_rise'` (<=2.5), `'mid_rise'` (2.5-5), `'high_rise'` (>5) |
| `density_category` | `'low_density'` (<20% MF), `'medium_density'` (20-50%), `'high_density'` (>50%) |

## Project Structure

```
fire-incident-analysis/
├── incident_pipeline/           # Original AFD incident/housing analysis (run from repo root)
│   ├── 01_download_data.py      # Fetch data from APIs
│   ├── 02_clean_incidents.py    # Clean & classify incidents
│   ├── 03_create_crosswalk.py   # Census → response area mapping + zoning
│   ├── 04_analysis.py           # Calculate rates & run tests
│   ├── 05_visualize.py          # Generate maps & charts
│   ├── 06_nfirs_cause_analysis.py  # NFIRS cause code & building height analysis
│   ├── census_variables.py      # Shared Census variable definitions
│   ├── quick_start.py           # Convenience script
│   └── run_all.py               # Run full pipeline
├── report_pipeline/             # Fiscal-productivity / fire-fiscal report pipeline
│   ├── 12_parse_tcad_roll.py    # Parse TCAD certified appraisal roll
│   ├── 13_build_metro_parcels.py   # Build metro parcel set (Travis+Williamson+Hays)
│   ├── 14_build_report_pdf.py   # Render the master report to PDF
│   ├── 15_build_report_figures.py  # Report figures & diagrams
│   ├── v2_county_sources.py     # County data source registry (PVS ratios, citations)
│   ├── v2_fetch_parcels.py      # Fetch Williamson/Hays parcels from CAD servers
│   └── viz_palette.py           # Shared Austin civic color palette
├── notebooks/                   # Analysis notebooks
│   ├── fiscal_productivity.ipynb   # Fiscal break-even models (A: land, B: road-miles)
│   ├── fire_use_vs_pays.ipynb   # Fire service use vs. pays-in by response area
│   ├── validation.ipynb         # 24-check validation gate → outputs/validation_report.csv
│   ├── interactive_map.ipynb    # Interactive 3D fire-fiscal map
│   ├── value_per_acre_metro.ipynb  # Metro value-per-acre surface
│   └── *.ipynb                  # Older EDA notebooks
├── legacy/                      # Orphaned scripts kept for reference (parcel join,
│                                #   census-tract analysis, townhome cohort analysis)
├── raw_data/                    # Downloaded data (gitignored)
├── processed_data/              # Cleaned/merged data (gitignored)
├── outputs/                     # Results & visualizations (gitignored)
├── docs/                        # Research context, reports, design docs
│   ├── FIRE_FISCAL_FULL_REPORT.md  # Fire-fiscal master report
│   ├── RESEARCH_CONTEXT.md      # Policy background, glossary
│   └── plans/                   # Analysis design documents
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```
