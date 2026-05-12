# Curriculum Overview

The training is structured as **27 modules** across **8 phases**, taking you from beginner to a confident, business-aligned BI professional in market risk.

## 📘 Phase 1 — Foundations

Build the mental model. Understand the business, the firm, the lifecycle, and the products before touching any data structures.

| # | Module | Focus |
|---|--------|-------|
| 1 | [Market Risk Foundations](modules/01-market-risk-foundations.md) | What market risk is, the risk function, regulatory landscape |
| 2 | [How a Securities Firm is Organized](modules/02-securities-firm-organization.md) | Front/Middle/Back office, Risk, Finance, Compliance — and how they map to data |
| 3 | [The Trade Lifecycle (Risk Lens)](modules/03-trade-lifecycle.md) | Front-to-back data flow: trade → position → revaluation → risk → reporting |
| 4 | [Financial Instruments Primer](modules/04-financial-instruments.md) | Cash vs. derivatives, linear vs. non-linear payoffs, just enough product knowledge |

## 📗 Phase 2 — Data Modeling Core

The core craft. Dimensional modeling applied to risk data — facts, dimensions, grain.

| # | Module | Focus |
|---|--------|-------|
| 5 | [Dimensional Modeling Fundamentals](modules/05-dimensional-modeling.md) | Star vs. snowflake, fact vs. dimension, SCDs, Kimball basics |
| 6 | [Core Dimensions in Market Risk](modules/06-core-dimensions.md) | Instrument, counterparty, book, trader, risk factor, scenario |
| 7 | [The Fact Tables of Market Risk](modules/07-fact-tables.md) | Trade, position, sensitivity, VaR, stress, P&L — grain analysis for each |

## 📙 Phase 3 — Risk Measures

The core risk measures. Heavy on statistics — but always in context.

| # | Module | Focus |
|---|--------|-------|
| 8 | [Sensitivities Deep Dive](modules/08-sensitivities.md) | Greeks, DV01, CS01, bucketed sensitivities, FRTB buckets |
| 9 | [Value at Risk (VaR)](modules/09-value-at-risk.md) ⭐ | Historical, parametric, Monte Carlo. Expected Shortfall. Backtesting. The biggest stats module. |
| 10 | [Stress Testing & Scenarios](modules/10-stress-testing.md) ⭐ | Historical, hypothetical, regulatory, reverse stress |

## 📕 Phase 4 — Cross-Cutting Concepts

The concepts that touch every part of the data model.

| # | Module | Focus |
|---|--------|-------|
| 11 | [Market Data & Risk Factors](modules/11-market-data.md) | Curves, surfaces, fixings, risk factor taxonomy, proxying |
| 12 | [Aggregation, Hierarchies & Additivity](modules/12-aggregation-additivity.md) ⭐ | Additive / semi-additive / non-additive — the biggest source of bugs |
| 13 | [Time & Bitemporality](modules/13-time-bitemporality.md) ⭐ | Trade/value/settlement/as-of/system dates. Reproducing historical views. |
| 14 | [P&L and P&L Attribution](modules/14-pnl-attribution.md) | Clean/dirty P&L, Greek-based explain, hypothetical vs. actual |

## 📔 Phase 5 — Engineering & Operational Excellence

The reality of running risk data in production.

| # | Module | Focus |
|---|--------|-------|
| 15 | [Data Quality & Reconciliation](modules/15-data-quality.md) | DQ frameworks, front-to-back recs, tolerance bands |
| 16 | [Data Lineage & Auditability](modules/16-lineage-auditability.md) | BCBS 239, traceability, regulatory expectations |
| 17 | [Performance & Materialization](modules/17-performance-materialization.md) | Aggregates, partitioning, columnar storage, when to pre-compute |
| 18 | [Architecture Patterns](modules/18-architecture-patterns.md) | Risk warehouse vs. mart, golden source, batch vs. intraday |

## 📒 Phase 6 — Working as a Business-Aligned Pro

The soft skills that separate good from great.

| # | Module | Focus |
|---|--------|-------|
| 19 | [Regulatory Context (Just Enough)](modules/19-regulatory-context.md) | FRTB SA/IMA, IMCC, P&L attribution test, NMRF, IFRS 9 |
| 20 | [Working with the Business](modules/20-working-with-business.md) | Translating trader/risk manager language, asking right questions |
| 21 | [Anti-patterns & War Stories](modules/21-antipatterns.md) | Real cases of risk numbers going wrong |

## 🎓 Phase 7 — Capstone

Bring it all together.

| # | Module | Focus |
|---|--------|-------|
| 22 | [End-to-End Walkthrough](modules/22-capstone.md) | Design a full market risk data mart from scratch |

## 🏛️ Phase 8 — Vendor Systems (applied)

