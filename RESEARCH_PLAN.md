# Fire Department Resource Allocation Analysis
## Research Hub: Austin Housing & Land Use Working Group

---

## Executive Summary

**Research Question:** Do suburban areas in Austin utilize disproportionate fire department resources on a per-capita basis compared to urban areas?

**Policy Relevance:**
- Informs the single-stair/mid-rise building debate
- Addresses fire department concerns about aerial equipment needs
- Provides data for budget and zoning discussions
- Connects to the Pew report on multifamily building safety

**Core Hypothesis:** Suburban areas with predominantly single-family housing consume more fire resources per capita and experience higher fire incident rates than denser urban areas with multifamily housing.

---

## Data Sources

### 1. Austin Fire Department Data

| Dataset | API Endpoint | Description |
|---------|-------------|-------------|
| **AFD Fire Incidents 2022-2024** | `https://data.austintexas.gov/resource/v5hh-nyr8.json` | Recent fire incident records with location, type, response area |
| **AFD Fire Incidents 2018-2021** | `https://data.austintexas.gov/resource/j9w8-x2vu.json` | Historical incident data for trend analysis |
| **Fire Stations** | `https://data.austintexas.gov/resource/szku-46rx.json` | Station locations and information |
| **AFD Response Areas** | ArcGIS FeatureServer (see below) | Geographic boundaries for first-due response |

**ArcGIS Endpoint for Response Areas:**
```
Base: https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/BOUNDARIES_afd_response_areas/FeatureServer/0

Query all features as GeoJSON:
/query?where=1=1&outFields=*&outSR=4326&f=geojson
```

**Key Fields in Incident Data:**
- `incident_number` - Unique ID
- `problem` - Specific incident type (STRUCTURE FIRE, GRASS FIRE, TRASH FIRE, etc.)
- `call_type` - General category (Fire, Rescue, Hazmat)
- `responsearea` - First-due response area code
- `location` - Lat/long coordinates
- `council_district` - City Council district

---

### 2. Census / American Community Survey Data

| Table | Variables | Description |
|-------|-----------|-------------|
| **B01003** | `B01003_001E` | Total Population |
| **B25024** | `B25024_001E` through `B25024_011E` | Units in Structure (housing typology) |
| **B25034** | `B25034_001E` through `B25034_011E` | Year Structure Built |
| **B19013** | `B19013_001E` | Median Household Income |

**Census API Query Pattern:**
```
https://api.census.gov/data/2022/acs/acs5?get=B25024_001E,B25024_002E,...&for=tract:*&in=state:48&in=county:453
```

**B25024 Housing Unit Breakdown:**
| Variable | Description |
|----------|-------------|
| B25024_002E | 1, detached (single-family detached) |
| B25024_003E | 1, attached (townhouse) |
| B25024_004E | 2 units (duplex) |
| B25024_005E | 3 or 4 units |
| B25024_006E | 5 to 9 units |
| B25024_007E | 10 to 19 units |
| B25024_008E | 20 to 49 units |
| B25024_009E | 50 or more units |
| B25024_010E | Mobile home |
| B25024_011E | Boat, RV, van, etc. |

---

### 3. Additional Context Data

| Dataset | Source | Use |
|---------|--------|-----|
| Census Tract Boundaries | Census TIGER/Line | Spatial join for demographics |
| City Limits | Austin Open Data | Define study area |
| Zoning Districts | Austin Open Data | Control for commercial vs residential |
| Council Districts | Austin Open Data | Political geography for findings |

---

## Methodology

### Phase 1: Data Collection & Preparation

1. **Download fire incident data** (2018-2024, ~6 years)
   - Filter to fire-related calls only (exclude medical, hazmat unless relevant)
   - Geocode any records missing coordinates
   - Validate response area assignments

2. **Retrieve AFD response area boundaries**
   - Download as GeoJSON from ArcGIS
   - Calculate area (sq miles) for each response zone

3. **Pull Census demographics at tract level**
   - Population (B01003)
   - Housing units by type (B25024)
   - Housing age (B25034) - potential confounding variable
   - Income (B19013) - potential confounding variable

