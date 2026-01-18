# Fire Resource Analysis: Task Tracker

## Project Overview

**Goal:** Test whether suburban areas in Austin consume disproportionate fire resources per capita compared to urban areas.

**Timeline:** 4-6 weeks (part-time)  
**Output:** Data-backed brief for Research Hub + supporting visualizations

---

## Phase 1: Data Acquisition (Week 1)

### Task 1.1: Download Fire Incident Data
**Time:** 1-2 hours  
**Output:** `incidents_2018_2024.csv`

```bash
# Download via curl or browser
curl "https://data.austintexas.gov/api/views/v5hh-nyr8/rows.csv?accessType=DOWNLOAD" \
  -o incidents_2022_2024.csv

curl "https://data.austintexas.gov/api/views/j9w8-x2vu/rows.csv?accessType=DOWNLOAD" \
  -o incidents_2018_2021.csv
```

**Checklist:**
- [ ] Download 2022-2024 incidents
- [ ] Download 2018-2021 incidents  
- [ ] Combine into single file
- [ ] Note: How many records total? How many have valid coordinates?

---

### Task 1.2: Download Response Area Boundaries
**Time:** 30 min  
**Output:** `afd_response_areas.geojson`

```bash
curl "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/BOUNDARIES_afd_response_areas/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson" \
  -o afd_response_areas.geojson
```

**Checklist:**
- [ ] Download GeoJSON
- [ ] Open in QGIS/kepler.gl to verify geometry
- [ ] Note: How many response areas? What fields are included?

---

### Task 1.3: Download Census Data
**Time:** 1-2 hours  
**Output:** `census_tracts_travis.csv`, `census_tracts_travis.geojson`

**Option A: Census API**
```python
import requests
import pandas as pd

# Population by tract
url = "https://api.census.gov/data/2022/acs/acs5"
params = {
    "get": "B01003_001E,NAME",
    "for": "tract:*",
    "in": "state:48 county:453"
}
response = requests.get(url, params=params)
pop_data = pd.DataFrame(response.json()[1:], columns=response.json()[0])

# Housing units by type (B25024)
params["get"] = "B25024_001E,B25024_002E,B25024_003E,B25024_004E,B25024_005E,B25024_006E,B25024_007E,B25024_008E,B25024_009E,B25024_010E,B25024_011E,NAME"
response = requests.get(url, params=params)
housing_data = pd.DataFrame(response.json()[1:], columns=response.json()[0])
```

**Option B: Census Reporter**
- https://censusreporter.org/profiles/05000US48453-travis-county-tx/
- Download tract-level tables B01003 and B25024

**Option C: TIGER Boundaries**
```bash
curl "https://www2.census.gov/geo/tiger/TIGER2022/TRACT/tl_2022_48_tract.zip" -o texas_tracts.zip
unzip texas_tracts.zip
# Filter to Travis County (COUNTYFP = 453)
```

**Checklist:**
- [ ] Download population (B01003)
- [ ] Download housing typology (B25024)
- [ ] Download tract boundaries
- [ ] Filter to Travis County
- [ ] Create GEOID field for joining

---

### Task 1.4: Download Supporting Data
**Time:** 1 hour

| Dataset | Source | Purpose |
|---------|--------|---------|
| Fire Stations | `data.austintexas.gov/resource/szku-46rx.json` | Station locations |
| City Limits | Austin Open Data | Study boundary |

**Checklist:**
- [ ] Download fire station locations
- [ ] Download city limits boundary

---

## Phase 2: Data Exploration (Week 1-2)

### Task 2.1: Explore Incident Data
**Time:** 2-3 hours

```python
import pandas as pd
df = pd.read_csv("incidents_2022_2024.csv")

print(f"Total records: {len(df)}")
print(f"Date range: {df['incdate'].min()} to {df['incdate'].max()}")
print(f"Records with coordinates: {df['location'].notna().sum()}")
print(df['problem'].value_counts().head(20))
print(df['call_type'].value_counts())
```

