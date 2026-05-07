# Module 7 — The Fact Tables of Market Risk

!!! abstract "Module Goal"
    The major fact tables in risk, their grain, and example schemas. The most important module for a BI professional.

!!! note "Status: Outline"
    This module's content will be expanded during the training. The outline below shows what the module will cover.

## Outline

### 7.1 Trade Fact

*To be expanded.*

Grain: one row per trade event. Transactional fact. Columns and FKs.

### 7.2 Position Fact

*To be expanded.*

Grain: one row per (book × instrument × as-of-date). Periodic snapshot fact. Why we don't reconstruct from trades on the fly.

### 7.3 Cash Flow Fact

*To be expanded.*

Grain: one row per scheduled payment. Used for liquidity and settlement projections.

### 7.4 Sensitivity Fact

*To be expanded.*

Grain: one row per (trade or book × risk factor × tenor × as-of-date). Long format vs. wide format trade-offs.

### 7.5 Market Data Fact

*To be expanded.*

Grain: one row per (risk factor × tenor × as-of-date × snap-time). Bitemporal.

### 7.6 VaR Fact

*To be expanded.*

Grain: one row per (book × as-of-date × confidence × horizon × measure type).

### 7.7 Scenario P&L Fact

*To be expanded.*

Grain: one row per (book × scenario × as-of-date). Building block for VaR and stress.

### 7.8 Stress P&L Fact

*To be expanded.*

Grain: same shape as scenario P&L but scenarios are named/managed differently.

### 7.9 P&L Fact

*To be expanded.*

Grain: one row per (book × as-of-date × P&L component). Daily, attributed.

### 7.10 Limits & Utilization Fact

*To be expanded.*

Grain: one row per (book × limit type × as-of-date).

### 7.11 Backtesting Fact

*To be expanded.*

Grain: one row per (book × as-of-date) comparing predicted vs. actual P&L.

### 7.12 Choosing Snapshot vs. Transactional vs. Accumulating

*To be expanded.*

Kimball's three fact table types in risk context.

### 7.13 The most common grain mistakes

*To be expanded.*

Mixing trade-level and book-level rows; forgetting tenor; missing as-of-date.


## Key Takeaways

*To be filled in as content is written.*

## Glossary Terms Introduced

*To be filled in.*

---

[← Module 6 — Core Dimensions](06-core-dimensions.md){ .md-button } [Next: Module 8 — Sensitivities →](08-sensitivities.md){ .md-button .md-button--primary }
