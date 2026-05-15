# Credit Risk Track — Curriculum Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author a parallel Credit Risk track on the existing Risk BI Training site, structurally mirroring the Market Risk track (8 phases, ~24 modules) and reusing shared modules where the topic genuinely transfers (data modelling, engineering excellence, lineage, bitemporality).

**Architecture:** Sequential drafting in nav order. Claude drafts each module to 600–1000 lines; user reviews/edits. Each module includes: structured prose, ≥1 mermaid diagram, ≥2 worked code examples (SQL or Python), 3–5 exercises with solutions in a collapsed `<details>` block. Honesty disclaimers (same pattern as Phase 8 Vendor Systems) are mandatory and load-bearing.

**Tech Stack:** MkDocs Material 9.7, pymdown-extensions (admonitions, superfences, tabbed, tasklist, arithmatex/MathJax), mermaid for diagrams, fenced SQL/Python code blocks. Top-tabs navigation already wired in `mkdocs.yml` (architecture phase, 2026-05-15).

**Audit baseline (2026-05-15):**
- Track architecture in place: top-tabs nav, course chooser on home, overview page at `docs/credit-modules/00-credit-risk-overview.md`.
- All credit modules — UNWRITTEN. Only the overview exists.
- Glossary — Market-Risk-focused; credit-specific terms to be added incrementally as modules are drafted.
- No `docs/credit-modules/code-samples/` directory yet — will reuse the existing `docs/code-samples/` structure with a `credit-` prefix on filenames.

---

## File Structure

```
docs/
├── index.md                         # Already updated — course chooser
├── curriculum.md                    # Market Risk curriculum (already scoped)
├── credit-modules/
│   ├── 00-credit-risk-overview.md   # EXISTS — track entry page
│   ├── 01-credit-risk-foundations.md            # NEW
│   ├── 02-credit-function-organization.md       # NEW
│   ├── 03-credit-instrument-lifecycle.md        # NEW
│   ├── 04-credit-instruments.md                 # NEW
│   ├── 05-core-credit-dimensions.md             # NEW
│   ├── 06-credit-fact-tables.md                 # NEW
│   ├── 07-probability-of-default.md             # NEW
│   ├── 08-loss-given-default.md                 # NEW
│   ├── 09-exposure-at-default.md                # NEW
│   ├── 10-expected-loss.md                      # NEW
│   ├── 11-unexpected-loss-credit-var.md         # NEW
│   ├── 12-credit-stress-testing.md              # NEW
│   ├── 13-rating-systems-migration.md           # NEW
│   ├── 14-collateral-netting.md                 # NEW
│   ├── 15-concentration-limits.md               # NEW
│   ├── 16-ifrs9-cecl-provisioning.md            # NEW
│   ├── 17-credit-regulatory-context.md          # NEW
│   ├── 18-working-with-credit-officers.md       # NEW
│   ├── 19-credit-antipatterns.md                # NEW
│   ├── 20-credit-capstone.md                    # NEW
│   ├── 21-moodys-creditedge-applied.md          # NEW
│   └── 22-sp-capital-iq-applied.md              # NEW
├── code-samples/
│   ├── sql/credit-*.sql             # New, prefixed for clarity
│   └── python/credit-*.py
└── glossary.md                      # Append credit terms as drafted
```

> Numbering note: Credit-modules use `01..22` independent of the Market Risk `01..27`. The overview is `00`. Where a credit module is genuinely a passthrough to a Market Risk module (e.g. dimensional-modelling fundamentals), no credit file is created — the overview's "Where this connects to Market Risk" section already links it.

---

## Module template (canonical, same as Market Risk)

Every credit-module follows this section order. Deviations only when the topic genuinely doesn't support a section.

1. **Learning objectives** — bullet list, 4–6 items, measurable verbs
2. **Why this matters** — 2–3 paragraphs connecting topic to BI/data work in credit risk
3. **Core concepts** — main body, sub-headed by concept, with diagrams inline
4. **Worked examples** — ≥2 examples with code (SQL/Python) or step-by-step calculation
5. **Common pitfalls** — admonition block, 3–5 items
6. **Exercises** — 3–5 questions, mix of conceptual and applied; solutions in `??? note "Solution"` collapsed blocks
7. **Further reading** — 3–6 links/refs (papers, books, regulator docs)
8. **Recap** — 5-bullet "you should now be able to…" summary

