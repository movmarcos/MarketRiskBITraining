# Module 9 — Value at Risk (VaR) ⭐

!!! abstract "Module Goal"
    The big one. Three methodologies, scenario P&L, ES, backtesting — with the statistics woven in.

!!! note "Status: Outline"
    This module's content will be expanded during the training. The outline below shows what the module will cover.

## Outline

### 9.1 What VaR Is — Precisely

*To be expanded.*

The X% confidence loss threshold over Y days. Why both numbers matter.

### 9.2 📊 Stats Detour — Distributions

*To be expanded.*

Normal, fat-tailed, empirical. Why financial returns aren't normal.

### 9.3 📊 Stats Detour — Percentiles & Quantiles

*To be expanded.*

VaR is literally a percentile. Worked example.

### 9.4 Historical Simulation VaR

*To be expanded.*

Replay historical moves on today's portfolio. Pros, cons, data needs.

### 9.5 Parametric VaR

*To be expanded.*

Normal distribution assumption, covariance matrix.

### 9.6 📊 Stats Detour — Variance, Covariance, Correlation

*To be expanded.*

The matrix that makes parametric VaR work.

### 9.7 Monte Carlo VaR

*To be expanded.*

Simulating thousands of scenarios from a model.

### 9.8 Scenario P&L Vectors — The Foundational Data

*To be expanded.*

The data structure VaR is computed *from*. Why storing this matters.

### 9.9 📊 Stats Detour — Volatility Scaling (√t Rule)

*To be expanded.*

Going from 1-day to 10-day VaR. Assumptions and limits.

### 9.10 Why VaR is Non-Additive

*To be expanded.*

The diversification benefit. Subadditivity. VaR(A+B) ≤ VaR(A)+VaR(B).

### 9.11 Component VaR / Marginal VaR / Incremental VaR

*To be expanded.*

Attributing portfolio VaR to constituents. Data structures for each.

### 9.12 Expected Shortfall (ES / CVaR)

*To be expanded.*

The FRTB replacement. Coherent risk measure. Same data, different aggregation.

### 9.13 Liquidity Horizons under FRTB

*To be expanded.*

Different risk factors get different horizons (10d–250d).

### 9.14 Backtesting

*To be expanded.*

Comparing predicted VaR to actual P&L. Hypothetical vs. actual P&L.

### 9.15 📊 Stats Detour — Backtesting Statistics

*To be expanded.*

Kupiec test, traffic light (green/amber/red), exception counting.

### 9.16 The VaR Fact Table — Full Schema

*To be expanded.*

Putting it all together. Every column, every FK.

### 9.17 Pitfalls

*To be expanded.*

Summing VaRs, ignoring liquidity horizons, stale historical windows, regime changes.


## Key Takeaways

*To be filled in as content is written.*

## Glossary Terms Introduced

*To be filled in.*

---

[← Module 8 — Sensitivities](08-sensitivities.md){ .md-button } [Next: Module 10 — Stress Testing →](10-stress-testing.md){ .md-button .md-button--primary }
