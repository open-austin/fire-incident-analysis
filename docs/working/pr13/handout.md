# Four open questions from the PR13 review — discussion handout

A neutral, data-backed guide for working through the review feedback together. Each item states the suggestion, what the report's own data shows, and the choices on the table.

- **Report:** Fire-Fiscal Master (PR #13) · **Review:** Issue #14 · **Figures:** from repo outputs, 2026-07-14
- **How to use:** take the four items in order. Read the finding, weigh the two directions, mark a decision.
- Figures are measurements from the project's own data; named suggestions paraphrase the written review. The decisions are the group's to make. A print-ready version is at [`handout.html`](handout.html).

---

## A — Vehicle & trash fires: keep or remove?

**Suggestion (Eric).** Consider removing vehicle, outdoor, and trash fires — possibly less relevant to the fire-service-vs-property question, and possibly affecting apparent demand in denser areas.

**What the data shows — weighted fire demand by category:**

| Category | Incidents | Weighted | % of demand |
|---|--:|--:|--:|
| Structure fire (non-confined) | 3,176 | 31,760 | 48.7% |
| Structure fire (confined) | 2,517 | 12,585 | 19.3% |
| Trash / dumpster | 9,626 | 9,626 | 14.8% |
| Outdoor / vegetation | 3,404 | 6,808 | 10.4% |
| Vehicle | 2,190 | 4,380 | 6.7% |
| Other | 7 | 7 | 0.0% |
| **Vehicle + outdoor + trash** | **15,220** | **20,814** | **31.9%** |

These are **32% of weighted demand** but **73% of all incident records** — the weighted share is lower because the model already down-weights them by severity (trash = 1 vs. structure = 10). By area type:

| Area type | Non-structure = % of its demand | Share of total (all) | Share (structure-only) |
|---|--:|--:|--:|
| urban_core | 23.9% | 3.4% | 3.8% |
| inner_suburban | 31.4% | 74.5% | 75.3% |
| outer_suburban | 36.4% | 21.4% | 20.0% |

Non-structure fires are a larger share of demand in the outer suburbs (36.4%) than the urban core (23.9%). Removing them shifts the urban core's share up slightly (3.4→3.8%) and the outer suburbs' down (21.4→20.0%).

**Decision**
- [ ] **Keep, with a note** — real calls, already severity-weighted; document that they skew outer/suburban.
- [ ] **Remove** — structure-fire-only measure; note that it drops ~73% of incident records.

Decided: ____________________

---

## B — Road-mile cost model (§5.3 / §6.2): reframe or cut?

**Suggestion (Eric).** Reconsider §6.2 ("the cost model changes the verdict"): the framing may read as selecting a cost basis for its result, or imply a road-focused argument the report is not making.

**What the data shows** (46 cities + unincorporated county):
- **35 of 46 cities (76%)** keep the same verdict under both cost models; **11** change sign. Correlation between models: **r = 0.85**.
- Unincorporated county: **−16,098** (land basis) vs. **−15,999** (road basis) per acre — nearly identical. The largest single result does not depend on the cost model.

| Change to net drain (road basis) | Change to contributor (road basis) |
|---|---|
| Buda, Wells Branch, Georgetown, Kyle | Bee Cave, Shady Hollow, Point Venture, Woodcreek, Liberty Hill, Manor, Elgin |

The overall conclusion is stable across both models; the cases that change are borderline and fall in both directions.

**Decision**
- [ ] **Reframe as a sensitivity check** — lead with the agreement statistics; present the 11 as borderline cases; retitle away from "changes the verdict."
- [ ] **Cut from the presentation version** — shorter, at the cost of the robustness result.

Decided: ____________________

---

## C — Revenue vs. property value (§2.1–2.2)

**Suggestion (Eric).** The report uses both revenue and value; consider standardizing. A follow-on idea: using revenue could reflect the tax exemptions single-family homes receive.

**What the data shows.** The model computes `revenue = value × 0.021` using one uniform effective tax rate applied everywhere. With a constant multiplier, value-per-acre and revenue-per-acre produce **identical rankings** — the label does not change the numbers. Reflecting an exemption effect would require **per-parcel taxable value** (after homestead caps and exemptions), currently populated for **Travis County only**.

Two separate items: (1) a terminology inconsistency — a one-sentence wording fix; (2) a per-parcel taxable-value analysis — new work, Travis-only for now.

**Decision**
- [ ] **Clarify wording now** — state that revenue is value × a uniform rate, and use one term consistently.
- [ ] **Scope taxable-value analysis later** — as its own task; note the Travis-only limitation.

Decided: ____________________

---

## D — §2.4 "Fiscal productivity & break-even": revise or cut?

**Suggestion (Eric).** The subsection may not add value and reads as clunky.

**What it does.** §2.4 introduces the break-even frame the rest of the report relies on: an area pays in (revenue, rising with value) and costs to serve (roughly flat per acre); where those cross is break-even, and later sections (§6.2, §6.3, the fire analysis) build on that frame.

**Decision**
- [ ] **Revise** — compress to a short "how to read this report" callout plus the break-even diagram.
- [ ] **Cut** — remove the section; later sections then rely on the reader inferring the frame.

Decided: ____________________

---

## At a glance

| Item | What the data shows | On the table |
|---|---|---|
| A | 32% of weighted demand, 73% of records; proportionally more outer-suburban than urban | Keep with a note · Remove |
| B | 76% verdict agreement, r = 0.85, largest area near-identical under both models | Reframe as sensitivity check · Cut |
| C | Uniform rate → identical rankings; exemption effect needs per-parcel taxable value (Travis-only) | Clarify wording · Scope later |
| D | Introduces the break-even frame used throughout the report | Revise to a callout · Cut |

---

## Methods & provenance

Every figure above is traceable — source data, formula, and a reproduction step are recorded in **[`docs/METHODS.md`](../../METHODS.md)**. Quick map:

| Figure (this handout) | Provenance entry |
|---|---|
| §A weighted demand by category (48.7% … 31.9%; 65,166 total) | METHODS → *Weighted fire demand by category* |
| §A non-structure share by area type (23.9 / 31.4 / 36.4%) | METHODS → *Non-structure demand by area type* |
| §B 76% agreement, r = 0.85, −16,098 vs −15,999 | METHODS → *Cost-model verdict agreement* |
| §C `revenue = value × 0.021`, identical rankings | METHODS → *Revenue definition* |

*Figures computed from the project's own outputs on 2026-07-14. Named suggestions paraphrase the written PR13 review (Issue #14).*
