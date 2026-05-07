# Market Risk BI Training — Finalization Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the 20 outline-only modules (03–22), finish the glossary, and add diagrams + code samples so the site is a practitioner-grade beginner-to-pro training.

**Architecture:** Sequential drafting in nav order (03 → 22). Claude drafts each module to 600–1000 lines; user reviews/edits. Each module includes: structured prose, ≥1 mermaid diagram, ≥2 worked code examples (SQL or Python), 3–5 exercises with solutions in a collapsed `<details>` block. Glossary and asset polish happen after content is in place. Commit after each module is reviewed.

**Tech Stack:** MkDocs Material 9.7, pymdown-extensions (admonitions, superfences, tabbed, tasklist, arithmatex/MathJax), mermaid for diagrams, fenced SQL/Python code blocks.

**Audit baseline (2026-05-07):**
- Modules 01, 02 — DRAFT (~140 / ~250 lines, no code/exercises yet)
- Modules 03–22 — SKELETON (outline + "*To be expanded*" markers only)
- Glossary — DRAFT, terms A–V, missing X–Z and ~20 cross-referenced terms
- `docs/assets/` — empty, no diagrams or images committed
- No code samples, no exercises anywhere

---

## File Structure

```
docs/
├── index.md                  # Landing — refresh after content is in
├── curriculum.md             # Refresh stats coverage map after Phases 3–4 done
├── glossary.md               # Complete A–Z + add ~20 missing terms
├── _template.md              # NEW — canonical module template
├── assets/                   # NEW content — diagrams as committed .svg/.png if generated; otherwise inline mermaid
├── code-samples/             # NEW — runnable .sql / .py files referenced by modules via pymdownx.snippets
│   ├── README.md
│   ├── sql/
│   └── python/
└── modules/
    ├── 01-…  → polish pass (add diagram + 1 example + 3 exercises)
    ├── 02-…  → polish pass (add 1 example + 3 exercises; diagrams already present)
    ├── 03-…21  → full draft (per-task spec below)
    └── 22-capstone.md  → full draft (project brief + rubric + reference solution outline)
```

---

## Module template (canonical structure)

Every module 03–22 follows this section order. Deviations only when the topic genuinely doesn't support a section (note in the task).

1. **Learning objectives** — bullet list, 4–6 items, measurable verbs
2. **Why this matters** — 2–3 paragraphs connecting topic to BI/data work in market risk
3. **Core concepts** — main body, sub-headed by concept, with diagrams inline
4. **Worked examples** — ≥2 examples with code (SQL/Python) or step-by-step calculation
5. **Common pitfalls** — admonition block, 3–5 items
6. **Exercises** — 3–5 questions, mix of conceptual and applied; solutions in `??? note "Solution"` collapsed blocks
7. **Further reading** — 3–6 links/refs (papers, books, regulator docs)
8. **Recap** — 5-bullet "you should now be able to…" summary

Acceptance criteria per module: 600–1000 lines, ≥1 mermaid diagram, ≥2 code examples, 3–5 exercises with solutions, no `*To be expanded*` markers remaining.

---

## Phase 0 — Infrastructure

### Task 0: Create module template and code-samples scaffold

