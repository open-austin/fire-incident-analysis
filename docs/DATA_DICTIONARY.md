# Data Dictionary

This document describes every dataset produced by the Austin Fire Incident Analysis project. Each section covers one file, listing what it contains, how many records it has, and what every column means in plain language.

**Who is this for?** Anyone reviewing our data — policy analysts, council staff, community members, or new contributors. No programming knowledge required.

**Where are these files?** All processed datasets live in the `processed_data/` folder. Analysis summaries and visualizations live in the `outputs/` folder.

---

## Table of Contents

1. [Processed Datasets](#processed-datasets)
   - [incidents_clean.csv](#incidents_cleancsv) — Cleaned fire incidents
   - [incidents_with_parcels.csv](#incidents_with_parcelscsv) — Incidents matched to properties
   - [incidents_enriched.csv](#incidents_enrichedcsv) — Fully enriched incidents (final)
   - [response_area_demographics.csv](#response_area_demographicscsv) — Demographics by response area
   - [tract_to_response_area_crosswalk.csv](#tract_to_response_area_crosswalkcsv) — Census-to-response-area mapping
2. [Analysis Outputs](#analysis-outputs)
   - [summary_by_urban_class.csv](#summary_by_urban_classcsv) — Rates by urban/suburban type
   - [summary_by_housing_type.csv](#summary_by_housing_typecsv) — Rates by housing mix
   - [summary_by_building_age.csv](#summary_by_building_agecsv) — Rates by building age
   - [summary_by_incident_type.csv](#summary_by_incident_typecsv) — Incident type counts
   - [fire_rates_by_building_type.csv](#fire_rates_by_building_typecsv) — Rates by building type (parcel-level)
   - [fire_rates_by_year_built.csv](#fire_rates_by_year_builtcsv) — Rates by year built (parcel-level)
3. [NFIRS Cause Analysis Outputs](#nfirs-cause-analysis-outputs)
   - [cause_by_housing_type.csv](#cause_by_housing_typecsv)
   - [heat_source_by_housing.csv](#heat_source_by_housingcsv)
4. [Key Terms](#key-terms)

---

## Processed Datasets

These are the main datasets our pipeline produces. Each one builds on the previous, adding more context to each fire incident.

---

### incidents_clean.csv

**What is it?** The cleaned and classified list of all Austin Fire Department incidents from 2022 through 2024. This is the starting point for all analysis.

**How many records?** 20,934 incidents

**Created by:** `02_clean_incidents.py`

| Column | What It Means |
|--------|--------------|
| `incident_number` | Unique ID assigned by AFD to each incident (e.g., "22000002") |
| `calendaryear` | The year the incident occurred (2022, 2023, or 2024) |
| `month` | The month the incident occurred (e.g., "Jan", "Feb") |
| `incdate` | The full date and time of the incident |
| `call_type` | The general type of call (e.g., "Fire") |
| `problem` | The specific problem reported (e.g., "STRUCTURE - Structure Fire", "GRASS - Small Grass Fire") |
| `responsearea` | The AFD response area where the incident occurred (e.g., "00-2403"). Austin is divided into 711 of these zones |
| `jurisdiction` | The jurisdiction that responded (typically "AFD" for Austin Fire Department) |
| `prioritydescription` | The priority level assigned to the call |
| `council_district` | The Austin City Council district number where the incident occurred |
| `location` | The original location coordinates as reported |
| `longitude` | The east-west coordinate of the incident (negative numbers = west of Greenwich) |
| `latitude` | The north-south coordinate of the incident |
| `is_structure_fire` | True/False — Was this a fire in a building? Includes both non-confined (BOX alarm) and confined (electrical, cooking) structure fires, aligned with NFPA/NFIRS reporting standards |
| `is_nonconfined_structure_fire` | True/False — Was this a non-confined structure fire? These are BOX alarm dispatches where fire spread beyond its origin point (NFIRS code 111) |
| `is_confined_structure_fire` | True/False — Was this a confined structure fire? These are electrical (ELEC) and cooking (BBQ) fires that typically stayed at their point of origin (NFIRS codes 113-118) |
| `is_vehicle_fire` | True/False — Was this a vehicle fire? |
| `is_outdoor_fire` | True/False — Was this a grass, brush, or outdoor fire? |
| `is_trash_fire` | True/False — Was this a trash or dumpster fire? |
| `incident_category` | A plain-language grouping: "Structure Fire (non-confined)", "Structure Fire (confined)", "Vehicle Fire", "Outdoor/Vegetation Fire", "Trash/Dumpster Fire", or "Other" |

---

### incidents_with_parcels.csv

**What is it?** Each fire incident matched to the specific property (parcel) where it occurred. This lets us know what type of building was involved, when it was built, and its assessed value.

**How many records?** 20,921 incidents (99.9% match rate)

**Created by:** `07_parcel_join.py`

This file contains all the columns from `incidents_clean.csv` (above), plus:

| Column | What It Means |
|--------|--------------|
| `PARCEL_ID` | The unique ID for the property parcel from Travis County Appraisal District |
| `PROP_ID` | The property ID number |
| `LAND_USE` | Numeric code for how the land is used (e.g., 100 = residential) |
| `GENERAL_LAND_USE` | Broader land use category code |
| `PROPERTY_ADDRESS` | The street address of the property |
| `IMPRV_TYPE` | The type of building on the property. Common values: "1 FAM DWELLING" (single-family home), "APARTMENT 100+" (large apartment complex), "DUPLEX", "TOWNHOUSE", "COMMERCIAL", "RETAIL" |
| `BLDG_SQUARE_FOOTAGE` | The building's size in square feet |
| `YEAR_BUILT` | The year the building was constructed |
| `UNITS` | The number of housing units on this parcel (1 for a house, 200+ for a large apartment complex) |
| `ZONING_ZTYPE` | The full zoning code with any overlay suffixes (e.g., "MF-3-CO" means Multifamily-3 with a Conditional Overlay) |
| `ZONING_BASE` | The base zoning code without overlays (e.g., "MF" for Multifamily, "SF" for Single Family, "CS" for Commercial Services) |
| `COUNCIL_DISTRICT` | The council district from the parcel data |
| `MARKET_VALUE` | The estimated market value of the property (in dollars) |
| `APPRAISED_VAL` | The appraised value used for tax purposes (in dollars) |
| `LAND_ACRES` | The size of the parcel in acres |
| `FAR` | Floor Area Ratio — how much of the lot is covered by building. Higher numbers = denser construction |

---

### incidents_enriched.csv

**What is it?** The most complete version of our incident data. Each fire incident has been matched to its property AND enriched with zoning descriptions and Census demographics for the surrounding neighborhood. **This is the best file to use for most analysis.**

**How many records?** 20,921 incidents

**Created by:** `09_zoning_and_census.py`

This file contains all columns from `incidents_with_parcels.csv` (above), plus:

#### Zoning Information

| Column | What It Means |
|--------|--------------|
| `zoning_label` | Human-readable name for the zoning code (e.g., "Single Family Residential", "Central Business District", "Multifamily Residential") |
| `zoning_category` | Broad grouping: "Residential", "Commercial", "Industrial", "Mixed-Use", "Public/Civic", or "Special" |

#### Census Tract Information

| Column | What It Means |
|--------|--------------|
| `census_tract_geoid` | The unique Census ID for the tract where this incident occurred (e.g., "48453002441") |
| `census_county_fips` | The county code: 453 = Travis, 209 = Hays, 491 = Williamson |
| `census_tract_name` | The Census tract number (e.g., "24.41") |
| `census_tract_land_area_sqm` | The land area of the Census tract in square meters |

#### Census Population and Housing (for the tract where this incident occurred)

| Column | What It Means |
|--------|--------------|
| `census_population` | Total population of the Census tract |
| `housing_total_units` | Total number of housing units in the tract |
| `housing_1_detached` | Number of single-family detached homes (standalone houses) |
| `housing_1_attached` | Number of single-family attached homes (e.g., townhomes sharing a wall) |
| `housing_2_units` | Number of units in duplex buildings (2-unit buildings) |
| `housing_3_4_units` | Number of units in small apartment buildings (3-4 units) |
| `housing_5_9_units` | Number of units in small-medium apartment buildings (5-9 units) |
| `housing_10_19_units` | Number of units in medium apartment buildings (10-19 units) |
| `housing_20_49_units` | Number of units in mid-size apartment buildings (20-49 units) |
| `housing_50plus_units` | Number of units in large apartment complexes (50+ units) |
| `housing_mobile_home` | Number of mobile homes |
| `housing_boat_rv_van` | Number of boat, RV, or van housing units |

#### Census Year Built (for the tract where this incident occurred)

| Column | What It Means |
|--------|--------------|
| `yrbuilt_total` | Total housing units with known construction year |
| `yrbuilt_2020_later` | Units built in 2020 or later |
| `yrbuilt_2010_2019` | Units built between 2010 and 2019 |
| `yrbuilt_2000_2009` | Units built between 2000 and 2009 |
| `yrbuilt_1990_1999` | Units built in the 1990s |
| `yrbuilt_1980_1989` | Units built in the 1980s |
| `yrbuilt_1970_1979` | Units built in the 1970s |
| `yrbuilt_1960_1969` | Units built in the 1960s |
| `yrbuilt_1950_1959` | Units built in the 1950s |
| `yrbuilt_1940_1949` | Units built in the 1940s |
| `yrbuilt_1939_earlier` | Units built before 1940 |

---

### response_area_demographics.csv

**What is it?** A summary of population, housing, and building age for each of Austin's fire response areas. These numbers come from U.S. Census data, allocated to response areas using geographic overlap.

**How many records?** 753 response areas (some areas have multiple entries due to overlapping tracts)

**Created by:** `03_create_crosswalk.py`

| Column | What It Means |
|--------|--------------|
| `response_area_id` | The AFD response area ID number |
| **Population & Housing Counts** | |
| `population` | Estimated number of people living in this response area |
| `total_units` | Total estimated housing units |
| `single_family` | Number of single-family homes (detached + attached) |
| `duplex` | Number of units in 2-unit buildings |
| `small_multifamily` | Number of units in buildings with 3-19 units |
| `large_multifamily` | Number of units in buildings with 20+ units |
| `multifamily` | All multifamily units combined (duplex + small + large) |
| `mobile_other` | Mobile homes and other housing types |
| **Building Age** | |
| `yb_total` | Total units with known construction year |
| `built_2010_plus` | Units built 2010 or later (likely has modern sprinkler systems) |
| `built_1970_2009` | Units built between 1970 and 2009 |
| `built_pre_1970` | Units built before 1970 (older construction, less likely to have sprinklers) |
| **Percentages** | |
| `pct_single_family` | What percent of housing is single-family |
| `pct_duplex` | What percent is duplex |
| `pct_small_mf` | What percent is small multifamily (3-19 units) |
| `pct_large_mf` | What percent is large multifamily (20+ units) |
| `pct_multifamily` | What percent is any type of multifamily |
| `pct_built_2010_plus` | What percent of buildings were built after 2010 |
| `pct_built_1970_2009` | What percent were built 1970-2009 |
| `pct_built_pre_1970` | What percent were built before 1970 |

---

### tract_to_response_area_crosswalk.csv

**What is it?** A technical mapping file that shows how Census tracts overlap with AFD response areas. Used internally to allocate Census population and housing data to response areas based on geographic overlap.

**How many records?** 2,642 (each row is one Census tract / response area pair)

**Created by:** `03_create_crosswalk.py`

| Column | What It Means |
|--------|--------------|
| `GEOID` | The Census tract ID |
| `response_area_id` | The AFD response area ID |
| `weight` | What fraction of the Census tract's area falls within this response area (0 to 1). For example, 0.25 means 25% of the tract overlaps with this response area |
| `tract_area` | The total area of the Census tract (in square meters) |
| `intersect_area` | The area where the tract and response area overlap (in square meters) |

---

## Analysis Outputs

These files contain the results of our analysis — rates, comparisons, and statistical findings. They live in the `outputs/` folder.

---

### summary_by_urban_class.csv

**What is it?** Fire incident rates compared across three types of areas: urban core, inner suburban, and outer suburban.

**How many records?** 3 (one per urban class)

**Created by:** `04_analysis.py`

| Column | What It Means |
|--------|--------------|
| `urban_class` | The type of area: **urban_core** (very dense, 10,000+ people per sq mi), **inner_suburban** (moderate density, 3,000-10,000), or **outer_suburban** (low density, under 3,000) |
| `population` | Total estimated population in this class |
| `total_units` | Total housing units |
| `single_family` | Number of single-family homes |
| `multifamily` | Number of multifamily units |
| `total_incidents` | Total fire incidents (2022-2024) |
| `structure_fires` | Number of structure fires specifically |
| `area_sq_miles` | Total land area in square miles |
| `num_response_areas` | How many response areas fall in this class |
| `incidents_per_1000_pop` | Fire incidents per 1,000 residents (3-year total) |
| `incidents_per_1000_units` | Fire incidents per 1,000 housing units (3-year total) |
| `structure_fires_per_1000_units` | Structure fires per 1,000 housing units (3-year total) |
| `pop_density` | Population density (people per square mile) |
| `pct_single_family` | Percent of housing that is single-family |
| `annual_incidents_per_1000_pop` | Yearly average incidents per 1,000 residents |
| `annual_incidents_per_1000_units` | Yearly average incidents per 1,000 housing units |

---

### summary_by_housing_type.csv

**What is it?** Fire incident rates compared by how much single-family housing dominates the area. Areas are grouped into four buckets based on the percent of housing that is single-family.

**How many records?** 4 (one per housing category)

**Created by:** `04_analysis.py`

| Column | What It Means |
|--------|--------------|
| `sf_category` | The housing mix bucket: **<25% SF** (mostly apartments), **25-50% SF**, **50-75% SF**, or **>75% SF** (mostly houses) |
| `population` | Total population in areas of this type |
| `total_units` | Total housing units |
| `total_incidents` | Total fire incidents (2022-2024) |
| `structure_fires` | Number of structure fires |
| `num_response_areas` | Number of response areas in this category |
| `incidents_per_1000_pop` | Incidents per 1,000 residents |
| `incidents_per_1000_units` | Incidents per 1,000 housing units |
| `structure_fires_per_1000_units` | Structure fires per 1,000 housing units |

---

### summary_by_building_age.csv

**What is it?** Compares fire rates between areas with newer buildings (majority built after 2010, likely with modern sprinkler systems) and areas with older building stock.

**How many records?** 2 (newer vs. older)

**Created by:** `04_analysis.py`

| Column | What It Means |
|--------|--------------|
| `building_age` | **Newer (50%+ post-2010)** = areas where most buildings are recent; **Older (<50% post-2010)** = areas with mostly older buildings |
| `population` | Total population |
| `total_units` | Total housing units |
| `total_incidents` | Total fire incidents |
| `structure_fires` | Number of structure fires |
| `num_areas` | Number of response areas |
| `incidents_per_1000_pop` | Incidents per 1,000 residents |
| `structure_per_1000_units` | Structure fires per 1,000 housing units |

---

### summary_by_incident_type.csv

**What is it?** A count of how many incidents fall into each category (structure fire, vehicle fire, outdoor fire, etc.).

**Created by:** `04_analysis.py`

---

### fire_rates_by_building_type.csv

**What is it?** Fire rates calculated at the individual property (parcel) level, grouped by building type. This is the most granular view — it tells us exactly which types of buildings have the most fires.

**How many records?** 9 building types

**Created by:** `08_parcel_analysis.py`

| Column | What It Means |
|--------|--------------|
| `building_type` | The type of building: Single Family, Duplex, Small Multifamily (3-4 units), Mid Multifamily (5-25), Large Multifamily (50+), Commercial, Industrial/Warehouse, Hotel/Hospitality, Manufactured Home |
| `total_parcels` | How many properties of this type exist in Austin |
| `all_incidents` | Total fire incidents at these properties (2022-2024) |
| `structure_fires` | Number of structure fires at these properties |
| `trash_fires` | Number of trash/dumpster fires at these properties |
| `all_rate_per_1k` | All fire incidents per 1,000 properties of this type |
| `structure_rate_per_1k` | Structure fires per 1,000 properties of this type |
| `trash_rate_per_1k` | Trash fires per 1,000 properties of this type |

**Key finding:** Large multifamily complexes have 1,351 structure fires per 1,000 parcels vs. 8.0 for single-family homes. This is because each large complex contains hundreds of units, so more people and more potential fire sources per parcel. Structure fire counts include both non-confined (BOX alarm) and confined (electrical, cooking) fires per NFPA standards.

---

### fire_rates_by_year_built.csv

**What is it?** Fire rates grouped by when buildings were constructed, using parcel-level data.

**Created by:** `08_parcel_analysis.py`

---

## Townhome Analysis Outputs

---

### townhome_incidents.csv (processed_data)

**What is it?** All fire incidents at parcels classified as "TOWNHOMES" by TCAD, including both true individual townhome units and multi-unit condo complexes that TCAD mislabels as townhomes. Includes backfilled year-built data from property records for 9 condo complexes missing this data in TCAD.

**How many records?** 46 incidents

**Created by:** `10_townhome_cohort_analysis.py`

**Data quality note:** TCAD's "TOWNHOMES" classification includes 355 multi-unit condo complexes (10-234 units per parcel). True individual townhomes have UNITS <= 1. Filter on the `UNITS` column to distinguish them.

---

### townhome_rates_by_cohort.csv

**What is it?** Fire incident rates per 1,000 parcels for all TCAD "TOWNHOMES" parcels, grouped by fire code era (pre-2019, 2019-2021, post-2021). Includes year-built data backfilled from property records.

**How many records?** 3 (one per code cohort)

**Created by:** `10_townhome_cohort_analysis.py`

**Key finding:** With only 5 structure fires across 3,896 true townhome parcels in 3 years, rates are very low (~1 in 671 parcels/year) but cannot support code cohort comparisons. Would require ~55 years of data at current rates to reach statistical significance.

---

### townhome_cohort_summary.txt

**What is it?** A comprehensive text summary of the townhome analysis including data quality findings, fire rarity context, national NFPA comparisons, and honest assessment of what the data can and cannot support.

**Created by:** `10_townhome_cohort_analysis.py`

---

## NFIRS Cause Analysis Outputs

These files come from the National Fire Incident Reporting System (NFIRS) data, which provides detailed information about what caused each fire. This data covers 2018-2021 and requires a separate manual download.

---

### cause_by_housing_type.csv

**What is it?** Breaks down fire causes (intentional, unintentional, equipment failure, etc.) comparing multifamily buildings to single-family homes.

**Created by:** `06_nfirs_cause_analysis.py`

---

### heat_source_by_housing.csv

**What is it?** What was the heat source that started the fire — cooking equipment, smoking materials, electrical, heating equipment, or open flame — comparing multifamily to single-family.

**Created by:** `06_nfirs_cause_analysis.py`

---

## Key Terms

| Term | Definition |
|------|-----------|
| **AFD** | Austin Fire Department |
| **Response area** | One of 711 geographic zones that Austin is divided into for fire response. Each is served by a specific fire station |
| **Census tract** | A small geographic area defined by the U.S. Census Bureau, typically containing 1,200 to 8,000 people |
| **Parcel** | A single piece of property (a lot) as defined by the county appraisal district. One parcel might contain a house, an apartment complex, or a commercial building |
| **Structure fire** | A fire that occurs in a building. Following NFPA/NFIRS standards, this includes both **non-confined** fires (BOX alarm dispatches where fire spread, NFIRS code 111) and **confined** fires (electrical and cooking fires that stayed at origin, NFIRS codes 113-118). AFD dispatch codes (BOX, ELEC, BBQ) determine response level, not incident classification |
| **Multifamily** | Housing with multiple units in one building — apartments, condos, duplexes, etc. |
| **Single-family** | A standalone house on its own lot, designed for one household |
| **Per 1,000 rate** | A way to make fair comparisons. "5 fires per 1,000 units" means that for every 1,000 housing units, there were 5 fire incidents. This adjusts for the fact that larger areas naturally have more fires |
| **ACS / American Community Survey** | An ongoing Census Bureau survey that provides yearly estimates of population, housing, income, and other demographics |
| **NFIRS** | National Fire Incident Reporting System — a federal database where fire departments report detailed information about fire causes |
| **ETJ** | Extra-Territorial Jurisdiction — areas outside Austin's city limits but within its planning authority. These areas don't have city zoning |
| **Sprinkler code** | Austin adopted a residential sprinkler requirement around 2006 (effective ~2010 for new construction). Buildings built after this are more likely to have fire sprinklers |
| **Townhome fire code cohorts** | Austin changed townhome fire protection requirements over time: Pre-2019 required 2-hour fire separation walls only; 2019-2021 allowed builder's choice between 2-hour walls or 1-hour walls with sprinklers; Post-2021 requires sprinklers in all new townhomes |
| **Non-confined fire** | A structure fire where flames spread beyond the point of origin, triggering a full BOX alarm response (multiple engines, ladder truck). NFIRS code 111 |
| **Confined fire** | A structure fire that stayed contained at its origin point (e.g., a cooking fire on a stove, an electrical panel fire). Dispatched as ELEC or BBQ with a lighter response. NFIRS codes 113-118 |
| **NFPA** | National Fire Protection Association — sets fire safety standards and publishes national fire statistics. Their methodology counts both confined and non-confined fires as structure fires |
| **HOME initiative** | A proposed Austin land use reform that would allow more housing density in traditionally single-family neighborhoods |
| **Single-stair building code** | A proposed building code change that would allow residential buildings (typically up to 6 stories) to be built with one stairwell instead of two, enabling more housing units per floor |
| **FAR (Floor Area Ratio)** | The ratio of a building's total floor area to the size of the lot. Higher FAR = denser development |
| **Choropleth map** | A map where areas are shaded based on a data value (e.g., darker red = more fires per capita) |
