# Claude Code Instructions

## Skills-First Workflow (Superpowers)

Before responding to any user message, check if any available skill applies (even at 1% relevance) and invoke it via the Skill tool BEFORE taking action or asking clarifying questions.

Priority order:
1. Process skills first (brainstorming, debugging) - these determine HOW to approach the task
2. Implementation skills second - these guide execution

## Data provenance for every claim

**No number ships without its provenance.** Any quantitative claim in a deliverable — report, handout, README, issue/PR comment, chart caption — must be traceable to (1) its source data (file + columns), (2) the exact formula/transformation (including filters, weights, and null handling), and (3) a reproduction step (copy-paste snippet or `notebook.ipynb → cell N` / `script.py:line`). A figure a reader can't trace is a claim they can't check; don't publish it.

When you add or change a number in a deliverable, add or update its entry in `docs/METHODS.md` (the provenance ledger + standard) and leave a short pointer to it in the deliverable. Compute numbers in a notebook/script, never by hand. Prefer numbers that `notebooks/validation.ipynb` re-derives on every run.
