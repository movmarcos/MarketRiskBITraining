# Module 21 — Anti-patterns & War Stories

!!! abstract "Module Goal"
    Real cases of risk numbers going wrong, and what BI/data could have prevented.

!!! note "Status: Outline"
    This module's content will be expanded during the training. The outline below shows what the module will cover.

## Outline

### 21.1 Summing VaR Across Books

*To be expanded.*

The classic. Why it's wrong, what to do instead.

### 21.2 Wrong-Grain Joins

*To be expanded.*

Joining a trade fact to a position fact without thinking. Catastrophic counts.

### 21.3 FX Double Conversion

*To be expanded.*

Converting a trade ccy to USD, then USD to GBP — using stale rates each time.

### 21.4 Stale Market Data

*To be expanded.*

Yesterday's vol surface flowing into today's risk. Missed by basic checks.

### 21.5 Late-Arriving Trades

*To be expanded.*

Trades booked T+1 not flowing into the T-as-of risk view.

### 21.6 Snapshot vs. Live Confusion

*To be expanded.*

Reporting hits a 'live' position table when it should hit the snapshot.

### 21.7 Mishandled Restatements

*To be expanded.*

Yesterday's report changes overnight. Audit trail gone.

### 21.8 Currency-Aware Thresholding

*To be expanded.*

A $1M tolerance applied to JPY positions. Constant false positives.

### 21.9 The 'Helpful' DBA

*To be expanded.*

Manual production fix. No record. Days to discover. Months to unwind.

### 21.10 Untracked Spreadsheet Outputs

*To be expanded.*

Numbers leaving the warehouse. Modified offline. Re-presented as truth.

### 21.11 Hierarchy Drift

*To be expanded.*

Book moved desks without SCD2 tracking. Historical reports re-attribute silently.

### 21.12 What All These Have in Common

*To be expanded.*

Lessons: grain rigor, conformed dimensions, bitemporality, lineage, controls.


## Key Takeaways

*To be filled in as content is written.*

## Glossary Terms Introduced

*To be filled in.*

---

[← Module 20 — Working with Business](20-working-with-business.md){ .md-button } [Next: Module 22 — Capstone →](22-capstone.md){ .md-button .md-button--primary }
