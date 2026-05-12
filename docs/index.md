---
hide:
  - navigation
  - toc
---

<div class="mr-hero" markdown>

<p class="mr-hero__eyebrow">Market Risk · BI · Data Engineering</p>

<h1 class="mr-hero__title">From SQL writer to risk-data professional.</h1>

<p class="mr-hero__subtitle">A structured, practitioner-grade training on market risk for the data engineers, BI developers, and analytics teams who model, store, and serve the numbers a trading desk runs on.</p>

[Start with Module 01](modules/01-market-risk-foundations.md){ .mr-hero__cta }
[See the curriculum](curriculum.md){ .mr-hero__cta .mr-hero__cta--ghost }

</div>

<div class="mr-stats" markdown>

<div class="mr-stat" markdown>
<p class="mr-stat__value">25</p>
<p class="mr-stat__label">Modules</p>
</div>

<div class="mr-stat" markdown>
<p class="mr-stat__value">8</p>
<p class="mr-stat__label">Phases</p>
</div>

<div class="mr-stat" markdown>
<p class="mr-stat__value">8–12</p>
<p class="mr-stat__label">Weeks part-time</p>
</div>

<div class="mr-stat" markdown>
<p class="mr-stat__value">SQL · Python</p>
<p class="mr-stat__label">Tooling</p>
</div>

</div>

## Why this training exists

Most market-risk training is written for **risk managers** (who know the business and need the math) or for **quants** (who need the models). Almost nothing is written for the **data professional** whose job is to source, model, store, and serve the data that all of the above depend on.

This training fills that gap. The focus is always on table structures, grain, dimensions, aggregation rules, and reconciliation — framed inside the business context that makes the answers obvious.

## Pick a phase

<div class="mr-phases" markdown>

[<span class="mr-phase__num">Phase 01 · Modules 01–04</span>
<span class="mr-phase__title">Foundations</span>
<span class="mr-phase__desc">Market risk basics, how a securities firm is organised, the trade lifecycle, and the universe of financial instruments.</span>
<span class="mr-phase__meta">→ Start here</span>](modules/01-market-risk-foundations.md){ .mr-phase }

[<span class="mr-phase__num">Phase 02 · Modules 05–07</span>
<span class="mr-phase__title">Data Modeling Core</span>
<span class="mr-phase__desc">Dimensional modeling under regulatory scrutiny: SCDs, conformed dimensions, fact-table types and grain.</span>
<span class="mr-phase__meta">→ Modeling fundamentals</span>](modules/05-dimensional-modeling.md){ .mr-phase }

[<span class="mr-phase__num">Phase 03 · Modules 08–10</span>
<span class="mr-phase__title">Risk Measures</span>
<span class="mr-phase__desc">Sensitivities and the Greeks, Value at Risk and Expected Shortfall, and stress testing — with the data shapes that store them.</span>
<span class="mr-phase__meta">→ The numbers that matter</span>](modules/08-sensitivities.md){ .mr-phase }

[<span class="mr-phase__num">Phase 04 · Modules 11–14</span>
<span class="mr-phase__title">Cross-Cutting Concepts</span>
<span class="mr-phase__desc">Market data lineage, additivity (and why VaR doesn't sum), bitemporality, and P&amp;L attribution.</span>
<span class="mr-phase__meta">→ Concepts that span every module</span>](modules/11-market-data.md){ .mr-phase }

[<span class="mr-phase__num">Phase 05 · Modules 15–18</span>
<span class="mr-phase__title">Engineering Excellence</span>
<span class="mr-phase__desc">Data quality, lineage and auditability, performance and materialization, and reference architectures for risk warehouses.</span>
<span class="mr-phase__meta">→ Production-grade discipline</span>](modules/15-data-quality.md){ .mr-phase }

[<span class="mr-phase__num">Phase 06 · Modules 19–21</span>
<span class="mr-phase__title">Business-Aligned Pro</span>
<span class="mr-phase__desc">Regulatory context (Basel, FRTB, BCBS 239), translating business asks into data specs, and recognising anti-patterns.</span>
<span class="mr-phase__meta">→ Talk to the desk</span>](modules/19-regulatory-context.md){ .mr-phase }

[<span class="mr-phase__num">Phase 07 · Module 22</span>
<span class="mr-phase__title">Capstone</span>
<span class="mr-phase__desc">Design and implement a small risk reporting mart end-to-end, with a rubric and reference-solution outline.</span>
<span class="mr-phase__meta">→ Put it together</span>](modules/22-capstone.md){ .mr-phase }

[<span class="mr-phase__num">Phase 08 · Modules 23–25</span>
<span class="mr-phase__title">Vendor Systems (applied)</span>
<span class="mr-phase__desc">A framework for onboarding any vendor system to your warehouse, with applied case studies for Murex (MX.3) and Polypaths fixed-income analytics.</span>
<span class="mr-phase__meta">→ Real-world systems</span>](modules/23-vendor-systems-framework.md){ .mr-phase }

</div>

## What's covered, what's not

| In scope | Out of scope |
|----------|--------------|
| Classical historical, parametric, and Monte Carlo VaR | Full pricing-model derivations (Black–Scholes calibration, SABR, local vol) |
| Sensitivities and the Greeks at conceptual + data-shape level | Detailed FRTB capital-calculation implementation |
| FRTB at conceptual level (SA bucketing, IMA / PLA framework) | Real-time / streaming risk |
| Dimensional modelling for risk warehouses | ML-augmented risk modelling |
| Bitemporality, lineage, data quality | Vendor product training (Bloomberg, Refinitiv specifics) |
| The regulatory landscape (Basel, FRTB, BCBS 239) | Regulatory exam prep (CFA / FRM / PRM) |
| Capstone project — design a small risk mart end-to-end | |

The training treats the data professional's perspective as primary. Where the maths matters for the data shape, it's covered in context; where it doesn't, it's deferred to specialist sources.

## How to use this site

- **Sequential learners** — start with [Module 01](modules/01-market-risk-foundations.md) and work through to [Module 22](modules/22-capstone.md).
- **Reference users** — jump straight to a topic via the sidebar or search.
- **Quick lookups** — the [glossary](glossary.md) covers terms you'll hear daily.
- **Planning your time** — see the [curriculum overview](curriculum.md) for per-module hour estimates and three suggested study sequences (sequential beginner, VaR-focused refresher, architecture-focused).

Each module follows the same eight-section structure: **learning objectives**, **why it matters**, **core concepts**, **worked examples** (SQL + Python), **common pitfalls**, **exercises with solutions**, **further reading**, and a **recap**.