**Checklist:**
- [ ] How many incidents total?
- [ ] What % have valid coordinates?
- [ ] What are the top incident types?
- [ ] How many are structure fires vs grass/trash?

---

### Task 2.2: Explore Response Areas
**Time:** 1 hour

```python
import geopandas as gpd
gdf = gpd.read_file("afd_response_areas.geojson")
gdf = gdf.to_crs("EPSG:32614")
gdf["area_sq_miles"] = gdf.geometry.area / 2.59e6
print(gdf["area_sq_miles"].describe())
```

**Checklist:**
- [ ] What fields identify each area?
- [ ] What's the size distribution?
- [ ] Do boundaries look correct?

---

### Task 2.3: Explore Census Data
**Time:** 1 hour

**Checklist:**
- [ ] Total population in Travis County
- [ ] Total housing units
- [ ] SF vs MF split
- [ ] Any zero-population tracts?

---

## Phase 3: Spatial Joins (Week 2)

### Task 3.1: Join Incidents to Response Areas
**Time:** 2 hours  
**Output:** `incidents_with_response_area.csv`

```python
from shapely.geometry import Point
import geopandas as gpd

def parse_location(loc):
    if pd.isna(loc): return None
    try:
        lon, lat = loc.strip("()").split(",")
        return Point(float(lon), float(lat))
    except: return None

incidents["geometry"] = incidents["location"].apply(parse_location)
incidents_gdf = gpd.GeoDataFrame(incidents, geometry="geometry", crs="EPSG:4326")
incidents_joined = gpd.sjoin(incidents_gdf, response_areas, how="left", predicate="within")
```

**Checklist:**
- [ ] Parse coordinates
- [ ] Spatial join
- [ ] Validate against `responsearea` field
- [ ] Count incidents outside boundaries

---

### Task 3.2: Build Tract → Response Area Crosswalk
**Time:** 3-4 hours  
**Output:** `tract_to_response_area_crosswalk.csv`

**Area-Weighted Interpolation:**
```python
tracts = tracts.to_crs("EPSG:32614")
response_areas = response_areas.to_crs("EPSG:32614")
tracts["tract_area"] = tracts.geometry.area

overlay = gpd.overlay(tracts, response_areas, how="intersection")
overlay["intersection_area"] = overlay.geometry.area
overlay["weight"] = overlay["intersection_area"] / overlay["tract_area"]
```

**Checklist:**
- [ ] Decide: area-weighted vs centroid
- [ ] Build crosswalk
- [ ] Validate population totals

---

### Task 3.3: Aggregate Census to Response Areas
**Time:** 1-2 hours  
**Output:** `response_areas_with_demographics.csv`

```python
merged["allocated_pop"] = merged["population"] * merged["weight"]
response_area_stats = merged.groupby("response_area_id").agg({
    "allocated_pop": "sum",
    "allocated_sf_units": "sum",
    "allocated_mf_units": "sum"
}).reset_index()
```

**Checklist:**
- [ ] Allocate population
- [ ] Allocate housing units
- [ ] Calculate % SF per area
- [ ] Sanity check totals

---

## Phase 4: Classification (Week 2-3)

### Task 4.1: Calculate Density & Classify
**Time:** 1.5 hours

| Classification | Density (people/sq mi) |
|----------------|------------------------|
| Urban Core | ≥ 10,000 |
| Inner Suburban | 3,000 - 10,000 |
| Outer Suburban | 1,000 - 3,000 |
| Exurban | < 1,000 |

```python
def classify_urban(density):
    if density >= 10000: return "urban_core"
    elif density >= 3000: return "inner_suburban"
    elif density >= 1000: return "outer_suburban"
    else: return "exurban"

response_areas["urban_class"] = response_areas["pop_density"].apply(classify_urban)
```

**Checklist:**
- [ ] Calculate density
- [ ] Apply classification
- [ ] Map it - does it look right?
- [ ] Cross-tab with housing typology

---

## Phase 5: Core Analysis (Week 3)

