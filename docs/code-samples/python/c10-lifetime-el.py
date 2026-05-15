# Module: Credit M10 — Expected Loss
# Purpose:  Compute the lifetime Expected Loss (EL) term-structure walk for a
#           single 5-year amortising term loan. The walk is the discrete-time
#           workhorse of IFRS 9 / CECL ECL: for each future year, multiply
#           the marginal probability of default by the loss given default by
#           the exposure at that future date, then discount back to today and
#           sum across years. The 12-month EL is also reported for comparison.
# Caveat:   This is a *teaching* implementation. Production lifetime ECL
#           handles drawdown patterns for revolvers, time-varying LGD,
#           survival-probability adjustments (a default in year 3 is only
#           possible if the loan has survived years 1 and 2), and a discount
#           rate that for IFRS 9 is the *original effective interest rate* of
#           the instrument. The numbers below illustrate the *shape* of a
#           lifetime EL walk, not a regulatorily defensible figure.
# Depends:  Python 3.11+, numpy only.
# Run:      python docs/code-samples/python/c10-lifetime-el.py

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LoanSpec:
    """A stylised amortising term loan.

    Conventions:
      - The principal amortises linearly from `notional_usd` at t=0 to zero
        at maturity. Realistic loans amortise on a mortgage-style schedule;
        the linear schedule keeps the arithmetic visible.
      - LGD is constant across the life. In practice LGD has a small term
        structure (recovery values can drift with collateral revaluation
        cycles) but the simplification is conventional for first-pass ECL.
      - The discount rate is intended as a proxy for the original effective
        interest rate of the loan; under IFRS 9 the EIR is the contractual
        rate adjusted for fees and is fixed at origination.
    """

    notional_usd: float
    tenor_years: int
    lgd: float
    discount_rate: float


def amortising_ead_schedule(spec: LoanSpec) -> np.ndarray:
    """Return the EAD at the *start* of each forward year.

    For a 5-year linear amortiser the schedule is [N, 0.8N, 0.6N, 0.4N, 0.2N].
    The exposure at the start of year t is what would be owed if default
    occurred during year t; the simplification assumes default occurs at the
    start of the year (so the year's full opening balance is at risk).
    """
    steps = np.arange(spec.tenor_years)
    remaining_fraction = 1.0 - steps / spec.tenor_years
    return spec.notional_usd * remaining_fraction


def lifetime_el_walk(
    spec: LoanSpec,
    marginal_pd: np.ndarray,
) -> dict[str, np.ndarray | float]:
    """Compute the per-year and lifetime Expected Loss walk.

    Returns a dictionary with the per-year arrays (ead, marginal_el,
    discounted_el) and the headline lifetime_el and twelve_month_el scalars.

    Arithmetic per year t (1-indexed):
        ead_t           = opening balance at start of year t
        marginal_el_t   = marginal_pd_t * lgd * ead_t
        discounted_el_t = marginal_el_t / (1 + discount_rate) ** t
        lifetime_el     = sum over t of discounted_el_t

    The 12-month EL uses the year-1 marginal PD and the year-1 opening EAD,
    undiscounted (the 12m horizon is short enough that the IFRS 9 convention
    typically does not discount).
    """
    if marginal_pd.shape != (spec.tenor_years,):
        raise ValueError(
            f"marginal_pd must be length {spec.tenor_years}, got {marginal_pd.shape}"
        )
    if not np.all((marginal_pd >= 0) & (marginal_pd <= 1)):
        raise ValueError("marginal_pd must be in [0, 1]")
    if not 0 <= spec.lgd <= 1:
        raise ValueError("LGD must be in [0, 1]")

    ead = amortising_ead_schedule(spec)
    marginal_el = marginal_pd * spec.lgd * ead
    discount_factors = (1.0 + spec.discount_rate) ** -np.arange(1, spec.tenor_years + 1)
    discounted_el = marginal_el * discount_factors
    lifetime_el = float(discounted_el.sum())
    twelve_month_el = float(marginal_pd[0] * spec.lgd * ead[0])

    return {
        "ead": ead,
        "marginal_pd": marginal_pd,
        "marginal_el": marginal_el,
        "discounted_el": discounted_el,
        "lifetime_el": lifetime_el,
        "twelve_month_el": twelve_month_el,
    }


def format_report(spec: LoanSpec, walk: dict[str, np.ndarray | float]) -> str:
    """Render the walk as a human-readable table."""
    lines = [
        "Lifetime Expected Loss walk — 5y amortising term loan",
        "=" * 62,
        f"  Notional (t=0)            = ${spec.notional_usd:>14,.0f}",
        f"  Tenor                     = {spec.tenor_years} years",
        f"  LGD (constant)            = {spec.lgd:.2%}",
        f"  Discount rate (EIR proxy) = {spec.discount_rate:.2%}",
        "",
        "  year | opening EAD       | marginal PD | marginal EL      | discounted EL",
        "  -----+-------------------+-------------+------------------+-----------------",
    ]
    ead = walk["ead"]
    marginal_pd = walk["marginal_pd"]
    marginal_el = walk["marginal_el"]
    discounted_el = walk["discounted_el"]
    for year_index in range(spec.tenor_years):
        lines.append(
            f"   {year_index + 1:>3} | ${ead[year_index]:>14,.0f}   |   {marginal_pd[year_index]:>7.2%}   | ${marginal_el[year_index]:>13,.0f}   | ${discounted_el[year_index]:>13,.0f}"
        )
    lines.extend(
        [
            "",
            f"  Lifetime EL (sum of discounted EL) = ${walk['lifetime_el']:>14,.0f}",
            f"  12-month EL (year-1, undiscounted) = ${walk['twelve_month_el']:>14,.0f}",
            "",
            f"  Lifetime / 12-month ratio          = {walk['lifetime_el'] / walk['twelve_month_el']:>6.2f}x",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    spec = LoanSpec(
        notional_usd=10_000_000.0,
        tenor_years=5,
        lgd=0.45,
        discount_rate=0.05,
    )
    # Deteriorating credit: marginal PD ramps from 80bps in year 1 to 250bps in year 5.
    marginal_pd = np.array([0.0080, 0.0120, 0.0170, 0.0210, 0.0250])

    walk = lifetime_el_walk(spec, marginal_pd)
    print(format_report(spec, walk))
