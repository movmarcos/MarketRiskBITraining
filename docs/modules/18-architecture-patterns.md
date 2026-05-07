# Module 18 — Architecture Patterns

!!! abstract "Module Goal"
    How risk data systems are typically organized end-to-end.

!!! note "Status: Outline"
    This module's content will be expanded during the training. The outline below shows what the module will cover.

## Outline

### 18.1 The Layered Architecture

*To be expanded.*

Source → staging → integration → mart → reporting.

### 18.2 Trade Store / Position Store / Risk Store / Reporting Store

*To be expanded.*

The classic separation. Why each layer exists.

### 18.3 Risk Warehouse vs. Risk Mart

*To be expanded.*

Warehouse = canonical history; mart = use-case-specific subset.

### 18.4 Golden Source

*To be expanded.*

Per data domain: who's authoritative, why, and how it's enforced.

### 18.5 Batch vs. Intraday

*To be expanded.*

EOD process. Intraday risk for trading desks.

### 18.6 Event-Driven vs. Snapshot-Driven

*To be expanded.*

Kafka-based vs. nightly batch. Hybrid patterns.

### 18.7 Cloud Patterns

*To be expanded.*

Snowflake / BigQuery / Databricks / Redshift in risk contexts.

### 18.8 The Modern Stack in Risk

*To be expanded.*

dbt for transformation, Great Expectations for DQ, Atlan/Collibra for governance.

### 18.9 Reference Architecture Walkthrough

*To be expanded.*

End-to-end diagram of a typical bank's risk data platform.


## Key Takeaways

*To be filled in as content is written.*

## Glossary Terms Introduced

*To be filled in.*

---

[← Module 17 — Performance](17-performance-materialization.md){ .md-button } [Next: Module 19 — Regulatory Context →](19-regulatory-context.md){ .md-button .md-button--primary }