Acceptance criteria per module: 600–1000 lines, ≥1 mermaid diagram, ≥2 code examples, 3–5 exercises with solutions, no `*To be expanded*` markers remaining.

---

## Per-module content brief

### Phase 1 — Foundations

#### M01: Credit Risk Foundations
What credit risk is, distinguished from market/operational/liquidity. The PD × LGD × EAD identity introduced as the unifying decomposition. Brief regulatory tour (Basel I → II IRB → III, IFRS 9 / CECL). The same load-bearing diagram pattern as MR M01 (risk taxonomy + sub-types). Audience: data professional reading their first credit-risk doc.

#### M02: The Credit Function in a Securities Firm
Credit as a 2nd-line-of-defence function. Underwriting vs. credit risk vs. credit portfolio management vs. credit operations. Reporting lines (CRO ≠ CCO). Where credit data lives in the firm's stack and how it differs structurally from market-risk data flows.

#### M03: Loan / Bond / Credit-Derivative Lifecycle
Origination → underwriting → drawdown → servicing → restructure → default → recovery → write-off. Compared and contrasted with the market-risk trade lifecycle (M03 of MR track). State-transition diagram. Why credit lifecycles span years not days, and what that does to your bitemporal model.

#### M04: Credit Instruments
Loans (term, revolver, syndicated), bonds (senior secured/unsecured/sub), credit derivatives (CDS single-name and index, total return swaps), securitisations (ABS/MBS/CLO at conceptual level). For each: cashflow shape, default-risk shape, data-model implications. Companion to MR M04.

### Phase 2 — Data Modeling

> Phase 2's M05 (dimensional-modelling fundamentals) is a passthrough to Market Risk M05. No credit file required. Linked from the overview.

#### M05 (credit numbering): Core Credit Dimensions
`dim_obligor`, `dim_facility`, `dim_collateral`, `dim_rating_scale`, `dim_industry`, `dim_country_risk`. Each profiled the way MR M06 profiles market-risk dimensions. Conformance with MR's `dim_counterparty` is the entire point — a counterparty is an obligor when seen from credit, a counterparty when seen from trading.

#### M06 (credit numbering): Credit Fact Tables
`fact_facility_balance`, `fact_facility_drawn_undrawn`, `fact_pd_assignment`, `fact_lgd_assignment`, `fact_ead_calculation`, `fact_expected_loss`, `fact_default_event`, `fact_recovery_cashflow`, `fact_rating_history`. Grain analysis for each. Companion to MR M07.

### Phase 3 — Risk Measures (the dense maths phase)

#### M07: Probability of Default (PD)
Through-the-cycle (TTC) vs. point-in-time (PIT) PD. PD calibration data: historical default rates by rating bucket, by vintage, by segment. Bayesian shrinkage for low-default portfolios (LDP). Term-structure of PD. Survival analysis at intuitive level. Honesty disclaimer: deep model-validation territory will be flagged as out-of-scope, with pointers.

#### M08: Loss Given Default (LGD)
Recovery rates by seniority, by collateral type, by jurisdiction. Cure rates and the workout LGD vs. market LGD distinction. Downturn LGD (regulatory requirement). The famous beta-distribution model for LGD. Data lineage from a workout system to an LGD fact.

#### M09: Exposure at Default (EAD)
For drawn facilities EAD ≈ outstanding. For revolvers EAD = drawn + CCF × undrawn. CCF (credit conversion factor) calibration data needs. For derivatives EAD = current exposure + PFE (potential future exposure); reference SA-CCR and IMM at conceptual level. Wrong-way risk teaser.

#### M10: Expected Loss (PD × LGD × EAD)
The product. One-period EL, lifetime EL (lead-in to IFRS 9 stage 2/3). EL allocation (counterparty → portfolio → segment) and the additivity question — EL *is* additive across counterparties (unlike VaR), which has fact-table consequences. Aggregation patterns.

#### M11: Unexpected Loss & Credit VaR
The portfolio loss distribution. Variance of credit losses, the role of correlation. Asymptotic Single Risk Factor (ASRF) — the model behind Basel IRB capital. CreditMetrics intuition (Merton + asset-correlation matrix). Credit VaR vs. capital. Honesty disclaimer: full Monte Carlo credit-portfolio model implementation is out of scope; the goal is to teach the data professional what numbers are produced and how to store them.