**Files:**
- Create: `docs/_template.md`
- Create: `docs/code-samples/README.md`
- Create: `docs/code-samples/sql/.gitkeep`, `docs/code-samples/python/.gitkeep`
- Create: `docs/assets/.gitkeep`
- Modify: `mkdocs.yml` (exclude `_template.md` from nav by leaving it out; nothing to change since it's not in nav)

- [ ] **Step 1:** Write `docs/_template.md` containing the 8-section canonical structure with placeholder examples of each block (admonition, mermaid, fenced SQL, exercise + collapsed solution). This is a reference document, not nav-linked.
- [ ] **Step 2:** Write `docs/code-samples/README.md` explaining: how snippets are referenced via `--8<--` (pymdownx.snippets), naming convention (`<module-num>-<short-name>.sql/.py`), and that every snippet must run standalone (or have a header comment explaining required setup).
- [ ] **Step 3:** Verify mkdocs builds — run `mkdocs build` locally and check output.
- [ ] **Step 4:** Commit.
  ```bash
  git add docs/_template.md docs/code-samples/ docs/assets/
  git commit -m "Add module template and code-samples scaffold"
  ```

---

## Phase 1 — Module drafting (sequential, one per task)

Format for each task: target sections beyond the canonical template, the required diagrams, the required examples, and the required exercises.

---

### Task 1: Module 03 — Trade Lifecycle

**File:** `docs/modules/03-trade-lifecycle.md`

**Required content (beyond canonical template):**
- Front-to-back lifecycle stages: pre-trade → execution → confirmation → settlement → lifecycle events → maturity/expiry/termination.
- Status taxonomy (NEW / AMENDED / CANCELLED / SETTLED / TERMINATED) with state-transition rules.
- Why amendments and cancellations matter for risk reporting (point-in-time vs. as-of).

**Diagrams (mermaid):**
- State diagram of trade statuses and allowed transitions.
- Sequence diagram showing F→M→B information flow for a new trade.

**Code examples:**
1. SQL: query that returns the as-of state of a trade given an `event_log` table with `valid_from`/`valid_to`.
2. SQL: detect "torn trades" — booked in front office but missing in back office at end of day.

**Exercises (3–5):** include one applied question of the form "given this event log, what is the trade's state on date X?"

- [ ] Draft the file (~700 lines).
- [ ] Run `mkdocs build`; review locally; user reviews/edits.
- [ ] Commit: `Draft Module 03 — Trade Lifecycle`.

---

### Task 2: Module 04 — Financial Instruments

**File:** `docs/modules/04-financial-instruments.md`

**Required content:**
- Asset classes: Rates, FX, Credit, Equity, Commodity — for each: typical instruments, key risk drivers, typical sensitivities.
- Cash vs. derivative; linear vs. non-linear; vanilla vs. exotic.
- Instrument identifiers (ISIN, CUSIP, RIC, internal IDs) and why instrument master is its own dimension.
- Pricing model families at a glance (no math derivations — that's Phase 3).

**Diagrams:**
- Tree/taxonomy diagram of asset classes → instrument types → example products.
- Table (markdown) mapping instrument family to risk drivers.

**Code examples:**
1. Python: function classifying an instrument by `asset_class` + `payoff_type` returning its dominant risk drivers.
2. SQL: count instruments by asset class and product type from a sample instrument master.

**Exercises:** include "given instrument X, which sensitivities would you expect to see?"

- [ ] Draft (~800 lines), build, review, commit: `Draft Module 04 — Financial Instruments`.

---

### Task 3: Module 05 — Dimensional Modeling

**File:** `docs/modules/05-dimensional-modeling.md`

**Required content:**
- Star vs. snowflake; conformed dimensions; bus matrix.
- SCD types 0/1/2/3/6 with when to use each in market risk.
- Surrogate vs. natural keys; junk dimensions; degenerate dimensions; role-playing dimensions (e.g. trade date vs. settle date both reference Date dim).
- Why dimensional modeling fits market risk reporting (BI tools, drill paths, slice/dice).

**Diagrams:**
- Star schema diagram for a sample risk-measure fact with 5–6 dimensions.
- Bus matrix (markdown table) showing facts × dimensions.

**Code examples:**
1. SQL: SCD Type 2 upsert pattern (MERGE) for a Counterparty dimension.
2. SQL: as-of join — fact joined to SCD2 dim using `valid_from`/`valid_to`.

**Exercises:** include "design the dimensions for an FX-spot trade fact" and "spot the SCD-type mistake in this schema."

- [ ] Draft (~900 lines), build, review, commit: `Draft Module 05 — Dimensional Modeling`.

---

### Task 4: Module 06 — Core Dimensions

**File:** `docs/modules/06-core-dimensions.md`

**Required content:**
- Walk through the canonical risk-reporting dimensions: Date, Trade, Instrument, Counterparty, Book/Desk, Legal Entity, Currency, Risk Factor, Scenario, Source System.
- For each: grain, candidate keys, SCD type, key attributes, common gotchas.
- Conformance across regions/desks (US trade-date vs. APAC trade-date is a real example).

**Diagrams:**
- ER diagram (mermaid) of core dimensions and their relationships.

**Code examples:**
1. SQL: Date dimension generation script (calendar with trading-day flags per region).
2. SQL: hierarchical Book/Desk/Legal-Entity rollup query.

**Exercises:** include "given two desks merging, how do you handle the SCD2 history?"

- [ ] Draft (~800 lines), build, review, commit: `Draft Module 06 — Core Dimensions`.

---

### Task 5: Module 07 — Fact Tables

**File:** `docs/modules/07-fact-tables.md`

**Required content:**
- Transactional / periodic-snapshot / accumulating-snapshot fact types — and which fits which risk measure.
- Grain declaration; additive / semi-additive / non-additive measures (VaR is non-additive — preview of Module 12).
- Late-arriving facts; restatements; the difference between fact-version (bitemporal) and SCD2 on dimensions.
- Fact-table design patterns specific to risk: sensitivities fact, VaR fact, P&L fact, position fact.

**Diagrams:**
- Mermaid showing the three fact types side-by-side with example grain.

**Code examples:**
1. SQL: insert pattern for a periodic-snapshot end-of-day position fact (with bitemporal columns).
2. SQL: query that handles late-arriving fact rows by `as_of_date` vs. `business_date`.

**Exercises:** include "what's the grain of this fact?" and "is this measure additive?"

- [ ] Draft (~800 lines), build, review, commit: `Draft Module 07 — Fact Tables`.

---

### Task 6: Module 08 — Sensitivities

**File:** `docs/modules/08-sensitivities.md`

**Required content:**
- First-order Greeks: Delta, Vega, Rho, Theta — and bucketed variants (delta-by-tenor, vega surface).
- Second-order: Gamma, cross-gamma, vanna, volga.
- DV01, CS01, PV01 conventions.
- How sensitivities flow from pricing engines to risk warehouses; storage shapes (long format vs. wide format).
- Bumping methodology (parallel vs. bucketed, absolute vs. relative).

**Diagrams:**
- Mermaid diagram: pricing engine → sensitivities calc → risk fact table.

**Code examples:**
1. Python: numerical delta of a vanilla option via central difference, with a brief Black–Scholes pricer.
2. SQL: aggregate bucketed delta to a parallel delta by summing across tenors.

**Exercises:** include "given these tenor buckets and DV01s, compute parallel DV01" and a question on cross-gamma.

- [ ] Draft (~900 lines), build, review, commit: `Draft Module 08 — Sensitivities`.

---

### Task 7: Module 09 — Value at Risk (CRITICAL)

**File:** `docs/modules/09-value-at-risk.md`

**Required content:**
- Definition; horizon; confidence level; the historical / parametric / Monte Carlo approaches with full pros/cons.
- Expected Shortfall (CVaR/ES) and why FRTB moved away from VaR.
- Backtesting: traffic-light (Basel) framework; Kupiec, Christoffersen tests.
- Stressed VaR; incremental VaR; component VaR; marginal VaR.
- Why VaR is non-additive across portfolios — set up Module 12.

**Diagrams:**
- Histogram diagram showing P&L distribution with VaR and ES marked.
- Mermaid flow: positions → risk factors → scenarios → P&L vector → VaR.

**Code examples:**
1. Python: 1-day 99% historical VaR over a returns series, with ES at the same level.
2. Python: parametric VaR for a 2-asset portfolio via Cholesky on the covariance matrix.

**Exercises:** ≥5 — include backtesting interpretation and one "why does VaR_A + VaR_B ≠ VaR_(A+B)?"

- [ ] Draft (~1000 lines — this is the flagship module), build, review, commit: `Draft Module 09 — Value at Risk`.

---

### Task 8: Module 10 — Stress Testing

**File:** `docs/modules/10-stress-testing.md`

**Required content:**
- Historical scenarios (1987, 2008, 2020); hypothetical scenarios; reverse stress tests.
- Sensitivity-based vs. full-revaluation stress.
- Regulatory stress programs at a glance (CCAR/DFAST, EBA, BoE) — high-level only.
- Storing stress results: Scenario dimension + stress fact.

**Diagrams:**
- Mermaid: scenario library → shock vector → revaluation → stress P&L fact.

**Code examples:**
1. Python: apply a shock vector to a sensitivities table and compute stressed P&L.
2. SQL: store and query stress results by scenario + book.

**Exercises:** include reverse-stress reasoning and one full-reval vs. sensitivity-based comparison.

- [ ] Draft (~800 lines), build, review, commit: `Draft Module 10 — Stress Testing`.

---

### Task 9: Module 11 — Market Data

**File:** `docs/modules/11-market-data.md`

**Required content:**
- Snapshot structure: curves, surfaces, fixings, FX rates, equity prices.
- EOD vs. intraday; closing conventions per region; market-data hierarchies (vendor → cleansed → official).
- Proxy and bootstrap; missing data handling; outlier detection.
- Why market-data lineage is critical for P&L attribution and audit.

**Diagrams:**
- Mermaid: vendor sources → cleansing → official curves → consumers.

**Code examples:**
1. Python: bootstrap a zero curve from par swap rates (simple, no calibration to discount factors edge cases).
2. SQL: query that joins trades to the official EOD market-data snapshot for a given business date.

**Exercises:** include "spot the market-data error in this curve" and a fixings-vs-forecast question.

- [ ] Draft (~800 lines), build, review, commit: `Draft Module 11 — Market Data`.

---

### Task 10: Module 12 — Aggregation & Additivity (CRITICAL)

**File:** `docs/modules/12-aggregation-additivity.md`

**Required content:**
- Why sums lie: VaR, ES, capital are not additive; sensitivities are additive (mostly); P&L is additive.
- Diversification benefit; sub-additivity; coherent risk measures (Artzner et al.).
- Storage implications: store the *components needed to re-aggregate*, not the aggregates.
- "Pre-aggregated reporting tables are a trap" — anti-pattern preview.

**Diagrams:**
- Mermaid showing what aggregates safely vs. what doesn't, by measure type.

**Code examples:**
1. Python: demonstrate non-additivity of historical VaR with a 2-portfolio example.
2. SQL: a query that incorrectly sums VaR (with a comment showing why), then the correct re-aggregation pattern.

**Exercises:** include "which of these measures can you SUM in a BI tool?" matrix.

- [ ] Draft (~900 lines — flagship), build, review, commit: `Draft Module 12 — Aggregation & Additivity`.

---

### Task 11: Module 13 — Time & Bitemporality (CRITICAL)

**File:** `docs/modules/13-time-bitemporality.md`

**Required content:**
- Two timelines: business date (when something is true in the world) vs. system/as-of date (when we knew it).
- Bitemporal modeling pattern: `business_from`/`business_to` × `as_of_from`/`as_of_to`.
- Restatements, corrections, retro-fixes — and why audit/regulators demand bitemporal storage.
- "Latest" is ambiguous: as-of-latest vs. business-latest vs. report-latest.

**Diagrams:**
- 2D plot (mermaid or markdown ASCII) of the bitemporal grid with labeled regions.

**Code examples:**
1. SQL: bitemporal upsert (correct an old business-date fact without losing the prior version).
2. SQL: as-of query that reproduces a report exactly as it was on a past system date.

**Exercises:** include "given this bitemporal table, what would the report show as of date X but for business date Y?"

- [ ] Draft (~900 lines — flagship), build, review, commit: `Draft Module 13 — Time & Bitemporality`.

---

### Task 12: Module 14 — P&L Attribution

**File:** `docs/modules/14-pnl-attribution.md`

**Required content:**
- Clean P&L vs. dirty P&L; risk-theoretical P&L vs. hypothetical P&L (FRTB PLA).
- Taylor-series decomposition: ΔP ≈ Δ·dS + ½Γ·dS² + V·dσ + θ·dt + …
- Unexplained P&L: causes (model error, missing risk factors, market-data errors).
- PLA test under FRTB at a high level.

**Diagrams:**
- Mermaid waterfall: total P&L → delta P&L → vega P&L → theta P&L → unexplained.

**Code examples:**
1. Python: Taylor-series P&L attribution for a single option position given Greeks and market moves.
2. SQL: compute aggregate attributed P&L by Greek across a book.

**Exercises:** include a worked attribution from raw data and one "diagnose the source of unexplained P&L."

- [ ] Draft (~800 lines), build, review, commit: `Draft Module 14 — P&L Attribution`.

---

### Task 13: Module 15 — Data Quality

**File:** `docs/modules/15-data-quality.md`

**Required content:**
- DQ dimensions: completeness, accuracy, consistency, timeliness, validity, uniqueness.
- Reconciliation patterns (front-to-back, source-vs-warehouse, totals tie-out).
- DQ checks at ingestion vs. inside the warehouse (dbt tests, Great Expectations style).
- Severity tiers and what should block the EOD run.

**Diagrams:**
- Mermaid: DQ check stages across the pipeline (ingest → stage → mart → reporting).

**Code examples:**
1. SQL: reconciliation query — total notional in source vs. warehouse with a configurable tolerance.
2. SQL: a reusable DQ-check pattern (template view that returns rows that violated a rule).

**Exercises:** include "design DQ checks for a sensitivities feed" and "what severity is a missing FX rate?"

- [ ] Draft (~800 lines), build, review, commit: `Draft Module 15 — Data Quality`.

---

### Task 14: Module 16 — Lineage & Auditability

**File:** `docs/modules/16-lineage-auditability.md`

**Required content:**
- Column-level vs. table-level lineage; parsing-based vs. log-based lineage.
- What auditors and regulators expect (BCBS 239 principles, especially data lineage and traceability).
- Reproducibility: bitemporality + lineage = "show me the report exactly as it was."
- Tools landscape (open-source: OpenLineage, Marquez; commercial: Atlan, Collibra) — overview only.

**Diagrams:**
- Mermaid: lineage graph from raw feed → mart → report.

**Code examples:**
1. SQL: query the lineage table to find every downstream artifact of a source column.
2. Python: parse a SQL file and emit OpenLineage-style table-level edges (very small example).

**Exercises:** include a BCBS 239 mapping exercise.

- [ ] Draft (~700 lines), build, review, commit: `Draft Module 16 — Lineage & Auditability`.

---

### Task 15: Module 17 — Performance & Materialization

**File:** `docs/modules/17-performance-materialization.md`

**Required content:**
- Materialization strategies: view, table, incremental, snapshot.
- Partitioning, clustering, sort keys; warehouse-specific patterns at a glance (Snowflake, BigQuery, Redshift).
- Trade-offs: storage cost vs. compute cost; freshness vs. cost.
- Anti-pattern: materializing aggregates of non-additive measures (link back to Module 12).

**Diagrams:**
- Decision tree (mermaid) for "when do I make this incremental?"

**Code examples:**
1. SQL: incremental dbt-style model for a sensitivities fact with partition pruning.
2. SQL: clustering/partitioning DDL for a daily-grain risk fact.

**Exercises:** include sizing-style estimation for storage and runtime.

- [ ] Draft (~700 lines), build, review, commit: `Draft Module 17 — Performance & Materialization`.

---

### Task 16: Module 18 — Architecture Patterns

**File:** `docs/modules/18-architecture-patterns.md`

**Required content:**
- Lambda vs. Kappa vs. medallion (bronze/silver/gold).
- ELT vs. ETL in the modern stack.
- Where the risk warehouse sits relative to the data lake/lakehouse.
- Reference architecture for a market-risk BI stack: ingestion → conformance → marts → reporting.

**Diagrams:**
- Reference architecture mermaid diagram.

**Code examples:**
1. SQL: a "silver-layer" conformance view standardizing two source-system feeds.
2. Pseudo-code/yaml: a dbt project structure for the medallion model.

**Exercises:** include "given these constraints, sketch the architecture."

- [ ] Draft (~700 lines), build, review, commit: `Draft Module 18 — Architecture Patterns`.

---

### Task 17: Module 19 — Regulatory Context

**File:** `docs/modules/19-regulatory-context.md`

**Required content:**
- Basel III/IV market risk; FRTB SA vs. IMA; the IMCC and DRC.
- BCBS 239 (data risk principles) — most relevant for BI/data folks.
- High-level coverage of CCAR/DFAST, EBA stress testing.
- What data BI teams must produce to support each regime.

**Diagrams:**
- Mermaid: regulator → regime → required data outputs.

**Code examples:**
1. SQL: extract the data needed for an FRTB SA bucket-level sensitivities report.
2. SQL: BCBS-239 lineage attestation query.

**Exercises:** include a "map this BCBS 239 principle to a data engineering practice" matrix.

- [ ] Draft (~700 lines), build, review, commit: `Draft Module 19 — Regulatory Context`.

---

### Task 18: Module 20 — Working with the Business

**File:** `docs/modules/20-working-with-business.md`

**Required content:**
- Stakeholder map: traders, risk managers, finance, compliance, audit, regulators — what each cares about.
- Translating business asks into data specs (grain, dimensions, measures, freshness).
- How to push back on a "just sum it" request; how to surface non-additivity to non-quants.
- Communicating uncertainty in DQ issues without losing trust.

**Diagrams:**
- Stakeholder/RACI matrix (markdown table).

**Code examples:** less applicable — instead, include 2 worked "translation" examples (business ask → data spec).

**Exercises:** include "rewrite this business ask as a precise data spec."

- [ ] Draft (~600 lines — more prose, fewer code blocks), build, review, commit: `Draft Module 20 — Working with the Business`.

---

### Task 19: Module 21 — Anti-patterns

**File:** `docs/modules/21-antipatterns.md`

**Required content:**
- Pre-aggregating non-additive measures.
- Storing only the latest snapshot (no bitemporality) and discovering you can't reproduce yesterday's report.
- "One big fact table" with mixed grains.
- Hard-coded business dates; timezone-naïve EOD.
- Implicit conformance (fixing identifiers in the report layer).
- Over-trusting source systems' "official" feed.

**Format:** for each anti-pattern, a 1-page block: symptom → why it happens → why it hurts → the fix → example before/after SQL.

**Diagrams:** before/after star schemas for two of the anti-patterns.

**Code examples:** the before/after SQL pairs *are* the code examples — at least 4 such pairs.

**Exercises:** include "audit this schema for anti-patterns."

- [ ] Draft (~800 lines), build, review, commit: `Draft Module 21 — Anti-patterns`.

---

### Task 20: Module 22 — Capstone

**File:** `docs/modules/22-capstone.md`

**Required content:**
- Project brief: design and partially implement a market-risk reporting mart for a small synthetic portfolio (rates + FX) covering positions, sensitivities, VaR, P&L, and stress.
- Deliverables: bus matrix, ER diagram, dbt-style model code, sample reports, DQ checks, lineage attestation.
- Rubric (table) — what "passing" vs. "excellent" looks like for each deliverable.
- Reference solution outline (NOT a full solution — bullet outline of the approach + 2 illustrative code snippets) so users can self-grade.
- Self-assessment questions: 15+ questions covering all phases.

**Diagrams:** sample bus matrix and a target reference architecture.

**Code examples:** 2–3 illustrative snippets (one DDL for a fact, one VaR calc, one DQ check).

- [ ] Draft (~900 lines), build, review, commit: `Draft Module 22 — Capstone`.

---

## Phase 2 — Polish & Completion

### Task 21: Backfill modules 01 and 02 to template

**Files:**
- Modify: `docs/modules/01-market-risk-foundations.md`
- Modify: `docs/modules/02-securities-firm-organization.md`

**Required additions:**
- Module 01: add 1 mermaid diagram (risk-types overview), 1 worked example (a tiny DV01 calculation), 3 exercises with collapsed solutions, "Further reading" section.
- Module 02: add 1 worked example (trace a trade through the org), 3 exercises with collapsed solutions, "Further reading" section. (Diagrams already present.)

- [ ] Edit both files; ensure each now matches the canonical 8-section template.
- [ ] Build, review, commit: `Polish Modules 01–02 to template`.

---

### Task 22: Complete the glossary

**File:** `docs/modules/glossary.md` (note: file is at `docs/glossary.md`)

**Required additions:**
- Add missing X–Z entries (Yield curve, Zero coupon, etc.).
- Cross-link every glossary term that appears as a section header in any module 03–22 (use mkdocs internal links).
- Remove the "will be expanded" footer note.
- Add a "see also" line on the densest entries (VaR, Sensitivity, P&L, etc.).

Acceptance: every distinct technical term used in modules 01–22 has a glossary entry, and the glossary footer is gone.

- [ ] Edit, build, review, commit: `Complete glossary A–Z and cross-link`.

---

### Task 23: Refresh `index.md` and `curriculum.md`

**Files:**
- Modify: `docs/index.md`
- Modify: `docs/curriculum.md`

**Required updates:**
- `index.md`: rewrite the "module structure" section to point to actually-completed modules; add a "How to use this site" block; add a "What's covered / What's not" block listing in-scope (FRTB IMA at conceptual level, classical VaR, dimensional modeling) vs. out-of-scope (full pricing-model derivations, regulatory exam prep).
- `curriculum.md`: refresh the stats coverage map now that all modules exist; remove any "coming soon" language; add an estimated time-per-module table.

- [ ] Edit, build, review, commit: `Refresh index and curriculum after content completion`.

---

### Task 24: Consolidated review pass

**Files:** all of `docs/modules/*.md`

**Checks:**
- Every module's "Further reading" links resolve (spot-check ~5 random links).
- No `*To be expanded*` markers anywhere (`grep -r "To be expanded" docs/` returns nothing).
- Every code block has a language hint for syntax highlighting.
- Every mermaid diagram renders (verify locally in `mkdocs serve`).
- Cross-references between modules use mkdocs link syntax, not external URLs.
- No duplicated content across modules (each concept owned by one module).

- [ ] Run the checks.
- [ ] Fix any issues found in a single sweep.
- [ ] Final commit: `Consolidated review pass — fix link rot, missing language hints, cross-refs`.

---

### Task 25: Re-enable strict build

**File:** `.github/workflows/deploy.yml`

Now that the site is content-complete, restore strict mode so future PRs catch broken links and missing nav entries.

- [ ] Change `mkdocs build --verbose` back to `mkdocs build --strict`.
- [ ] Push and confirm the run is green.
- [ ] Commit: `Re-enable mkdocs --strict for CI`.

---

## Self-review checklist

- [x] Every nav file in mkdocs.yml is covered by a task (modules 01–22, glossary, index, curriculum).
- [x] No `TBD` / `TODO` placeholders inside the plan.
- [x] Each module task names: target file, required sections, required diagrams, required code examples, required exercises, target line count.
- [x] Phase order ensures the critical/flagship modules (09, 12, 13) get full attention and their downstream consumers (14 references 12 and 13) are drafted after them.
- [x] Polish phase (21–24) addresses every gap surfaced by the audit (assets, code samples, glossary completeness, link rot).
- [x] Final task (25) restores CI rigor.

---

## Execution choice

After saving this plan, choose:

1. **Subagent-driven (recommended for this scale):** dispatch a fresh subagent per module task; user reviews after each draft; fastest iteration and keeps main context clean.
2. **Inline execution:** I draft each module in this conversation; user reviews inline. Slower for 20 modules but no context handoff.
