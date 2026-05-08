# Module: 11 — Market Data & Risk Factors
# Purpose:  Bootstrap a zero curve from a small set of par swap rates.
#           Demonstrates the core idea — successive substitution from short
#           tenors out — without the day-count, compounding, and basis-curve
#           machinery that a production engine requires.
# Depends:  Python 3.11+ (no third-party libraries).
# Run:      python docs/code-samples/python/11-bootstrap-curve.py
#
# Reproducibility note: the par-rate inputs here are static. In production
# the par rates would come from fact_market_data at a fixed
# (business_date, as_of_timestamp) snapshot, joined to dim_market_factor
# for tenor metadata. The bootstrap output would be persisted to the same
# fact_market_data with a `derivation_method = 'BOOTSTRAP_LINEAR'` flag and
# a lineage pointer to the par-rate source rows. Different bootstrap methods
# (linear-on-zero, log-linear-on-discount-factor, monotone-cubic-spline)
# produce materially different zero rates between knot points; the method
# choice belongs in the warehouse alongside the curve.

from __future__ import annotations

import math
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

# Par swap rates: tenor in years -> annualised par rate (decimal). A par swap
# rate is the fixed coupon that makes the swap fair — i.e., the present value
# of the fixed leg equals the present value of the floating leg, which under
# our simplifying assumptions equals 1 - DF(T) for a swap maturing at T.
#
# This is a textbook upward-sloping curve; in real life curves can be
# inverted, humped, or kinked, and the bootstrap must cope with whatever the
# market produces.
PAR_SWAP_RATES: dict[float, float] = {
    1.0:  0.0200,   # 1Y  par = 2.00%
    2.0:  0.0220,   # 2Y  par = 2.20%
    3.0:  0.0240,   # 3Y  par = 2.40%
    5.0:  0.0260,   # 5Y  par = 2.60%
    10.0: 0.0280,   # 10Y par = 2.80%
}


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CurvePoint:
    """A single (tenor, zero_rate, discount_factor) triple."""

    tenor_years: float
    zero_rate: float
    discount_factor: float


def bootstrap_zero_curve(par_rates: dict[float, float]) -> dict[float, float]:
    """Bootstrap zero rates from par swap rates by successive substitution.

    Simplifying assumptions (a production bootstrap relaxes all of these):

      * Annual coupons; no day-count convention.
      * Continuous compounding for the zero rate: DF(T) = exp(-z(T) * T).
      * Single curve — discount and projection share one set of zero rates,
        which only holds in pre-2008 single-curve frameworks.
      * Linear interpolation on the zero rate between knot points (only
        relevant when the par-rate tenors are not contiguous integers).

    Math sketch. A par swap with annual fixed coupon c maturing at tenor T
    has value 0 at inception, which in our simplified frame becomes:

        c * sum_{i=1..T} DF(i) + DF(T) = 1
        => DF(T) = (1 - c * sum_{i=1..T-1} DF(i)) / (1 + c)

    We solve for DF at each tenor using the previously-computed DFs at
    shorter tenors — this is the "successive substitution" core of the
    bootstrap. Once we have DF(T), the continuously-compounded zero rate is
    z(T) = -ln(DF(T)) / T.

    Returns: dict mapping tenor (years) to the zero rate (decimal).
    """
    if not par_rates:
        raise ValueError("par_rates must not be empty")
    if any(t <= 0 for t in par_rates):
        raise ValueError("tenors must be strictly positive")

    tenors = sorted(par_rates.keys())

    # Discount factors keyed by integer-year tenor along the bootstrapping
    # path. We need DFs at every coupon date, not just at the par-rate
    # tenors, so we interpolate the par rate linearly when a par-rate tenor
    # is not an integer year — fine for this educational example.
    discount_factors: dict[int, float] = {}

    max_tenor = int(tenors[-1])
    for year in range(1, max_tenor + 1):
        c = _interpolate_par_rate(year, par_rates)
        sum_prev_df = sum(discount_factors[i] for i in range(1, year))
        df_year = (1.0 - c * sum_prev_df) / (1.0 + c)
        if df_year <= 0:
            raise ValueError(
                f"Bootstrap produced non-positive DF at year {year}; "
                "input par rates are likely inconsistent."
            )
        discount_factors[year] = df_year

    # Convert to continuously-compounded zero rates at each *par-rate* tenor
    # (we only report rates at the input grid; the bootstrap consumed every
    # coupon date in between).
    zero_rates: dict[float, float] = {}
    for tenor in tenors:
        df = discount_factors[int(tenor)]
        zero_rates[tenor] = -math.log(df) / tenor
    return zero_rates


def _interpolate_par_rate(year: int, par_rates: dict[float, float]) -> float:
    """Linearly interpolate the par rate at integer-year `year`.

    Where `year` matches an input tenor, return that rate. Otherwise find
    the bracketing input tenors and linearly interpolate. Extrapolation
    beyond the input grid is forbidden — production engines support flat
    extrapolation, but flagging the missing data is safer here.
    """
    if year in par_rates:
        return par_rates[year]

    tenors = sorted(par_rates.keys())
    if year < tenors[0] or year > tenors[-1]:
        raise ValueError(
            f"year {year} is outside par-rate grid [{tenors[0]}, {tenors[-1]}]"
        )

    for lo, hi in zip(tenors, tenors[1:]):
        if lo <= year <= hi:
            w = (year - lo) / (hi - lo)
            return (1 - w) * par_rates[lo] + w * par_rates[hi]
    # Unreachable given the bracket check above.
    raise RuntimeError(f"interpolation failed at year {year}")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_curve(par_rates: dict[float, float], zero_rates: dict[float, float]) -> None:
    """Pretty-print the par vs zero comparison."""
    print(f"{'Tenor':>8s}  {'Par rate':>10s}  {'Zero rate':>10s}  {'Spread (bp)':>12s}")
    print("-" * 48)
    for tenor in sorted(par_rates.keys()):
        par = par_rates[tenor]
        zero = zero_rates[tenor]
        spread_bp = (zero - par) * 10_000
        print(
            f"  {tenor:>4.1f}Y    "
            f"{par * 100:>7.4f}%   "
            f"{zero * 100:>7.4f}%   "
            f"{spread_bp:>+8.2f}"
        )


def main() -> None:
    print("Module 11 — Bootstrap zero curve from par swap rates")
    print("=" * 56)
    print()
    zero_rates = bootstrap_zero_curve(PAR_SWAP_RATES)
    print_curve(PAR_SWAP_RATES, zero_rates)
    print()
    print("Notes:")
    print("  * Zero rates here are continuously compounded, par rates are")
    print("    annually compounded. The small negative spread is the")
    print("    compounding-convention difference, not an economic signal.")
    print("    Re-quote the zero in annual compounding (e^z - 1) and the")
    print("    relationship reverses on this upward-sloping curve.")
    print("  * On a flat curve, all par rates equal all zero rates (under a")
    print("    consistent compounding convention). Slope is what creates the")
    print("    par/zero gap; this curve is mildly upward-sloping.")
    print("  * Production: replace this with QuantLib or rateslib. Real curves")
    print("    require day-count conventions (ACT/360, 30/360), holiday")
    print("    calendars, multi-curve discount/projection split, and a chosen")
    print("    interpolation rule between knots. Persist the method on the")
    print("    market-data fact alongside the rate.")


if __name__ == "__main__":
    main()
