# Austin Fire Resource Allocation Analysis

**Research Question:** Do suburban areas in Austin utilize disproportionate fire department resources on a per-capita basis compared to urban areas?

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
| Census Tract Boundaries | [TIGER/Line Shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) |

## Key Outputs

- `outputs/summary_by_urban_class.csv` - Incident rates by urban/suburban classification
- `outputs/summary_by_housing_type.csv` - Incident rates by housing typology
- `outputs/statistical_tests.txt` - T-tests and ANOVA results
- `outputs/map_incidents_per_capita.html` - Interactive choropleth map
- `outputs/chart_urban_comparison.png` - Bar chart comparison

## Research Context

This analysis supports the Research Hub's investigation into fire department resource allocation, informed by:
- Single-stair building code discussions
- Fire department aerial equipment requirements
- Pew Research report on multifamily building safety
- Austin budget and zoning debates

## Contact

Research Hub - Austin Housing & Land Use Working Group
