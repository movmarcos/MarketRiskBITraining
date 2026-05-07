# Module 1 — Market Risk Foundations

!!! abstract "Module Goal"
    Understand what market risk *is*, why the function exists, who cares about it, and the regulatory landscape that shapes everything downstream — including the data you'll model.

## 1.1 What Is Market Risk?

**Market risk** is the risk of loss from movements in market prices. It's distinct from:

- **Credit risk** — risk that a counterparty defaults
- **Operational risk** — risk from process, people, or system failures
- **Liquidity risk** — risk of being unable to fund or unwind positions

Market risk specifically covers losses from changes in:

- **Interest rates** — yield curves, basis spreads
- **FX rates** — currency movements
- **Equity prices** — single names and indices
- **Credit spreads** — bond and CDS spreads (the *spread* component, not default itself)
- **Commodity prices** — oil, gas, metals, agriculturals
- **Volatility** — implied vol surfaces (a major risk for options books)

## 1.2 Why the Function Exists

Three fundamental reasons:

1. **Internal risk management.** A trading firm must know how much it can lose. Without measurement, you cannot manage.
2. **Capital adequacy.** Regulators require firms to hold capital against market risk. The amount is calculated from market risk measures.
3. **Limits & governance.** Each trader, desk, and division has limits (VaR limits, sensitivity limits, stress limits). Breaches must be detected and escalated.

## 1.3 The Risk Function — Independent by Design

Market risk sits in the **2nd line of defense** (we cover this in detail in [Module 2](02-securities-firm-organization.md)). The key principle: **independence from the front office**.

A trader has a direct financial incentive to under-report risk. The risk function exists to provide an independent, challenger view. This independence is reflected in:

