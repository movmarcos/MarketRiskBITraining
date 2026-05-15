# Credit Risk Track — Overview

!!! abstract "Track Goal"
    A parallel training track to Market Risk, focused on the data shapes, modelling decisions, and engineering disciplines specific to **credit risk** — for the same audience of BI developers, data engineers, and analytics teams.

---

## 1. Welcome to the Credit Risk Track

This track is the credit-risk sibling of the Market Risk training. Where Market Risk teaches the data professional how to model sensitivities, VaR, stress tests, and the temporal mess that surrounds them, the Credit Risk track teaches the analogous machinery for **probability of default (PD), loss given default (LGD), exposure at default (EAD), expected loss, credit VaR, IFRS 9 / CECL provisioning, and credit stress testing**.

The audience is identical: BI developers, data engineers, and analytics teams whose job is to source, model, store, and serve the numbers a **credit committee** runs on — the way the Market Risk track does for the numbers a trading desk runs on. The pedagogical contract is the same: business context first, data shapes always, just enough maths to make the data shapes obvious, and explicit honesty about where the author's knowledge thins.

If you have already worked through Market Risk, the structural patterns will feel familiar — eight phases, a foundations module, a data-modelling phase, a risk-measures phase, cross-cutting concepts, engineering excellence, business alignment, a capstone, and an applied vendor-systems phase. Several phases (data-modelling fundamentals, engineering, parts of regulation) are genuinely shared and will link back to the Market Risk modules as the canonical home of those topics.

## 2. Status (as of mid-2026)

This track is in active development. The track structure is set; modules are being drafted. Current status:

| Phase | Module | Status |
|---|---|---|
| 1 — Foundations | Credit Risk Foundations | Planned |
| 1 — Foundations | The Credit Function in a Securities Firm | Planned |
| 1 — Foundations | Loan / Bond / Credit-Derivative Lifecycle | Planned |
| 1 — Foundations | Credit Instruments | Planned |
| 2 — Data Modeling | Dimensional Modelling *(shared with Market Risk)* | Available |
| 2 — Data Modeling | Core Credit Dimensions | Planned |
| 2 — Data Modeling | Credit Fact Tables | Planned |
| 3 — Risk Measures | Probability of Default (PD) | Planned |
| 3 — Risk Measures | Loss Given Default (LGD) | Planned |
| 3 — Risk Measures | Exposure at Default (EAD) | Planned |
| 3 — Risk Measures | Expected Loss (PD × LGD × EAD) | Planned |
| 3 — Risk Measures | Unexpected Loss & Credit VaR | Planned |
| 3 — Risk Measures | Credit Stress Testing | Planned |
| 4 — Cross-cutting | Rating Systems & Migration | Planned |
| 4 — Cross-cutting | Collateral & Netting | Planned |
| 4 — Cross-cutting | Concentration Risk & Limits | Planned |
| 4 — Cross-cutting | IFRS 9 / CECL Provisioning | Planned |
| 5 — Engineering | Data Quality, Lineage, Performance, Architecture *(shared with Market Risk)* | Available |
| 6 — Business | Regulatory Context (Basel IRB, IFRS 9, CECL) | Planned |
| 6 — Business | Working with Credit Officers | Planned |
| 6 — Business | Credit Anti-patterns | Planned |
| 7 — Capstone | Credit Capstone Project | Planned |
| 8 — Vendor Systems | Moody's CreditEdge / DRSK | Planned |
| 8 — Vendor Systems | S&P Capital IQ Pro | Planned |

The "Available" rows above link to the Market Risk modules that are already published and that genuinely cover the same material from a perspective that transfers without modification. Credit-specific stubs will replace them only where the credit angle differs enough to warrant its own module.

## 3. Where this connects to Market Risk

Several modules are shared between the two tracks. Rather than duplicate them, this track points to the Market Risk versions as the canonical home of those topics:

