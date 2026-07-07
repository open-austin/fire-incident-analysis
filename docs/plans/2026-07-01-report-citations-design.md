# Design: Scholarly citations for the Fire-Fiscal Master Report

**Date:** 2026-07-01 · **Branch:** `report-citations` · **Status:** approved

## Goal

Add citation-grade sourcing to `docs/FIRE_FISCAL_FULL_REPORT.md`: every measure and
external source cited at first mention via footnote, plus a full bibliography.

## Decisions (validated with Chase)

1. **Scope:** full report only. The fiscal report and policy brief link to it.
2. **Style:** Chicago notes-bibliography. Full note on first cite, shortened after,
   alphabetized bibliography.
3. **Verification:** every source's URL/title/vintage confirmed on the live web
   before citing (access date 2026-07-01). Unreachable → flagged, not cited blind.
4. **Footnotes:** one unified stream. New citation notes share the existing
   `[^label]` markdown-footnote system (the PDF build already renders it). Where a
   code-pointer footnote already sits at the right spot (`[^rate]`, `[^budget]`,
   `[^tcad]`…), the source citation merges into it — citation first, code pointer
   after — rather than duplicating.

## What gets cited (first mention → source)

**Concepts / measures**
- Value per acre, value per road-mile → Marohn / Strong Towns; Minicozzi / Urban3
- Market vs. assessed value; roll certification → Tex. Property Tax Code
- Effective tax rate (2.1% blend) → published FY2024-25 jurisdiction rates
- Coverage vs. demand; ~90% standby → FireRescue1 (Knight; budget breakdown), NFPA 1710
- H3 hexagons → Uber H3 documentation

**Data**
- TCAD 2025 certified roll (PACS `PROP.TXT`) + Travis parcel GIS (2023 Land Database)
- WCAD parcels (Williamson County GIS MapServer); Hays CAD parcels (FeatureServer)
- Texas Comptroller Property Value Study / Appraisal District Ratio Study
- AFD Fire Incidents 2022–2024 (Austin Open Data v5hh-nyr8)
- City of Austin `LOCATION_fire_stations`, `BOUNDARIES_afd_response_areas`
- Census TIGER/Line 2023 roads (MTFCC S1100 exclusion); CB places 2023; ACS 2022
  5-yr B01003 / B25024 / B25034

**Dollar constants**
- City of Austin FY2024-25 adopted budget ($5.9B all-funds / $1.4B GF / AFD ≈$264M)
  → official budget document, KUT, ATXtoday

## Mechanics

- §14 becomes **References**: alphabetized Chicago bibliography + the existing
  cross-links paragraph.
- Verification fan-out: three parallel agents (Texas property/tax · Austin fire/budget ·
  Census/geodata/concepts), each returning canonical URL, title, publisher, date,
  and a ready bibliography entry per source.
- After edits: confirm footnote syntax renders in the PDF build path.