### Task 5.1: Count Incidents by Area
**Time:** 1 hour

```python
total_counts = incidents.groupby("response_area_id").size().reset_index(name="total_incidents")
structure_fires = incidents[incidents["problem"].str.contains("STRUCTURE|BOX", case=False, na=False)]
structure_counts = structure_fires.groupby("response_area_id").size().reset_index(name="structure_fires")
```

**Checklist:**
- [ ] Count total incidents
- [ ] Count structure fires
- [ ] Other incident types?

---

### Task 5.2: Calculate Per-Capita Rates
**Time:** 1 hour

```python
analysis["incidents_per_1000_pop"] = (analysis["total_incidents"] / analysis["population"]) * 1000
analysis["incidents_per_1000_units"] = (analysis["total_incidents"] / analysis["total_units"]) * 1000
analysis["structure_fires_per_1000_units"] = (analysis["structure_fires"] / analysis["total_units"]) * 1000
```

**Checklist:**
- [ ] Incidents per 1,000 pop
- [ ] Incidents per 1,000 units
- [ ] Structure fires per 1,000 units

---

### Task 5.3: Compare Urban vs Suburban
**Time:** 2 hours

```python
from scipy import stats

urban = analysis[analysis["urban_class"] == "urban_core"]["incidents_per_1000_pop"]
suburban = analysis[analysis["urban_class"].isin(["outer_suburban", "exurban"])]["incidents_per_1000_pop"]

t_stat, p_value = stats.ttest_ind(urban, suburban, nan_policy="omit")
```

**Checklist:**
- [ ] Summary table by urban class
- [ ] Statistical test (t-test or ANOVA)
- [ ] Is difference significant?
- [ ] Effect size?

---

### Task 5.4: Analyze by Housing Typology
**Time:** 1 hour

```python
from scipy.stats import pearsonr
corr, p = pearsonr(analysis["pct_sf"], analysis["incidents_per_1000_units"])
```

**Checklist:**
- [ ] Correlation: %SF vs incident rate
- [ ] Summary by SF category
- [ ] Does higher SF% = more fires?

---

## Phase 6: Visualization (Week 3-4)

### Task 6.1: Create Maps
**Time:** 2-3 hours

**Maps needed:**
1. [ ] Population density choropleth
2. [ ] Incidents per capita choropleth
3. [ ] % Single-family choropleth
4. [ ] Urban/suburban classification

---

### Task 6.2: Create Charts
**Time:** 1-2 hours

**Charts needed:**
1. [ ] Bar: Incident rates by urban class
2. [ ] Scatter: %SF vs incident rate
3. [ ] Bar: Incident types breakdown

---

## Phase 7: Write-Up (Week 4)

### Task 7.1: Draft Key Findings
**Time:** 2-3 hours

**Checklist:**
- [ ] State main finding (hypothesis supported?)
- [ ] Include specific numbers
- [ ] Note limitations
- [ ] Policy implications

---

### Task 7.2: Review with Tim
**Time:** 1 hour

**Checklist:**
- [ ] Schedule meeting
- [ ] Share draft beforehand
- [ ] Incorporate feedback

---

### Task 7.3: Finalize Deliverables
**Time:** 2 hours

**Final outputs:**
- [ ] 1-2 page brief (PDF)
- [ ] Summary stats (CSV)
- [ ] Maps (PNG)
- [ ] Methodology appendix
- [ ] Code/notebooks

---

## Time Summary

| Phase | Hours |
|-------|-------|
| 1. Data Acquisition | 4-6 |
| 2. Exploration | 4-6 |
| 3. Spatial Joins | 6-8 |
| 4. Classification | 2-3 |
| 5. Analysis | 5-6 |
| 6. Visualization | 3-5 |
| 7. Write-Up | 5-6 |
| **Total** | **29-40** |

At ~10 hrs/week = **3-4 weeks**

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| | | |

---

## Next Action

**Start here:** Task 1.1 - Download fire incident data
