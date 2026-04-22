# Multifamily Fire Cause Analysis Design

**Status:** ✅ Implemented in `06_nfirs_cause_analysis.py` — cause, heat source, area of origin, and sprinkler analyses complete. Building height analysis added March 2026 (pending NFIRS data for output generation).

## Problem Statement

Multifamily housing areas have **4.2x higher structure fire rates** than single-family areas:

| Housing Type | Structure Fires per 1,000 Units |
|--------------|--------------------------------|
| Multifamily (<25% SF) | 8.58 |
| Single-family (>75% SF) | 2.03 |

**Question:** Why? Is it arson, accidental causes, or building safety (sprinklers)?

## Data Sources

### Primary: National NFIRS (2018-2021)
- Texas FDID `WP801` (Austin area) - ~6,000 structure fire records
- Files: `fireincident.txt`, `basicincident.txt`

### Secondary: Existing Project Data
- `processed_data/response_areas_with_demographics.geojson` - housing typology, building age
- `processed_data/incidents_clean.csv` - AFD incidents 2022-2024

## Analysis 1: Data Extraction

**Goal:** Extract Austin fire incidents with full cause/sprinkler details.

**Join Strategy:**
1. Filter `basicincident.txt` for STATE="TX", FDID="WP801"
2. Join with `fireincident.txt` on STATE + FDID + INC_DATE + INC_NO
3. Extract key fields

**Key Fields:**

| Field | Description | Values |
|-------|-------------|--------|
| `PROP_USE` | Property use | 419=1-2 family, 429=multifamily, 439=boarding |
| `CAUSE_IGN` | Cause of ignition | 1=intentional, 2=unintentional, 3=equipment, 4=nature, U=undetermined |
| `HEAT_SOURC` | Heat source | 10-19=heating, 40-49=electrical, 61-63=smoking |
| `AREA_ORIG` | Area of origin | 21=bedroom, 24=kitchen, 51=mechanical |
| `AES_PRES` | Sprinkler present | Y/N/U |
| `AES_OPER` | Sprinkler operated | Y/N/U |
| `FIRE_SPRD` | Fire spread | 1=object, 2=room, 3=floor, 4=building |
| `PROP_LOSS` | Property loss | Dollar amount |

**Output:** `processed_data/nfirs_austin_detailed.csv`

## Analysis 2: Cause of Ignition by Housing Type

**Goal:** Determine what's driving higher multifamily fire rates.

### 2a. Cause Distribution
Cross-tabulate `CAUSE_IGN` by `PROP_USE`:

```
                    Single-Family    Multifamily    Ratio
Intentional (1)         X%              Y%          Y/X
Unintentional (2)       X%              Y%          Y/X
Equipment (3)           X%              Y%          Y/X
Undetermined (U)        X%              Y%          Y/X
```

**Interpretation:**
- High intentional ratio → arson is a driver
- High unintentional ratio → lifestyle factors (cooking, smoking)
- High equipment ratio → building infrastructure issues

### 2b. Heat Source Breakdown
Group `HEAT_SOURC` codes:

| Category | Codes | Examples |
|----------|-------|----------|
| Cooking | 12-15 | Stove, oven, grill, deep fryer |
| Heating | 10-11, 13 | Furnace, space heater, fireplace |
| Electrical | 40-49 | Wiring, appliances, lighting |
| Smoking | 61-63 | Cigarettes, pipes, matches |
| Other | All others | Open flame, chemical, etc. |

### 2c. Area of Origin
Group `AREA_ORIG` codes:

| Area | Codes | Significance |
|------|-------|--------------|
| Kitchen | 24 | Cooking fires |
| Bedroom | 21 | Smoking, electrical |
| Living room | 22 | Heating, electrical |
| Mechanical | 51-53 | Equipment failure |
| Exterior | 90s | Arson access point |

