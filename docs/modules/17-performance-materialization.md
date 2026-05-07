# Module 17 — Performance & Materialization Strategy

!!! abstract "Module Goal"
    Risk data is huge. Strategies for making it queryable.

!!! note "Status: Outline"
    This module's content will be expanded during the training. The outline below shows what the module will cover.

## Outline

### 17.1 The Scale of Risk Data

*To be expanded.*

Typical row counts: trades, positions, sensitivities, scenarios.

### 17.2 Partitioning Strategies

*To be expanded.*

By as-of-date (almost always). By legal entity. By asset class.

### 17.3 Columnar Storage

*To be expanded.*

Why Parquet / columnar warehouses dominate.

### 17.4 Aggregate Tables

*To be expanded.*

Pre-computed roll-ups: book × asset_class × date, etc.

### 17.5 Materialized Views

*To be expanded.*

When to use, refresh strategies, staleness.

### 17.6 OLAP Cubes

*To be expanded.*

Conceptual model. When still relevant.

### 17.7 Indexing in Columnar Worlds

*To be expanded.*

Clustering, sort keys, zone maps.

### 17.8 Caching at the BI Layer

*To be expanded.*

Tableau extracts, Power BI imports, query caches.

### 17.9 The Pre-Compute vs. On-the-Fly Decision

*To be expanded.*

Cost model. Latency expectations. Refresh windows.

### 17.10 Real-Time / Intraday Risk

*To be expanded.*

Different architecture entirely. Brief overview.


## Key Takeaways

*To be filled in as content is written.*

## Glossary Terms Introduced

*To be filled in.*

---

[← Module 16 — Lineage](16-lineage-auditability.md){ .md-button } [Next: Module 18 — Architecture →](18-architecture-patterns.md){ .md-button .md-button--primary }