The applied layer. The previous modules taught the *theory* of a risk warehouse; this phase covers the *practice* of integrating real vendor systems against it. Phase 8 starts with a vendor-agnostic framework, then instantiates it across the three principal sub-shapes within the trading-and-risk-platform category: trade-of-record platforms (Murex and its peer Calypso), specialist analytics calculators (Polypaths), and market-data infrastructure (Quantserver). The four applied modules together cover the dominant vendor shapes a tier-1 bank's market-risk warehouse encounters. The framework remains extensible: future contributors can fork any of the four applied patterns to write the analogous module for Summit, Front Arena, Sophis, or any other vendor the firm encounters.

| # | Module | Focus |
|---|--------|-------|
| 23 | [Vendor Systems Framework](modules/23-vendor-systems-framework.md) | Vendor categories, the 6-step onboarding template, the catalogue table, where vendor data fits in the medallion architecture |
| 24 | [Murex (MX.3) Applied](modules/24-murex-applied.md) | Datamart extraction, identifier xref, Murex DQ checks, version-upgrade planning — the framework instantiated for the field's dominant trade-of-record platform |
| 25 | [Polypaths Applied](modules/25-polypaths-applied.md) | OAS / prepayment / key-rate-duration analytics, run-snapshot bitemporality, calibration-recalibration impact — the framework instantiated for a specialist analytics calculator |
| 26 | [Quantserver Applied](modules/26-quantserver-applied.md) | Streaming feed-handling and normalisation, tick-data storage choices, sequence-gap DQ — the framework instantiated for market-data infrastructure |
| 27 | [Calypso Applied](modules/27-calypso-applied.md) | Cross-asset capital-markets platform, cashflow-vs-accrual DQ surface, collateral and clearing integration — the framework instantiated for Murex's closest trade-of-record peer |

## Statistics Coverage

Statistics is **woven through the modules** rather than taught separately. The training does not have a dedicated "stats" phase; instead, each statistical concept is introduced exactly where the data shape demands it. By the end you will have learned, in context:

| Module | Stats topics introduced |
|--------|-------------------------|
| [M08 — Sensitivities](modules/08-sensitivities.md) | Partial derivatives intuition, finite difference vs. analytical methods, bucketing as discretisation |
| [M09 — Value at Risk](modules/09-value-at-risk.md) ⭐ | Distributions, quantiles, mean / variance / stddev, covariance, correlation, normal vs. fat-tailed, confidence intervals, volatility scaling, tail measures, backtesting (Kupiec, Christoffersen) |
| [M10 — Stress Testing](modules/10-stress-testing.md) | Scenario design, joint vs. marginal shocks, optimisation basics |
| [M11 — Market Data](modules/11-market-data.md) | Interpolation methods, PCA on curves |
| [M12 — Aggregation](modules/12-aggregation-additivity.md) ⭐ | Covariance, sub-additivity, coherent risk measures, why you can sum means but not standard deviations |
| [M14 — P&L Attribution](modules/14-pnl-attribution.md) | Taylor series expansion, partial derivatives applied to P&L explain |
| [M19 — Regulatory Context](modules/19-regulatory-context.md) | High-level expected shortfall, FRTB statistical machinery (IMCC, NMRF, PLA test) |
| [M22 — Capstone](modules/22-capstone.md) | Applied stats end-to-end inside a working risk mart |

> Module 13 (Bitemporality) is intentionally not a stats module — it is about temporal data modelling.

## Estimated Time per Module

Realistic part-time estimates (assuming you work the worked examples and at least some exercises). Ranges, not points — your background matters.