- **Dimensional Modelling fundamentals** — star vs. snowflake, SCDs, conformed dimensions, Kimball patterns are identical regardless of whether the fact is a sensitivity or a credit exposure. See [Dimensional Modelling](../modules/05-dimensional-modeling.md).
- **Core Dimensions** — `dim_counterparty`, `dim_book`, `dim_currency`, `dim_date` are shared dimensions; their conformance across both tracks is the entire point. See [Core Dimensions](../modules/06-core-dimensions.md).
- **Bitemporality** — the as-of vs. system-time distinction is a credit-risk concern as much as a market-risk one (think IFRS 9 stage migration replays). See [Bitemporality](../modules/13-time-bitemporality.md).
- **Data Quality** — the framework, tolerance bands, and reconciliation patterns transfer wholesale. See [Data Quality](../modules/15-data-quality.md).
- **Lineage & Auditability** — BCBS 239 applies to credit numbers exactly as it applies to market-risk numbers. See [Lineage & Auditability](../modules/16-lineage-auditability.md).
- **Performance & Materialisation** — partitioning, columnar storage, aggregate strategies are the same craft. See [Performance & Materialisation](../modules/17-performance-materialization.md).
- **Architecture Patterns** — golden source, mart vs. warehouse, batch vs. intraday — same patterns, different facts. See [Architecture Patterns](../modules/18-architecture-patterns.md).

Where the credit angle materially differs from the market-risk treatment (e.g. counterparties carry rating histories that trades do not; collateral has its own bitemporal lifecycle; exposures are typically long-dated where trades are short-dated), a dedicated credit-risk module will eventually be authored. Until then, the shared Market Risk module is the reference.

## 4. Why Credit Risk for BI/data professionals

Every commercial bank, every securities firm with a counterparty book, and every asset manager running fixed-income or private-credit strategies has a credit-risk function. Its data shapes are **substantially different** from market risk in ways that a data professional who has only ever seen one will find surprising:

- **Long-dated obligations vs. short-dated trades.** A 30-year mortgage or a 7-year corporate loan sits on the books for years. A trading position turns over daily. Your fact tables need very different temporal modelling.
- **PD / LGD / EAD vs. sensitivities / VaR.** Credit risk is a *product* of three numbers, each modelled separately, each with its own data lineage. Market risk is a *transformation* of a single P&L distribution. The grain decisions are different.
- **Quarterly accruals vs. daily revaluation.** IFRS 9 / CECL provisioning runs on a different cadence and a different statistical foundation than daily VaR. Your warehouse needs to serve both.
- **Rating histories and migration matrices.** A counterparty has a rating, and that rating moves over time. Capturing that movement bitemporally — and pricing the migration risk it represents — is a credit-specific data problem.

The data engineer who can do **both** market and credit risk is rare and valuable. Many shops segregate the two functions deeply; the warehouse engineer who can speak both languages becomes the natural integrator for the firm's enterprise risk view. That's the role this track aims to prepare you for.

## 5. What's available today

- **Market Risk track** — the proven reference. Twenty-seven modules, eight phases, all published. Use it as the model for what the Credit Risk modules will look like once drafted. [Start here](../modules/01-market-risk-foundations.md).
- **Credit Risk Foundations** (M01) and **Credit Risk Measures** (PD, LGD, EAD, EL) — the next modules to be drafted. They are the highest-priority items because the rest of the track builds on their vocabulary.
- **Glossary** — the [shared glossary](../glossary.md) covers credit-specific terms alongside market-risk terms. New entries will be added as the credit modules are drafted.

If you are eager to start working through Credit Risk content right now, the most useful path is to read the Market Risk modules on **dimensional modelling**, **core dimensions**, **bitemporality**, **data quality**, and **lineage** — because every one of those modules transfers to credit risk with only the names of the facts changed. The credit-specific modules will fill in the risk-measure layer on top of that foundation.

## 6. A note on author honesty

The same disclaimer pattern applies here as in the [Vendor Systems](../modules/23-vendor-systems-framework.md) phase of the Market Risk track:

> I have strong general knowledge of credit risk — the regulatory frameworks (Basel IRB, IFRS 9, CECL), the canonical risk-measure decomposition (PD × LGD × EAD), the shape of a credit warehouse, and the major vendor systems. My depth varies by sub-topic. I'll write modules with explicit honesty disclaimers about what I know first-hand vs. where my knowledge thins (e.g. specific calibration techniques for behavioural PD models, jurisdiction-specific provisioning rules, internal-ratings-based model validation in detail).
>
> If you spot errors specific to your firm's practice or your jurisdiction's regulation, that's signal, not noise — the market modules were written the same way and the credit modules will be too. The honest "here is where my confidence drops" markers are deliberate and load-bearing; they tell you where to bring your own expert.

---

[← Back to Home](../index.md){ .md-button } [Market Risk Track →](../modules/01-market-risk-foundations.md){ .md-button .md-button--primary }
