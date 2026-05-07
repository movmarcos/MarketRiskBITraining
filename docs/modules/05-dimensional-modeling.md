# Module 5 — Dimensional Modeling Fundamentals

!!! abstract "Module Goal"
    Kimball's dimensional modeling — applied specifically to risk and finance data.

!!! note "Status: Outline"
    This module's content will be expanded during the training. The outline below shows what the module will cover.

## Outline

### 5.1 Why Dimensional Modeling

*To be expanded.*

Star schemas vs. 3NF. Why BI workloads need the former.

### 5.2 Facts and Dimensions

*To be expanded.*

Definitions, properties, the litmus tests.

### 5.3 Grain

*To be expanded.*

The most important concept. How to define grain rigorously.

### 5.4 Star vs. Snowflake

*To be expanded.*

When to normalize a dimension; when not to.

### 5.5 Surrogate vs. Natural Keys

*To be expanded.*

Why risk data almost always needs surrogates.

### 5.6 Slowly Changing Dimensions

*To be expanded.*

Type 1 (overwrite), Type 2 (versioning), Type 3 (limited history), Type 6 (hybrid). Examples for trader, book, instrument.

### 5.7 Conformed Dimensions

*To be expanded.*

Why every fact table sharing the same instrument dimension matters.

### 5.8 Degenerate Dimensions

*To be expanded.*

Trade ID lives on the fact, not in a dim — and why.

### 5.9 Junk Dimensions

*To be expanded.*

Combining low-cardinality flags.

### 5.10 Role-Playing Dimensions

*To be expanded.*

The same date dim used for trade_date, value_date, settlement_date.

### 5.11 Bridge Tables

*To be expanded.*

When you have many-to-many — e.g., trade-to-counterparty for novated trades.

### 5.12 Common Mistakes

*To be expanded.*

Mixing grains in one fact, missing surrogates, untracked SCD changes.


## Key Takeaways

*To be filled in as content is written.*

## Glossary Terms Introduced

*To be filled in.*

---

[← Module 4 — Financial Instruments](04-financial-instruments.md){ .md-button } [Next: Module 6 — Core Dimensions →](06-core-dimensions.md){ .md-button .md-button--primary }
