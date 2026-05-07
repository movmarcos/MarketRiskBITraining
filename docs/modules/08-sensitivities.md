# Module 8 — Sensitivities Deep Dive

!!! abstract "Module Goal"
    Greeks, DV01, CS01, bucketed sensitivities. How they're calculated, how they're stored, how they aggregate.

!!! note "Status: Outline"
    This module's content will be expanded during the training. The outline below shows what the module will cover.

## Outline

### 8.1 Recap from Module 1

*To be expanded.*

Sensitivity = partial derivative of value w.r.t. a market factor.

### 8.2 The Greeks

*To be expanded.*

Delta, Gamma, Vega, Theta, Rho — definitions, units, intuition.

### 8.3 Cross-Greeks

*To be expanded.*

Vanna, volga, charm. When they matter.

### 8.4 Rates Sensitivities

*To be expanded.*

DV01 / PV01, key rate durations, bucketed DV01.

### 8.5 Credit Sensitivities

*To be expanded.*

CS01, jump-to-default, spread01.

### 8.6 FX Sensitivities

*To be expanded.*

FX delta, FX vega, the smile risk.

### 8.7 Calculation Methods

*To be expanded.*

Analytical (closed form), finite difference (bump-and-revalue), AAD (algorithmic differentiation).

### 8.8 Storage: Long Format

*To be expanded.*

One row per (trade × risk factor × tenor). Pros, cons, example schema.

### 8.9 Storage: Wide Format

*To be expanded.*

Columns for delta, gamma, vega per risk factor. When acceptable.

### 8.10 FRTB SA Buckets

*To be expanded.*

How sensitivities are organized for standardized capital.

### 8.11 Aggregation Rules

*To be expanded.*

When can you sum sensitivities? (Same factor, same tenor, same currency, same shock convention.)

### 8.12 📊 Stats Detour — Partial Derivatives

*To be expanded.*

Intuitive picture, the tangent line, finite difference approximation.

### 8.13 Pitfalls

*To be expanded.*

Mixed shock conventions, missing tenor, currency mix, sign conventions.


## Key Takeaways

*To be filled in as content is written.*

## Glossary Terms Introduced

*To be filled in.*

---

[← Module 7 — Fact Tables](07-fact-tables.md){ .md-button } [Next: Module 9 — VaR →](09-value-at-risk.md){ .md-button .md-button--primary }