#### M12: Credit Stress Testing
Macro scenario → PD/LGD/EAD shifts → EL impact → capital impact. CCAR / DFAST / EBA / ICAAP at high level. Reverse stress testing. Difference from market-risk stress in cadence (quarterly vs. daily) and in the linkage to provisioning rather than P&L.

### Phase 4 — Cross-Cutting

#### M13: Rating Systems & Migration
Internal ratings vs. external (Moody's/S&P/Fitch) ratings. Master-scale design. Rating-migration matrices and how they're calibrated. Rating bitemporality is *significantly* harder than counterparty-attribute bitemporality because a rating change is itself a risk event. Connect to MR M13 (Bitemporality) but document where credit's needs diverge.

#### M14: Collateral & Netting
Collateral types (cash, securities, real estate, receivables, guarantees). Eligibility, haircuts, frequency of revaluation. Netting agreements (ISDA, GMRA) and their effect on EAD. Collateral lifecycle is its own bitemporal problem. Data model: `dim_collateral`, `fact_collateral_value`, `fact_collateral_assignment`.

#### M15: Concentration Risk & Limits
Single-name concentration, sector concentration, geographic concentration, vintage concentration. Herfindahl indices. Limit frameworks (single-name limit, sector limit, country limit) and how breaches are escalated. Limit-utilisation fact tables.

#### M16: IFRS 9 / CECL Provisioning
Stage 1 / 2 / 3 (IFRS 9). Lifetime ECL vs. 12-month ECL. Significant Increase in Credit Risk (SICR) — the operational definition. CECL parallel for US GAAP firms. Forward-looking macro overlay. Data-model implications: stage history, ECL calculation lineage, the quarterly cadence vs. daily MR cadence. Honesty disclaimer: jurisdiction-specific implementation choices vary widely; the module covers the canonical pattern.

### Phase 5 — Engineering

> Phase 5 is a passthrough to Market Risk M15–M18 (Data Quality, Lineage, Performance, Architecture). No credit-specific file required at the architecture-phase boundary. If credit-specific patterns emerge during drafting (e.g. workout-system lineage is materially different), they will be split into a dedicated module.

### Phase 6 — Business

#### M17: Regulatory Context (Basel IRB, IFRS 9, CECL)
The three standards a credit data professional must know. Basel IRB foundation/advanced. IFRS 9 vs. CECL key differences. Stress-test regulators (CCAR, EBA, BoE). Pillar 3 disclosures. The honesty disclaimer here is heavy: regulatory detail varies by jurisdiction and changes; the module teaches the structure and points to the BIS / IFRS / FASB primary sources.

#### M18: Working with Credit Officers
The cultural difference vs. working with traders. Credit officers think in narratives (the *credit memo*), in industries, in management quality. Translating "show me obligors at risk" into a SQL filter that respects the credit officer's actual mental model. Cf. MR M20.

#### M19: Credit Anti-patterns
Real cases where credit data went wrong. Stage migration that wasn't reproducible. PD models calibrated on too-recent data. Collateral haircuts not refreshed. Concentration breaches missed because the dimension was wrong. Cf. MR M21.

### Phase 7 — Capstone

#### M20: Credit Capstone Project
Design and implement a small credit-risk reporting mart end-to-end. Includes: counterparty / facility / collateral dimensions, balance / PD / LGD / EAD / EL facts, an IFRS 9 stage history, and a concentration view. Rubric and reference-solution outline. Cf. MR M22.

### Phase 8 — Vendor Systems

> Vendor scope is intentionally narrower than MR Phase 8. Two applied modules cover the dominant credit-data vendor shapes; the framework module is shared (passthrough to MR M23 Vendor Framework, with a credit-specific addendum embedded in M21 below).

#### M21: Moody's CreditEdge / DRSK Applied
EDF (Expected Default Frequency) data, the structural-model basis (Merton-style), how a credit warehouse ingests CreditEdge feeds, lineage from EDF to internal PD overlay. Honesty disclaimer: I have general knowledge; firm-specific contractual / API specifics will be flagged.

#### M22: S&P Capital IQ Pro Applied
Fundamentals data, ratings feeds, market-data integration, peer-group analytics. How credit officers use it day-to-day vs. how it lands in the warehouse. Same honesty disclaimer pattern.

---

## Authorship model

Same as the Market Risk track:

- **Claude drafts** each module to the template, 600–1000 lines.
- **User reviews** for technical accuracy, firm-specific calibration, and tone.
- **Iterate** on the draft until the user is satisfied; commit when accepted.
- **One module per session** is the typical cadence — the modules are dense and a single review pass can take an hour.
- **Sub-agent dispatch** is appropriate for parallel drafting of independent modules (e.g. M07/M08/M09 — PD/LGD/EAD — could be drafted in parallel since they're conceptually orthogonal).

## Honesty disclaimer pattern (mandatory)

Every credit module opens with — or contains within section 2 ("Why this matters") — an explicit honesty marker following the Vendor Systems pattern:

> **Confidence map for this module:**
>
> - **High confidence:** the canonical structure, the published regulatory framework, the standard data-model patterns, the maths at the level taught here.
> - **Medium confidence:** specific calibration techniques, jurisdiction-specific implementation choices, vendor-specific feed shapes.
> - **Lower confidence (flagged inline):** [specific topics where the author's knowledge thins, e.g. "behavioural PD model calibration for retail mortgages in EU jurisdictions"].
>
> If you spot errors specific to your firm's practice or your jurisdiction's regulation, that's signal, not noise.

The market modules were written this way and the credit modules must be too. The honest "here is where my confidence drops" markers are deliberate and load-bearing; they tell the reader where to bring their own expert.

## Suggested build order

The dependency graph between modules drives the build order. The recommendation:

1. **Phase 1 first (M01–M04)** — foundations. The vocabulary the rest of the track uses.
2. **Phase 3 (M07–M12) before Phase 2 finalisation** — risk measures drive the fact-table design. Drafting the fact-tables module without first drafting the measures it stores produces vague modules. Sequence: M07 → M08 → M09 → M10 → M11 → M12.
3. **Phase 2 (M05–M06)** — once the measures are in place, the dimensions and fact tables write themselves.
4. **Phase 4 (M13–M16)** — cross-cutting. M13 (Rating Systems) and M16 (IFRS 9 / CECL) are the highest-value modules in this phase; M14 and M15 can be drafted in either order.
5. **Phase 6 (M17–M19)** — business and regulatory. M17 (regulatory context) is dense and should be drafted with care; M18 and M19 are lighter.
6. **Phase 7 (M20)** — capstone. Drafted last because it integrates everything.
7. **Phase 8 (M21–M22)** — vendor applied. Lowest priority; depends on the credit warehouse design from M05/M06 being settled.

This order means the **first 12 credit modules drafted** give a reader a usable arc from "what is credit risk" through to "how is credit VaR and stress computed". That arc is the natural minimum-viable credit track.

## Notes on shared modules (Market Risk modules reused for Credit Risk readers)

The following Market Risk modules are linked from the credit-risk overview as the canonical home of the topic. The Credit Risk track does **not** create a duplicate file unless the credit angle materially differs:

| MR module | Why it transfers to credit |
|---|---|
| M05 — Dimensional Modelling | Star/snowflake/SCD/Kimball patterns are fact-agnostic. |
| M06 — Core Dimensions | `dim_counterparty`, `dim_book`, `dim_currency`, `dim_date` are conformed across both tracks; the conformance is the entire point. Credit adds `dim_obligor`, `dim_facility`, `dim_collateral` (covered in credit M05). |
| M13 — Bitemporality | The as-of vs. system-time distinction is identical. Credit adds rating-history bitemporality on top, which gets its own module (credit M13). |
| M15 — Data Quality | Framework, tolerance bands, reconciliation patterns are identical. |
| M16 — Lineage & Auditability | BCBS 239 covers credit numbers exactly as it covers market-risk numbers. |
| M17 — Performance & Materialisation | Partitioning / columnar / aggregate strategy is fact-agnostic. |
| M18 — Architecture Patterns | Golden source, mart vs. warehouse, batch vs. intraday — same patterns, different facts. |
| M23 — Vendor Systems Framework | The 6-step onboarding template applies to credit vendors equally. Credit Phase 8 modules instantiate it for CreditEdge / Capital IQ. |

Where the credit angle materially differs, a dedicated credit-risk module is warranted. The judgement calls are:

- **Bitemporality** — rating histories are a meaningful enough delta to warrant credit M13 (Rating Systems & Migration), but the underlying patterns from MR M13 still hold.
- **Aggregation & Additivity** — EL is additive (unlike VaR), which is a teachable contrast inside credit M10 rather than its own module.
- **P&L Attribution** — credit doesn't have a daily P&L attribution test the way market risk does; the analogous workflow is IFRS 9 / CECL provisioning movement explain (covered in credit M16).

## Glossary integration

Credit terms are appended to the existing `docs/glossary.md` (shared between tracks) as each module is drafted. New entries to add:

- Obligor, facility, drawn, undrawn, commitment, CCF
- PD (TTC, PIT, lifetime), LGD (workout, market, downturn), EAD, EL, UL
- IFRS 9 (Stage 1/2/3, SICR, ECL, lifetime ECL, 12-month ECL), CECL
- Basel IRB (Foundation, Advanced), AIRB / FIRB, A-IRB
- Migration matrix, ASRF, CreditMetrics
- Workout, recovery, cure, write-off
- Senior secured / senior unsecured / subordinated
- CDS, total return swap, single-name, index, ABS, MBS, CLO
- Collateral haircut, eligibility, ISDA CSA, GMRA, netting set
- Wrong-way risk, right-way risk
- SA-CCR, IMM, PFE, EE, EEPE
- Concentration, Herfindahl, single-name limit, sector limit
- CCAR, DFAST, EBA stress test, ICAAP

## Verification per module

Every module before commit must:

1. `mkdocs build --strict` — passes.
2. All internal links resolve (the strict build catches this).
3. At least one mermaid diagram renders.
4. At least two code examples exist; if SQL, must be runnable against a sketch of the credit warehouse; if Python, must be standalone or have a header comment explaining required setup.
5. 3–5 exercises with solutions in collapsed blocks.
6. Honesty disclaimer present in section 2 or as an admonition before section 3.
7. Length 600–1000 lines (markdown source).

## Out of scope (explicit non-goals)

To keep the track tractable:

- **Full credit-portfolio Monte Carlo implementation** — covered conceptually in M11; full code-level implementation is deferred to a future advanced module.
- **Behavioural / retail PD model deep-dives** — M07 covers the framework; deep specialist content for retail / SME / project-finance segments is not in scope.
- **Counterparty Credit Risk (CCR) for derivatives** — touched in M09 (EAD) at the SA-CCR conceptual level; full CCR / CVA / xVA modelling is a separate track that is not yet planned.
- **Securitisation-specific risk modelling** — M04 covers ABS/MBS/CLO at instrument-recognition level; tranching mechanics, waterfalls, and rating-agency methodologies are not in scope.
- **Country / sovereign credit risk** — touched in M15 (concentration); dedicated sovereign-risk methodology is not in scope.

These can be added as follow-on modules once the core 22 are stable.

---

## Phase 0 — Infrastructure (already complete as of 2026-05-15)

- [x] **Step 1:** Top-tabs nav added to `mkdocs.yml`.
- [x] **Step 2:** Course chooser added to `docs/index.md`.
- [x] **Step 3:** `.mr-tracks` / `.mr-track` CSS added to `docs/stylesheets/extra.css`.
- [x] **Step 4:** Track Overview written at `docs/credit-modules/00-credit-risk-overview.md`.
- [x] **Step 5:** `docs/curriculum.md` re-titled to Market Risk Curriculum.
- [x] **Step 6:** `mkdocs build --strict` passes.
- [x] **Step 7:** Architecture commit landed.

## Phase 1 — Module drafting (sequential, one per task)

> Tasks below are deliberately stubbed. They will be expanded with the same detail level as the Market Risk plan (`2026-05-07-finalize-training.md`) once the first module is drafted and the tone has been calibrated.

### Task 1: Credit M01 — Credit Risk Foundations
- [ ] Draft to template; honesty marker mandatory; mermaid diagram of credit-risk taxonomy; worked example computing one-year EL on a single facility.

### Task 2: Credit M02 — The Credit Function in a Securities Firm
- [ ] Draft to template; org diagram; mapping table of credit roles → data they consume.

### Task 3: Credit M03 — Loan / Bond / Credit-Derivative Lifecycle
- [ ] Draft to template; state-transition diagram; SQL example of facility lifecycle table.

### Task 4: Credit M04 — Credit Instruments
- [ ] Draft to template; instrument-comparison table; SQL example of `dim_facility` populated for each instrument type.

### Task 5: Credit M07 — Probability of Default (PD)
- [ ] Draft to template; PD calibration worked example in Python; honesty disclaimer flagging deep validation as out-of-scope.

### Task 6: Credit M08 — Loss Given Default (LGD)
- [ ] Draft to template; workout LGD calculation example; beta distribution illustration.

### Task 7: Credit M09 — Exposure at Default (EAD)
- [ ] Draft to template; CCF example for a revolver; SA-CCR conceptual diagram for derivatives.

### Task 8: Credit M10 — Expected Loss
- [ ] Draft to template; aggregation worked example showing EL additivity; SQL example aggregating EL up the obligor / sector / portfolio hierarchy.

### Task 9: Credit M11 — Unexpected Loss & Credit VaR
- [ ] Draft to template; ASRF intuition; small Python loss-distribution simulation.

### Task 10: Credit M12 — Credit Stress Testing
- [ ] Draft to template; macro scenario → PD shift → EL impact worked example; quarterly cadence callout vs. daily MR cadence.

### Task 11: Credit M05 — Core Credit Dimensions
- [ ] Draft to template; profile each credit-specific dimension; conformance discussion with shared MR dimensions.

### Task 12: Credit M06 — Credit Fact Tables
- [ ] Draft to template; grain analysis for each fact table; SQL DDL for the canonical tables.

### Task 13: Credit M13 — Rating Systems & Migration
- [ ] Draft to template; migration-matrix example in Python; rating bitemporality discussion.

### Task 14: Credit M16 — IFRS 9 / CECL Provisioning
- [ ] Draft to template; stage-migration worked example; SICR operational definition discussion.

### Task 15: Credit M14 — Collateral & Netting
- [ ] Draft to template; collateral lifecycle; SQL example of collateral-haircut application.

### Task 16: Credit M15 — Concentration Risk & Limits
- [ ] Draft to template; Herfindahl computation; limit-utilisation fact-table example.

### Task 17: Credit M17 — Regulatory Context
- [ ] Draft to template; regulatory-comparison table (Basel IRB / IFRS 9 / CECL); honesty disclaimer is heavy here.

### Task 18: Credit M18 — Working with Credit Officers
- [ ] Draft to template; translation table from credit-memo language to SQL filters.

### Task 19: Credit M19 — Credit Anti-patterns
- [ ] Draft to template; 5–7 real anecdotes (fictionalised), each with the data-design lesson.

### Task 20: Credit M20 — Credit Capstone Project
- [ ] Draft project brief, rubric, reference-solution outline; should reuse capstone scaffolding from MR M22.

### Task 21: Credit M21 — Moody's CreditEdge / DRSK Applied
- [ ] Draft to template; framework instantiation; honesty disclaimer flagging contractual / API specifics as firm-dependent.

### Task 22: Credit M22 — S&P Capital IQ Pro Applied
- [ ] Draft to template; framework instantiation; same honesty disclaimer pattern.

---

## Phase 2 — Polish

### Task 23: Glossary expansion
- [ ] Append all credit terms enumerated above to `docs/glossary.md`.

### Task 24: Credit curriculum overview page
- [ ] Once Phase 1 is complete, write `docs/credit-modules/curriculum.md` mirroring the structure of `docs/curriculum.md` (per-module hour estimates, suggested study sequences). Add to nav under the Credit Risk tab.

### Task 25: Cross-link audit
- [ ] Re-read every credit module and ensure cross-links to MR shared modules are correct and the conformance discussions are accurate.

### Task 26: Final build verification
- [ ] `mkdocs build --strict` passes with no new warnings beyond the pre-existing INFO about `_template.md` and `code-samples/README.md`.

---

## Done definition

The Credit Risk track is "v1 complete" when:

- All 22 credit modules are drafted to template (600–1000 lines each).
- Glossary covers all credit terms enumerated above.
- Credit curriculum page exists alongside the overview.
- Cross-links to MR shared modules are correct.
- `mkdocs build --strict` passes.
- The course-chooser card on the home page reads "→ 22 modules · Available now" instead of "in development".
