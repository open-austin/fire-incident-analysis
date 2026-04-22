# Project Guide: Austin Fire Incident Analysis

A plain-language guide for non-technical team members to understand what this project does, what we found, and where to find everything.

---

## What Is This Project?

We analyzed three years (2022-2024) of Austin Fire Department incident data to understand how fire risk varies across the city. Specifically, we looked at:

- **Where fires happen** — which neighborhoods and response areas see the most fires
- **What types of buildings are affected** — apartments vs. houses vs. commercial properties
- **Whether building age matters** — do older buildings have more fires?
- **What causes fires** — cooking, smoking, electrical issues, arson, etc.

This work supports policy discussions around Austin's **HOME initiative** (which would allow more housing density) and **single-stair building code** changes (which would affect new apartment design).

---

## What Did We Find?

### The big takeaways

1. **Multifamily buildings have significantly higher fire rates than single-family homes.** Areas dominated by apartments see roughly 4-6x more fire incidents per housing unit than areas dominated by houses.

2. **The gap is driven by cooking and smoking, not arson.** In multifamily buildings, 76% of fires are accidental — with cooking (24%) and smoking materials (18%) as leading causes. Arson is actually more common in single-family areas.

3. **Modern sprinkler codes help, but don't close the gap.** Buildings constructed after Austin's 2006 sprinkler requirement show ~60% fewer structure fires, but multifamily still outpaces single-family even in newer construction.

4. **Large apartment complexes stand out.** At the parcel level, large multifamily properties (50+ units) have 672 structure fires per 1,000 parcels compared to 4.7 for single-family — because each complex serves hundreds of households.

5. **Outer suburbs face a different challenge.** While fire *rates* are lower, each fire station covers 170 square miles compared to 1-4 square miles in urban areas — meaning longer response times.

---

## Where to Find Things

### Interactive Maps (open in any web browser)

These are HTML files in the `outputs/` folder. Double-click to open in your browser. You can zoom, pan, and click on areas to see details.

| File | What It Shows |
|------|--------------|
| `map_incidents_per_capita.html` | **Fire incident rates across Austin.** Darker red = more fires per resident. Great for seeing which parts of the city are most affected |
| `map_housing_typology.html` | **Housing mix across the city.** Shows what percent of each response area is single-family vs. multifamily |
| `map_urban_classification.html` | **Urban vs. suburban classification.** Color-coded by density: urban core, inner suburban, outer suburban |
| `map_building_age.html` | **Building age.** Shows where older (pre-1970) construction is concentrated |
| `map_fire_stations.html` | **Fire station locations** with coverage areas. Shows gaps in suburban coverage |

### Charts (PNG images)

Also in the `outputs/` folder. Open with any image viewer.

| File | What It Shows |
|------|--------------|
| `chart_urban_comparison.png` | Bar chart comparing fire rates across urban core, inner suburban, and outer suburban areas |
| `chart_housing_correlation.png` | Scatter plot showing the relationship between housing type and fire rates — more single-family = fewer fires |
| `chart_incident_type_by_housing.png` | What types of fires (structure, vehicle, outdoor, trash) happen in different housing areas |
| `chart_structure_fires_by_housing.png` | Structure fire trends over 2022-2024, split by housing type |
| `chart_building_age.png` | How building age relates to fire patterns |
| `chart_cause_comparison.png` | Side-by-side comparison of fire causes in multifamily vs. single-family (from NFIRS data) |
| `chart_heat_source_comparison.png` | What started the fire — cooking, smoking, electrical, etc. — by building type |

### Summary Tables (CSV spreadsheets)

These can be opened in Excel, Google Sheets, or any spreadsheet program. Located in `outputs/`.

| File | What It Shows |
|------|--------------|
| `summary_by_urban_class.csv` | Fire rates for urban core, inner suburban, and outer suburban — good quick reference for the density story |
| `summary_by_housing_type.csv` | Fire rates grouped by how much of the area is single-family — the core finding |
| `summary_by_building_age.csv` | Newer vs. older buildings and their fire rates |
| `fire_rates_by_building_type.csv` | Building-by-building fire rates (apartments, houses, commercial, etc.) — the most specific view |
| `station_coverage.csv` | How many fire stations serve each type of area and their coverage |
| `statistical_tests.txt` | The statistical significance of our findings (open with any text editor) |

### Written Report

| File | What It Shows |
|------|--------------|
| `outputs/REPORT_Austin_Fire_Analysis.md` | The full narrative report with methodology, findings, and policy implications. Can be opened in any text editor or Markdown viewer |
| `outputs/REPORT_Austin_Fire_Analysis.html` | Same report in HTML format — open in a web browser for formatted reading |
| `docs/POLICY_BRIEF.md` | Shorter policy brief focused on single-stair and HOME implications |