**Outputs:**
- `outputs/cause_by_housing_type.csv`
- `outputs/heat_source_by_housing.csv`
- `outputs/area_origin_by_housing.csv`
- `outputs/chart_cause_comparison.png`

## Analysis 3: Sprinkler & Building Age Effect

**Goal:** Quantify impact of Austin's 2006 sprinkler code.

### Background
- 2006: Austin adopted residential sprinkler requirement
- Post-2010 buildings should have sprinklers (construction lag)
- Current data shows 141% higher fire rates in older buildings

### 3a. Sprinkler Presence by Era

Cross-tabulate `AES_PRES` by building age:

```
                    Pre-2010    Post-2010
Sprinkler Present      X%          Y%
No Sprinkler           X%          Y%
```

### 3b. Sprinkler Effectiveness

When sprinklers present (`AES_PRES=Y`):
- Operation rate: % where `AES_OPER=Y`
- Fire containment: `FIRE_SPRD` distribution (object vs room vs building)
- Property loss: Average `PROP_LOSS` comparison

### 3c. Housing Type x Building Age x Sprinkler Matrix

Key analysis combining all factors:

```
                          Sprinkler Present    No Sprinkler
Single-Family Pre-2010         A                    B
Single-Family Post-2010        C                    D
Multifamily Pre-2010           E                    F
Multifamily Post-2010          G                    H
```

**Hypothesis to test:**
> "Multifamily has higher fire rates partly because older multifamily stock lacks sprinklers. Newer multifamily (post-2006) with sprinklers should have comparable or lower rates than single-family."

**Outputs:**
- `outputs/sprinkler_analysis.csv`
- `outputs/sprinkler_by_housing_age.csv`
- `outputs/chart_sprinkler_effect.png`
- `outputs/chart_housing_age_sprinkler_matrix.png`

## Implementation Plan

All steps implemented in `06_nfirs_cause_analysis.py`:

### Step 1: Extract NFIRS Data ✅
- Parses `fireincident.txt`, `basicincident.txt`, and `structurefire.txt` for TX/WP801
- Joins on incident key fields (STATE + FDID + INC_DATE + INC_NO + EXP_NO)

### Step 2: Code Lookups ✅
- Maps `CAUSE_IGN`, `HEAT_SOURC`, `AREA_ORIG`, `PROP_USE` codes to labels
- Grouped into readable categories

### Step 3: Cause Analysis ✅
- Aggregated by housing type (PROP_USE 419 vs 429)
- Outputs: `cause_by_housing_type.csv`, `heat_source_by_housing.csv`, `area_origin_by_housing.csv`
- Charts: `chart_cause_comparison.png`, `chart_heat_source_comparison.png`

### Step 4: Sprinkler Analysis ✅
- Cross-tabulated sprinkler presence by housing type
- Output: `sprinkler_by_housing.csv`
- **Finding:** Low reporting quality — no "present" records in Austin NFIRS data

### Step 5: Building Height Analysis ✅ (code complete)
- Added `structurefire.txt` loading for BLDG_ABOVE field
- `analyze_building_height()` categorizes by 1-2, 3-4, 5-7, 8+ stories
- `create_building_height_chart()` generates two-panel visualization
- Outputs pending NFIRS data download

## Actual Findings

1. **Cause:** Unintentional causes dominate in both types — 76% in MF vs 64% in SF. Cooking (24%) and smoking (18%) are the top MF heat sources. Arson is actually lower in MF (6%) than SF (10%).

2. **Sprinklers:** NFIRS sprinkler reporting for Austin is too sparse to draw conclusions — no "present" records. The area-level building age analysis (141% higher rates in older stock) remains the best proxy for sprinkler code effectiveness.

3. **Key insight:** The 4x gap is driven by behavioral factors (cooking, smoking) amplified by density, not by building deficiency or arson. This supports prevention-focused interventions over infrastructure-only responses.

## Out of Scope

- Police/crime data integration
- Prosecution outcomes
- Arrest rates
- Neighborhood crime correlation
