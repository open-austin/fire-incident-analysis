# Townhome Sprinkler Safety Analysis Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Analyze fire incident rates in townhomes by construction era to compare life safety outcomes between sprinkler-protected buildings and those relying on two-hour fire separations, informing fire code policy discussions.

**Architecture:** Filter existing incident data to townhome-specific fires, integrate TCAD parcel data for precise year-built classification, categorize buildings by code cohorts (pre-2019: 2hr wall no spkr; 2019-2021: 2hr wall or 1hr & spkr; post-2021: spkrs), calculate incident rates by cohort, and compare with national NFIRS data if local sample sizes are insufficient.

**Tech Stack:** Python (pandas, geopandas), existing project data (AFD incidents, TCAD parcels), NFIRS national data.

---

### Task 1: Filter Incident Data to Townhomes

**Files:**
- Modify: `processed_data/incidents_with_parcels.csv` (filter to townhome incidents)
- Create: `processed_data/townhome_incidents.csv`

**Step 1: Identify townhome classification in parcel data**

Review TCAD parcel data structure to confirm how townhomes are classified (likely via zoning or building type fields). Check `07_parcel_join.py` for existing parcel integration.

**Step 2: Filter incidents to townhome parcels**

```python
import pandas as pd

# Load incidents with parcels
incidents = pd.read_csv('processed_data/incidents_with_parcels.csv')

# Filter to townhome parcels (adjust field name based on TCAD data)
townhome_incidents = incidents[incidents['building_type'] == 'townhome']  # Placeholder field

# Save filtered data
townhome_incidents.to_csv('processed_data/townhome_incidents.csv', index=False)
```

**Step 3: Validate filter results**

Check row count and sample records to ensure filtering captured townhome incidents correctly.

**Step 4: Commit**

```bash
git add processed_data/townhome_incidents.csv
git commit -m "feat: filter incidents to townhome parcels"
```

### Task 2: Classify Townhome Buildings by Code Cohorts

**Files:**
- Modify: `processed_data/townhome_incidents.csv` (add cohort classification)
- Create: `scripts/10_townhome_cohort_analysis.py`

**Step 1: Define cohort logic based on year built**

Create mapping:
- Pre-2019: '2hr_wall_no_spkr'
- 2019-2021: '2hr_wall_or_1hr_spkr'  
- Post-2021: 'sprinklers_required'

**Step 2: Add cohort column to townhome data**

```python
def classify_cohort(year_built):
    if year_built < 2019:
        return '2hr_wall_no_spkr'
    elif 2019 <= year_built <= 2021:
        return '2hr_wall_or_1hr_spkr'
    else:
        return 'sprinklers_required'

townhome_incidents['code_cohort'] = townhome_incidents['year_built'].apply(classify_cohort)
```

**Step 3: Validate cohort distribution**

Check counts by cohort to ensure reasonable distribution across years.

**Step 4: Commit**

```bash
git add scripts/10_townhome_cohort_analysis.py processed_data/townhome_incidents.csv
git commit -m "feat: classify townhome buildings by fire code cohorts"
```

### Task 3: Calculate Incident Rates by Cohort

**Files:**
- Modify: `scripts/10_townhome_cohort_analysis.py` (add rate calculations)
- Create: `outputs/townhome_rates_by_cohort.csv`

**Step 1: Group incidents by cohort and calculate rates**

```python
# Calculate incidents per 1,000 units by cohort
cohort_rates = townhome_incidents.groupby('code_cohort').agg({
    'incident_id': 'count',
    'total_units': 'sum'  # Assuming parcel data has unit count
}).reset_index()

cohort_rates['rate_per_1000_units'] = (cohort_rates['incident_id'] / cohort_rates['total_units']) * 1000
```

**Step 2: Include structure fire rates specifically**

Filter to structure fires and recalculate rates.

**Step 3: Save results**

```python
cohort_rates.to_csv('outputs/townhome_rates_by_cohort.csv', index=False)
```

**Step 4: Commit**

```bash
git add outputs/townhome_rates_by_cohort.csv scripts/10_townhome_cohort_analysis.py
git commit -m "feat: calculate fire incident rates by townhome code cohorts"
```

### Task 4: Assess Statistical Significance

**Files:**
- Modify: `scripts/10_townhome_cohort_analysis.py` (add statistical tests)
- Create: `outputs/townhome_statistical_tests.txt`

**Step 1: Perform ANOVA or chi-square test**

```python
from scipy import stats

# ANOVA on rates across cohorts
f_stat, p_value = stats.f_oneway(
    cohort_rates[cohort_rates['code_cohort'] == '2hr_wall_no_spkr']['rate_per_1000_units'],
    cohort_rates[cohort_rates['code_cohort'] == '2hr_wall_or_1hr_spkr']['rate_per_1000_units'], 
    cohort_rates[cohort_rates['code_cohort'] == 'sprinklers_required']['rate_per_1000_units']
)
```

**Step 2: Check sample sizes**

Ensure each cohort has sufficient incidents for meaningful analysis (aim for n>30 per group).

**Step 3: Document results**

Write test results to text file.

**Step 4: Commit**

```bash
git add outputs/townhome_statistical_tests.txt scripts/10_townhome_cohort_analysis.py
git commit -m "feat: add statistical significance tests for townhome cohorts"
```

### Task 5: Compare with National NFIRS Data

**Files:**
- Create: `scripts/11_national_townhome_comparison.py`
- Create: `outputs/national_townhome_rates.csv`

**Step 1: Download NFIRS townhome data**

Use existing NFIRS script as template to filter national data to townhomes.

**Step 2: Calculate national rates by similar cohorts**

Apply same cohort logic to national data.

**Step 3: Compare Austin vs national rates**

Create side-by-side comparison table.

**Step 4: Commit**

```bash
git add scripts/11_national_townhome_comparison.py outputs/national_townhome_rates.csv
git commit -m "feat: compare Austin townhome rates with national NFIRS data"
```

### Task 6: Update Research Plan and Policy Brief

**Files:**
- Modify: `RESEARCH_PLAN.md` (add townhome findings section)
- Modify: `docs/POLICY_BRIEF.md` (add townhome safety implications)

**Step 1: Add townhome analysis section to research plan**

Document methodology, findings, and limitations.

**Step 2: Update policy brief**

Include implications for sprinkler requirements vs fire separations.

**Step 3: Generate visualizations**

Create charts comparing cohort rates.

**Step 4: Commit**

```bash
git add RESEARCH_PLAN.md docs/POLICY_BRIEF.md
git commit -m "docs: update research plan and policy brief with townhome sprinkler analysis"
```

### Task 7: Connect with Additional Experts

**Files:**
- Modify: `RESEARCH_PLAN.md` (add contacts section)

**Step 1: Document Chris Gannon contact**

Add to references/contacts section.

**Step 2: Note Stephen Smith inquiry**

Add as potential contact for fire investigation data.

**Step 3: Update stakeholder list**

Include AIA Austin and fire code board connections.

**Step 4: Commit**

```bash
git add RESEARCH_PLAN.md
git commit -m "docs: add fire code expert contacts to research plan"
```