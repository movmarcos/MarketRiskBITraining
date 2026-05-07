# Curriculum Overview

The training is structured as **22 modules** across **7 phases**, taking you from beginner to a confident, business-aligned BI professional in market risk.

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

## Statistics Coverage

Statistics is **woven through the modules** rather than taught separately. By the end you will have learned, in context:

- **Module 8 (Sensitivities):** partial derivatives intuition, finite difference vs. analytical methods
- **Module 9 (VaR):** distributions, percentiles, mean/variance/stddev, covariance, correlation, normal vs. fat-tailed, confidence intervals, volatility scaling, tail risk, backtesting statistics (Kupiec test)
- **Module 10 (Stress):** scenario design, joint vs. marginal shocks, optimization basics
- **Module 11 (Market Data):** interpolation methods, PCA on curves
- **Module 12 (Aggregation):** why you can sum means but not standard deviations
- **Module 14 (P&L Attribution):** Taylor series expansion (gentle introduction)

## Suggested Pace

| Phase | Suggested Time |
|-------|----------------|
| Phase 1 | ~1 week, light reading |
| Phase 2 | ~1–2 weeks, dense |
| Phase 3 | ~2–3 weeks, stats-heavy |
| Phase 4 | ~2 weeks |
| Phase 5 | ~1–2 weeks |
| Phase 6 | ~1 week |
| Phase 7 | ~1 week |
| **Total** | **~8–12 weeks** part-time |

## Ready to Start?

[Begin with Module 1 →](modules/01-market-risk-foundations.md){ .md-button .md-button--primary }