| # | Module | Hours (part-time) |
|---|--------|-------------------|
| 1 | [Market Risk Foundations](modules/01-market-risk-foundations.md) | 3–5 |
| 2 | [Securities Firm Organization](modules/02-securities-firm-organization.md) | 3–4 |
| 3 | [Trade Lifecycle](modules/03-trade-lifecycle.md) | 4–6 |
| 4 | [Financial Instruments Primer](modules/04-financial-instruments.md) | 6–8 |
| 5 | [Dimensional Modeling](modules/05-dimensional-modeling.md) | 6–8 |
| 6 | [Core Dimensions](modules/06-core-dimensions.md) | 6–8 |
| 7 | [Fact Tables of Market Risk](modules/07-fact-tables.md) | 8–10 |
| 8 | [Sensitivities Deep Dive](modules/08-sensitivities.md) | 6–8 |
| 9 | [Value at Risk](modules/09-value-at-risk.md) ⭐ | 8–12 |
| 10 | [Stress Testing](modules/10-stress-testing.md) | 5–7 |
| 11 | [Market Data & Risk Factors](modules/11-market-data.md) | 6–8 |
| 12 | [Aggregation & Additivity](modules/12-aggregation-additivity.md) ⭐ | 6–8 |
| 13 | [Time & Bitemporality](modules/13-time-bitemporality.md) ⭐ | 7–10 |
| 14 | [P&L Attribution](modules/14-pnl-attribution.md) | 6–8 |
| 15 | [Data Quality & Reconciliation](modules/15-data-quality.md) | 5–7 |
| 16 | [Lineage & Auditability](modules/16-lineage-auditability.md) | 4–6 |
| 17 | [Performance & Materialization](modules/17-performance-materialization.md) | 6–8 |
| 18 | [Architecture Patterns](modules/18-architecture-patterns.md) | 6–8 |
| 19 | [Regulatory Context](modules/19-regulatory-context.md) | 5–7 |
| 20 | [Working with the Business](modules/20-working-with-business.md) | 3–5 |
| 21 | [Anti-patterns & War Stories](modules/21-antipatterns.md) | 3–5 |
| 22 | [Capstone](modules/22-capstone.md) | 20–40 (depth-dependent) |
| 23 | [Vendor Systems Framework](modules/23-vendor-systems-framework.md) | 6–8 |
| 24 | [Murex (MX.3) Applied](modules/24-murex-applied.md) | 8–10 |
| 25 | [Polypaths Applied](modules/25-polypaths-applied.md) | 6–8 |
| 26 | [Quantserver Applied](modules/26-quantserver-applied.md) | 6–8 |
| 27 | [Calypso Applied](modules/27-calypso-applied.md) | 8–10 |
| | **Total** | **~185–270 hours** |

## Suggested Pace

| Phase | Suggested Time |
|-------|----------------|
| Phase 1 | ~1 week, light reading |
| Phase 2 | ~1–2 weeks, dense |
| Phase 3 | ~2–3 weeks, stats-heavy |
| Phase 4 | ~2 weeks |
| Phase 5 | ~1–2 weeks |
| Phase 6 | ~1 week |
| Phase 7 | ~1 week (or as long as you want — capstone depth is up to you) |
| Phase 8 | ~3–5 weeks (M23 is short; M24 and M27 are dense; M25 and M26 are narrower) |
| **Total** | **~10–16 weeks** part-time |

## Suggested Study Sequences

Three reader profiles. Pick the one that matches your goal — none of them is wrong, they just optimise for different outcomes.

### Sequential beginner

You're new to market risk and want the full picture. Work [M01](modules/01-market-risk-foundations.md) → [M22](modules/22-capstone.md) in order. Plan ~3 months part-time. Don't skip phases — the dimensional-modelling foundations (Phase 2) are what make the risk-measure modules (Phase 3) tractable.

### VaR-focused refresher

You already know dimensional modelling and want to go deep on VaR and the temporal data structures around it. Recommended path:

[M01](modules/01-market-risk-foundations.md) → [M07](modules/07-fact-tables.md) → [M08](modules/08-sensitivities.md) → [M09](modules/09-value-at-risk.md) → [M12](modules/12-aggregation-additivity.md) → [M13](modules/13-time-bitemporality.md) → [M22](modules/22-capstone.md)

This skips the lifecycle / instruments primer and jumps straight to fact tables, then the four flagship risk-data modules, then the capstone. ~40–60 hours.

### Architecture-focused

You're an engineer or architect and care about the warehouse, not the maths. Recommended path:

[M01](modules/01-market-risk-foundations.md) → [M02](modules/02-securities-firm-organization.md) → [M05](modules/05-dimensional-modeling.md) → [M06](modules/06-core-dimensions.md) → [M07](modules/07-fact-tables.md) → [M15](modules/15-data-quality.md) → [M16](modules/16-lineage-auditability.md) → [M17](modules/17-performance-materialization.md) → [M18](modules/18-architecture-patterns.md) → [M21](modules/21-antipatterns.md) → [M23](modules/23-vendor-systems-framework.md) → [M24](modules/24-murex-applied.md) → [M25](modules/25-polypaths-applied.md) → [M26](modules/26-quantserver-applied.md) → [M27](modules/27-calypso-applied.md)

This gives you the business framing, the dimensional core, the entire engineering-excellence phase, the war-stories module, and the applied vendor-onboarding phase that puts the architecture into practice against real systems — a trade-of-record platform (Murex), an analytics calculator (Polypaths), a market-data infrastructure platform (Quantserver), and Murex's closest trade-of-record peer (Calypso). Skim [M09](modules/09-value-at-risk.md) and [M13](modules/13-time-bitemporality.md) for the data shapes only. ~95–130 hours.

## Ready to Start?

[Begin with Module 1 →](modules/01-market-risk-foundations.md){ .md-button .md-button--primary }