- Separate reporting lines (Risk reports to a CRO, not to trading heads)
- Separate systems (Risk has its own data warehouse and engines)
- Separate calculations (Risk re-prices and re-computes, doesn't trust FO numbers blindly)

!!! info "Why this matters for BI"
    The independence requirement directly shapes data architecture. You'll often have **two parallel data flows** — one in the FO ecosystem, one in the Risk ecosystem — that must reconcile. Understanding why this duplication exists prevents you from "simplifying" it away.

## 1.4 Key Stakeholders

| Stakeholder | What They Care About |
|-------------|---------------------|
| **Traders** | Their book's P&L, sensitivities (Greeks), limits headroom |
| **Risk Managers** | VaR, stress, limit breaches, concentration, tail risk |
| **CRO / Senior Risk** | Aggregate exposure, regulatory capital, board reporting |
| **Finance** | P&L reconciliation, capital, regulatory submissions |
| **Regulators** | FRTB compliance, model approval, ad-hoc requests |
| **Internal Audit** | Controls, lineage, evidence, independence |

Each consumes the same underlying data through different lenses. **Conformed dimensions** ([Module 6](06-core-dimensions.md)) are how a single warehouse serves all of them.

## 1.5 Regulatory Landscape (Brief Tour)

You don't need to be a regulator, but knowing *why* a report exists makes you 10× more useful.

### Basel Framework

The Basel Committee on Banking Supervision sets global standards:

- **Basel II (2004)** — introduced the Internal Models Approach (IMA) for market risk; firms could use their own VaR models with regulator approval.
- **Basel 2.5 (2009, post-GFC)** — added **Stressed VaR (sVaR)** and **IRC** (Incremental Risk Charge) after VaR alone was shown to underestimate crisis losses.
- **Basel III** — broader bank capital framework; market risk piece evolved into FRTB.

### FRTB — The Current Regime

**FRTB (Fundamental Review of the Trading Book)** is the current market risk capital framework. Key shifts:

- **VaR replaced by Expected Shortfall (ES)** at 97.5% confidence
- **Liquidity horizons** vary by risk factor (10d to 250d)
- **Standardized Approach (SA)** is now meaningful — every firm computes it, even IMA-approved firms
- **Internal Models Approach (IMA)** has stricter approval — desk-level, not firm-level
- **Non-Modellable Risk Factors (NMRF)** get punitive capital treatment
- **P&L Attribution Test** — daily test that risk model P&L matches actual P&L within tolerance

### Other Regimes Worth Knowing

- **IFRS 9 / IFRS 13** — accounting standards governing fair value measurement
- **MiFID II** — EU markets regulation (transaction reporting, best execution)
- **Dodd-Frank** — US equivalent (Volcker rule, swap reporting)
- **CCAR / DFAST** — US stress testing for large banks
- **EBA Stress Tests** — EU equivalent

!!! tip "Regulator-driven data demands"
    Most "weird" things in your warehouse exist because of a regulator. Bitemporality? Required to reproduce historical reports. Granular trade-level storage? Required for reg reporting. Multiple P&L flavors? Required for the P&L attribution test.

## 1.6 Risk Measures at a Glance

The major measures you'll model. We deep-dive on each later.

| Measure | What It Measures | Module |
|---------|------------------|--------|
| **Sensitivities (Greeks, DV01)** | How value changes for a small market move | [Module 8](08-sensitivities.md) |
| **VaR** | Loss not expected to be exceeded with X% confidence | [Module 9](09-value-at-risk.md) |
| **Expected Shortfall (ES)** | Average loss in the worst (1-X)% of cases | [Module 9](09-value-at-risk.md) |
| **Stress P&L** | Loss under specific defined scenarios | [Module 10](10-stress-testing.md) |
| **IRC** | Default and migration risk for credit positions | [Module 19](19-regulatory-context.md) |

## 1.7 📊 Stats Detour — Risk, Return, Loss Distributions

Just an intuitive primer; we go deeper in [Module 9](09-value-at-risk.md).

- **Return** = change in value over a period, often expressed as a percentage.
- **Risk** = uncertainty about future returns, typically captured by the **distribution** of possible returns.
- **Loss distribution** = the distribution of P&L outcomes, usually with losses on one side and gains on the other.

Most risk measures are **summaries of this distribution**:

- **VaR** is a percentile of it (the 99th percentile loss, for example)
- **ES** is the average beyond that percentile
- **Stress P&L** is a single point on it (under a specific scenario)
- **Sensitivities** describe its *shape* near today's market

Holding this picture in your head — *every risk measure is a summary of a P&L distribution* — is the single most useful intuition in market risk.

## 1.8 Common Misconceptions

!!! warning "Things to unlearn before going further"
    - **"VaR tells you the worst case."** It doesn't. It tells you a threshold; losses *beyond* it are by definition not bounded by VaR. That's why ES exists.
    - **"More data = better risk numbers."** Not always. Historical VaR with 10 years of data may include irrelevant regimes. Most banks use 1–2 years.
    - **"Risk and Finance should always agree."** They use different bases (clean vs. dirty P&L, different snap times, different inclusion rules). Reconciliation is structural, not a bug.
    - **"Sensitivities can just be summed."** They can — within a risk factor and bucket. But mixing currencies, mixing tenors, or summing across different shock conventions silently produces garbage.

## 1.9 Key Takeaways

- Market risk = loss from market price moves (rates, FX, equity, credit, commodity, vol).
- The function is **independent by design**, which creates parallel data flows.
- Regulators (Basel, FRTB, IFRS) drive most of the data demands you'll see.
- Every risk measure is a summary of a **P&L distribution** — keep that mental picture.
- Stakeholders (traders, risk managers, CRO, Finance, regulators) all consume the same data through different lenses.

## 1.10 Glossary Terms Introduced

CRO, FRTB, IMA, SA, VaR, ES, IRC, NMRF, sVaR, P&L Attribution Test, Basel.
See the [glossary](../glossary.md) for definitions.

---

[← Curriculum](../curriculum.md){ .md-button } [Next: Module 2 — How a Securities Firm is Organized →](02-securities-firm-organization.md){ .md-button .md-button--primary }