### Detailed Data Files

For anyone who wants to dig into the data directly (in Excel, Google Sheets, or a data tool), the main files are in `processed_data/`. See the [Data Dictionary](DATA_DICTIONARY.md) for what every column means.

| File | Best For |
|------|---------|
| `incidents_enriched.csv` | **Start here.** Every fire incident with full property, zoning, and Census details. The most complete dataset |
| `incidents_with_parcels.csv` | Fire incidents matched to specific properties — good for property-level questions |
| `response_area_demographics.csv` | Area-level demographics — good for "what kind of neighborhoods have more fires?" questions |

---

## How the Pipeline Works

Our analysis runs as a series of numbered Python scripts, each building on the last. You don't need to understand the code, but it helps to know the flow:

```
Step 1: Download Data
   01_download_data.py
   Pulls fire incidents, boundaries, Census data, and zoning from public APIs
        |
        v
Step 2: Clean Incidents
   02_clean_incidents.py
   Fixes dates, removes duplicates, classifies each fire by type
        |
        v
Step 3: Build Demographics
   03_create_crosswalk.py
   Maps Census population/housing data to AFD response areas
        |
        v
Step 4: Analyze
   04_analysis.py
   Calculates fire rates, runs statistical tests, produces summary tables
        |
        v
Step 5: Visualize
   05_visualize.py
   Creates interactive maps and charts
        |
        v
Step 6 (optional): Match to Parcels
   07_parcel_join.py → 08_parcel_analysis.py → 09_zoning_and_census.py
   Matches each fire to a specific property for building-type analysis
        |
        v
Step 7 (optional): Cause Analysis
   06_nfirs_cause_analysis.py
   Analyzes what caused fires using detailed federal (NFIRS) data
```

---

## Data Sources

All of our data comes from public sources:

| Data | Source | Years |
|------|--------|-------|
| Fire incidents | [Austin Open Data Portal](https://data.austintexas.gov) | 2022-2024 |
| Response area boundaries | City of Austin GIS | Current |
| Fire station locations | City of Austin GIS | Current |
| Property parcels | Travis County Appraisal District (via City of Austin) | Current |
| Zoning districts | City of Austin GIS | Current |
| Population & housing | U.S. Census Bureau, American Community Survey 5-Year | 2022 |
| Fire causes (NFIRS) | U.S. Fire Administration | 2018-2021 |

---

## Frequently Asked Questions

**Q: Can I open the CSV files in Excel?**
Yes! All `.csv` files open directly in Excel or Google Sheets. Just double-click or use File > Open.

**Q: Can I open the maps on my phone?**
Yes. The `.html` map files work in any web browser, including mobile. You may need to transfer the file first (email, USB, etc.).

**Q: Why do some numbers look like decimals (e.g., population = 243.53)?**
Because Census data is reported by Census tracts, which don't line up perfectly with AFD response areas. We split the Census numbers proportionally based on geographic overlap. A value like 243.53 means "approximately 244 people" after the proportional allocation.

**Q: What's the difference between "per 1,000 population" and "per 1,000 units"?**
- **Per 1,000 population** divides by the number of *people* living in an area. It answers: "how many fires happen relative to how many people live here?"
- **Per 1,000 units** divides by the number of *housing units* (apartments, houses, etc.). It answers: "how many fires happen relative to how many homes are here?"

We use both because they tell different stories. An apartment complex might house fewer people per unit than a house with a family, so the two rates can diverge.

**Q: Why are 2018-2021 incidents not included?**
The Austin Open Data Portal removed the 2018-2021 fire incident dataset. We use 2022-2024 for the main analysis. The NFIRS cause analysis uses 2018-2021 federal data (which is still available) for the separate question of what *causes* fires.

**Q: What does "statistically significant" mean in the findings?**
It means the patterns we found are very unlikely to be due to random chance. When we say p < 0.001, it means there's less than a 0.1% chance the pattern is a coincidence. In plain terms: the differences are real, not flukes.

**Q: I want to filter the data for a specific council district. How?**
Open `incidents_enriched.csv` in Excel or Google Sheets. Use the filter feature on the `council_district` column to show only the district you're interested in.

---

## Background Reading

- [docs/RESEARCH_CONTEXT.md](RESEARCH_CONTEXT.md) — Policy background on the HOME initiative, single-stair building code, and glossary of zoning terms
- [docs/POLICY_BRIEF.md](POLICY_BRIEF.md) — Focused policy brief connecting findings to current Austin policy discussions
- The full [Data Dictionary](DATA_DICTIONARY.md) — Every column in every dataset, explained in plain language