4. **Spatial crosswalk: Census tracts → Response areas**
   - Use area-weighted interpolation to allocate tract data to response areas
   - Alternative: Point-in-polygon for tract centroids

### Phase 2: Classification

**Urban/Suburban Classification Options:**

| Method | Thresholds | Pros/Cons |
|--------|------------|-----------|
| **Population Density** | Urban: >10k/sq mi; Suburban: 3-10k; Exurban: <3k | Simple, defensible |
| **Distance from Downtown** | <3mi; 3-8mi; >8mi | Captures sprawl pattern |
| **Housing Typology** | >50% SF = suburban | Directly tests hypothesis |
| **Composite Index** | Combine density + typology + age | More nuanced |

**Recommended:** Use population density as primary, validate with housing typology.

### Phase 3: Analysis

**Core Metrics to Calculate:**

| Metric | Formula | What It Shows |
|--------|---------|---------------|
| Incidents per 1,000 residents | `(incidents / population) * 1000` | Per-capita demand |
| Incidents per 1,000 housing units | `(incidents / units) * 1000` | Per-unit risk |
| Structure fires per 1,000 units | Same, filtered to structure fires | Building fire risk |
| Response area coverage (sq mi per station) | `area / stations` | Service efficiency |

**Statistical Tests:**
- ANOVA / t-tests comparing urban vs suburban rates
- Regression controlling for income, housing age
- Spatial autocorrelation (Moran's I) to check clustering

### Phase 4: Deliverables

1. **Summary Statistics Table**
   - Incident rates by urban classification
   - Incident rates by housing typology
   - Confidence intervals

2. **Maps**
   - Choropleth: Incidents per capita by response area
   - Choropleth: Housing typology distribution
   - Dot density: Fire incident locations

3. **Key Findings Brief**
   - 1-2 page summary for policy audiences
   - Clear statement on whether hypothesis is supported

---

## Expected Findings & Implications

### If Hypothesis is Supported (Suburban > Urban fire burden):

- **Budget argument:** Suburban expansion costs more in fire services per capita
- **Density argument:** Allowing infill/mid-rise doesn't increase fire burden proportionally
- **Single-stair argument:** Dense buildings may actually be more efficient to serve
- **Zoning argument:** Sprawl-inducing zoning imposes hidden costs

### If Hypothesis is NOT Supported:

- Need to examine why (older building stock? More commercial in urban core?)
- May still find interesting patterns by incident type
- Important to report null findings honestly

### Confounding Variables to Address:

| Variable | Why It Matters | How to Control |
|----------|----------------|----------------|
| **Housing age** | Older buildings = more fire risk, often in urban core | Include B25034 in regression |
| **Income** | Lower income areas may have more fires (deferred maintenance) | Include B19013 |
| **Commercial uses** | Urban core has more commercial, different fire profile | Filter or segment |
| **Mutual aid** | Some areas served by ESD, not AFD | Verify jurisdiction field |

---

## Timeline

| Week | Tasks |
|------|-------|
| 1 | Data collection, cleaning, geocoding |
| 2 | Spatial joins, crosswalk creation |
| 3 | Calculate metrics, classification |
| 4 | Statistical analysis, mapping |
| 5 | Write-up, review with Tim |
| 6 | Finalize, prepare for publication |

---

## Tools & Environment

**Recommended Stack:**
- Python 3.10+ with geopandas, pandas, requests
- QGIS or ArcGIS Pro for cartography
- Jupyter notebooks for reproducible analysis

**Key Python Libraries:**
```bash
pip install pandas geopandas requests shapely folium matplotlib seaborn scipy
```

**Alternative: R Stack**
```r
install.packages(c("sf", "tidycensus", "dplyr", "ggplot2", "tmap"))
```

---

## References

- Pew Research Center report on multifamily building safety
- AFD Standard of Coverage documentation
- Austin City Council budget discussions (FY2024-2025)
- NFPA Fire Incident Data Organization (FIDO) guidelines

---

## Contact

Research Hub Working Group  
Questions: [Tim - contact info]
