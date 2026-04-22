# Update Log

## 2026-03-31 — Building Height & Density Analysis

**Branch:** `feature/building-height-data`

### Changes to `01_download_data.py`
- Added `download_arcgis_paginated()` function to handle ArcGIS FeatureServer endpoints that cap responses at 2,000 records
- Added **Austin Zoning Districts** as a new download step (~22k polygons, ~71 MB)
  - Source: City of Austin ArcGIS `Current_Zoning_gdb` FeatureServer
  - Output: `raw_data/zoning.geojson`
- Added fire station location download step
  - Source: City of Austin ArcGIS `LOCATION_fire_stations` FeatureServer
  - Output: `raw_data/fire_stations.geojson`

### Changes to `03_create_crosswalk.py`
- **Zoning-to-height mapping** (`ZONING_HEIGHT_MAP`): 44 Austin `BASE_ZONE` codes mapped to `(max_height_ft, max_stories)` based on the Land Development Code. Vertical mixed-use overlays (`-V` suffix) detected and bumped to a minimum of 6 stories.
- **`load_zoning()`**: Loads zoning GeoJSON, maps each polygon to its height/stories estimate, detects `-V` and `-MU` overlays.
- **`allocate_zoning_to_response_areas()`**: Area-weighted spatial allocation of zoning characteristics to response areas. Produces 4 columns:
  - `avg_max_stories` — area-weighted average max stories permitted
  - `avg_max_height_ft` — area-weighted average max building height (ft)
  - `dominant_zone` — most common zoning code by area
  - `pct_tall_zoning` — % of area zoned for 4+ stories
- **`estimate_height_from_census()`**: Census housing mix (B25024) fallback for ETJ areas without zoning coverage. Produces 4 columns:
  - `census_est_stories` — weighted average stories inferred from housing type mix (always computed for all areas)
  - `height_data_source` — `'zoning'`, `'census_estimate'`, or `'none'`
  - `height_category` — `'low_rise'` (≤2.5 stories), `'mid_rise'` (2.5–5), `'high_rise'` (>5)
  - `density_category` — `'low_density'` (<20% MF), `'medium_density'` (20–50%), `'high_density'` (>50%)
- **Coverage:** 508/711 response areas have zoning data; 203 ETJ areas use census-based estimates (flagged via `height_data_source`)

### Changes to `06_nfirs_cause_analysis.py`
- Added `structurefire.txt` loading alongside existing `fireincident.txt` and `basicincident.txt`
- Extracts per-incident building characteristics: `STRUC_TYPE`, `STRUC_STAT`, `BLDG_ABOVE`, `BLDG_BELOW`, `BLDG_LGTH`, `BLDG_WDTH`, `TOT_SQ_FT`, `FIRE_ORIG`
- **`analyze_building_height()`**: Categorizes fires by building height (1–2, 3–4, 5–7, 8+ stories), cross-tabs with fire spread, cause, sprinklers, property loss
- **`create_building_height_chart()`**: Two-panel chart (incident counts + fire spread by height)
- New outputs: `outputs/building_height_analysis.csv`, `outputs/chart_building_height.png`

### Changes to `README.md`
- Added data dictionary for `response_area_demographics.csv` (all 30 columns)
- Added glossary of terms (ETJ, ACS, NFIRS, urban_core, WUI, IBC, NFPA 1710, etc.)
- Added Austin zoning code quick reference table
- Added policy background: single-stair building code timeline, HOME initiative phases, combined fire coverage impact
- Added stakeholder info, key policy references table, research context section

### Data Validation
- Confirmed zoning integration: multifamily % correlates positively with zoning-permitted height
- CBD zones show highest avg stories (~21–25), SF zones lowest (~2–3)
- Census-estimated ETJ areas average 1.59 stories (consistent with rural/exurban character)
- Zero response areas with no height data after fallback

### Key Decisions
| Decision | Rationale |
|----------|-----------|
| Use zoning codes as height proxy instead of building footprints | Current data, full city coverage, directly tied to what *can* be built |
| Census housing mix as ETJ fallback with flag | ETJ areas lack zoning; B25024 housing type distribution is a reasonable proxy for typical building scale |
| Area-weighted allocation (not centroid) | More accurate for large response areas that span multiple zoning districts |
| Vertical mixed-use overlay → 6-story minimum | `-V` overlay explicitly permits taller development regardless of base zone |

### Pending
- [ ] Suburban vs urban contrast analysis and incident cause geographic mapping
- [ ] Consider 2013 building footprint data as historical baseline (temporal gap concern)
- [ ] Commit changes on `feature/building-height-data`
