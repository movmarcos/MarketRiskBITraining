# Module Template

> This file is the canonical module template. It is not part of the site nav. Copy it when starting a new module.

This template demonstrates every formatting block used across the curriculum. Replace each placeholder with module-specific content. Keep the eight top-level sections and their order.

---

## 1. Learning objectives

By the end of this module, you should be able to:

- **Define** the key terms introduced (replace with measurable verb + concept).
- **Explain** the relationships between [concept A] and [concept B].
- **Compute** [a specific quantity] from a typical input data set.
- **Identify** the most common pitfalls when implementing [topic] in production.
- **Apply** [technique] to a realistic BI/data-engineering scenario.
- **Evaluate** trade-offs between [approach 1] and [approach 2].

## 2. Why this matters

Open with a paragraph that grounds the topic in the daily life of a BI or data professional working in market risk. What problem does this knowledge unlock? Who relies on it (traders, risk managers, regulators, finance)?

A second paragraph should connect the module to upstream and downstream concerns: which earlier modules feed into it, and which later modules build on it. Reference real-world consequences of getting this wrong — failed regulatory submissions, mis-stated P&L, missed limit breaches.

Optionally a third paragraph framing the *practitioner* angle: what will a reader actually do differently after reading this?

## 3. Core concepts

### 3.1 Concept one

Explain the first sub-concept. Use prose, then reinforce with a diagram or table.

```mermaid
flowchart LR
    A[Trade capture] --> B[Position aggregation]
    B --> C[Risk measure]
    C --> D[Reporting layer]
```

### 3.2 Concept two

Use admonitions to highlight definitions, asides, and caveats:

!!! info "Definition: placeholder term"
    A *placeholder term* is a stand-in concept used in this template only. Replace with the real definition in your module. Definitions should be one or two sentences and link to the glossary entry.

### 3.3 A reference table

| Term            | Symbol | Typical units | Notes                              |
| --------------- | ------ | ------------- | ---------------------------------- |
| Spot price      | \(S\)  | currency      | Mark-to-market input               |
| Volatility      | \(\sigma\) | annualised %  | Historical or implied              |
| Time to expiry  | \(T\)  | years         | Day-count convention matters       |

### 3.4 A bit of math

Inline math renders via arithmatex: the standard normal density is \(\phi(x) = \frac{1}{\sqrt{2\pi}} e^{-x^2/2}\).

Display math:

$$
\text{VaR}_\alpha(L) = \inf\{ l \in \mathbb{R} : P(L > l) \leq 1 - \alpha \}
$$

## 4. Worked examples

### Example 1 — SQL: aggregating positions

A typical BI task is rolling a fact table up to a reporting grain. The snippet below would normally be inlined, but for reusable code prefer the snippets extension:

```sql
-- Inline example: sum notional by book and as-of date
SELECT
    book_id,
    as_of_date,
    SUM(notional_usd) AS total_notional_usd
FROM fact_position
WHERE as_of_date = DATE '2026-05-07'
GROUP BY book_id, as_of_date;
```

For longer or shared snippets, reference an external file via `pymdownx.snippets`. The path is relative to `docs/`:

```sql
--8<-- "code-samples/sql/example.sql"
```

Walk through the snippet line-by-line: what each clause does, what assumptions it makes about the schema, and how it would behave with bitemporal data.

### Example 2 — Python: a numerical calculation

```python
import numpy as np

def historical_var(pnl: np.ndarray, alpha: float = 0.99) -> float:
    """One-day historical VaR at confidence level alpha."""
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    losses = -np.asarray(pnl)
    return float(np.quantile(losses, alpha))


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    sample = rng.normal(0, 1_000_000, size=500)
    print(f"99% 1-day VaR: {historical_var(sample):,.0f}")
```

You can also pull this from the shared snippets directory:

```python
--8<-- "code-samples/python/example.py"
```

Discuss the result: what does the number mean, what are the units, and how would it differ under a parametric assumption?

## 5. Common pitfalls

!!! warning "Watch out"
    1. **Mixing as-of dates with effective dates.** Bitemporal models require both — conflating them produces silent data corruption.
    2. **Currency conversion at the wrong grain.** Convert at the trade or position level using the trade-date FX, not at the aggregate.
    3. **Implicit time-zone assumptions.** Always store timestamps in UTC and convert for display only.
    4. **Sign conventions for P&L vs. loss.** A positive number can mean profit *or* loss depending on the table — document it.
    5. **Treating VaR as additive across desks.** Risk measures are subadditive at best; do not sum them.

## 6. Exercises

1. **Conceptual.** In your own words, explain the difference between [term A] and [term B]. Which one does the front office care about, and why?

    ??? note "Solution"
        Term A refers to ... Term B refers to ... The front office typically focuses on Term A because it drives intraday hedging decisions, whereas Term B is an end-of-day reporting concept.

2. **SQL.** Given a `fact_position` table with columns `(book_id, instrument_id, as_of_date, notional_usd)`, write a query that returns the top 5 books by absolute notional for a given date.

    ??? note "Solution"
        ```sql
        SELECT book_id, SUM(ABS(notional_usd)) AS gross_notional
        FROM fact_position
        WHERE as_of_date = DATE '2026-05-07'
        GROUP BY book_id
        ORDER BY gross_notional DESC
        LIMIT 5;
        ```

3. **Python.** Modify `historical_var` from Example 2 to also return the index of the loss observation that defines the VaR threshold. Why might you want this?

    ??? note "Solution"
        Return `(var_value, np.argsort(losses)[int(np.ceil(alpha * len(losses))) - 1])`. The index lets you trace the VaR back to a specific historical day, which is useful for backtesting and for explaining drivers to risk managers.

4. **Design.** Sketch a star schema for [topic-specific scenario]. Identify at least one slowly changing dimension and justify the SCD type you would choose.

    ??? note "Solution"
        A reasonable design includes a `dim_book` (SCD type 2 to preserve org-hierarchy history), `dim_instrument` (SCD type 2 for reference-data changes), `dim_date`, and a `fact_position` at trade/day grain. Type 2 is appropriate where downstream reports need point-in-time correctness.

## 7. Further reading

- Hull, J. *Options, Futures, and Other Derivatives* — chapter most relevant to this module.
- Kimball, R. & Ross, M. *The Data Warehouse Toolkit* — relevant chapter on the modeling pattern used here.
- Basel Committee on Banking Supervision, *[relevant standard]*, latest version.
- Vendor documentation: [Snowflake / Postgres / etc. feature page].
- Internal: link to a related team wiki page or runbook.
- Blog post or paper that explains a specific pitfall well.

## 8. Recap

You should now be able to:

- Define the key terms introduced in this module and locate them in the glossary.
- Explain why this topic matters for a BI/data professional in market risk.
- Implement the core SQL or Python pattern shown in the worked examples.
- Recognise the common pitfalls and avoid them in your own work.
- Connect this module to its predecessors and successors in the curriculum.
