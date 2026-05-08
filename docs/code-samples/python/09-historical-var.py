# Module: 09 — Value at Risk
# Purpose:  Compute one-day historical VaR and Expected Shortfall (ES) at the
#           99% confidence level over a synthetic 250-day P&L series, using
#           the empirical-quantile method that underlies historical-simulation
#           VaR in production risk warehouses. Also illustrates the effect of
#           window length (250 vs 1000 days) on the tail estimate.
# Depends:  Python 3.11+, numpy.
# Run:      python docs/code-samples/python/09-historical-var.py
#
# Reproducibility note: numpy.random.default_rng(42) seeds the synthetic P&L
# series. In production the equivalent input would be a vector of historical
# returns (or scenario P&Ls) loaded from fact_pnl or fact_scenario_pnl. The
# seed should be persisted for any computation a regulator might re-run; the
# scenario_set_id is the production analogue of the seed.

from __future__ import annotations

import numpy as np


def historical_var(pnl: np.ndarray, confidence: float = 0.99) -> float:
    """One-day historical VaR at the given confidence level.

    Sign convention: VaR is reported as a positive loss number. The input
    `pnl` is signed P&L (positive = profit, negative = loss). The lower
    (1 - confidence) quantile of the P&L distribution is the threshold P&L
    below which losses fall with probability (1 - confidence); the absolute
    value of that threshold is the VaR.
    """
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")
    if pnl.size == 0:
        raise ValueError("pnl is empty")
    threshold = np.quantile(pnl, 1.0 - confidence)
    return float(-threshold)


def expected_shortfall(pnl: np.ndarray, confidence: float = 0.99) -> float:
    """One-day historical Expected Shortfall (ES / CVaR) at confidence level.

    ES is the mean P&L conditional on the P&L being at or below the VaR
    threshold. Reported as a positive loss number, on the same sign
    convention as historical_var.
    """
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")
    threshold = np.quantile(pnl, 1.0 - confidence)
    tail = pnl[pnl <= threshold]
    if tail.size == 0:
        # Degenerate case — should not happen for reasonably sized samples.
        return float(-threshold)
    return float(-tail.mean())


def synthetic_pnl(n_days: int, vol: float, seed: int) -> np.ndarray:
    """Generate a synthetic daily P&L series.

    The series is drawn from a Student-t distribution with 5 degrees of
    freedom and rescaled to the requested daily vol. The fat tail is
    deliberate — it makes the historical-vs-parametric comparison in the
    module narrative visible at modest sample sizes.
    """
    rng = np.random.default_rng(seed)
    raw = rng.standard_t(df=5, size=n_days)
    # Rescale so that the empirical std is approximately the target vol.
    return raw * (vol / raw.std(ddof=1))


def main() -> None:
    confidence = 0.99
    daily_vol = 1_000_000.0  # USD per day, P&L scale

    # 250 days is the regulatory minimum window for many VaR systems; it
    # also produces a pleasingly noisy tail estimate that motivates the
    # 1000-day comparison below.
    pnl_250 = synthetic_pnl(n_days=250, vol=daily_vol, seed=42)
    var_250 = historical_var(pnl_250, confidence)
    es_250 = expected_shortfall(pnl_250, confidence)

    # 1000 days reduces the sampling noise on the 1% tail (from ~2-3
    # observations to ~10) and typically produces a tighter VaR/ES pair.
    pnl_1000 = synthetic_pnl(n_days=1000, vol=daily_vol, seed=42)
    var_1000 = historical_var(pnl_1000, confidence)
    es_1000 = expected_shortfall(pnl_1000, confidence)

    print("Historical VaR / ES — synthetic Student-t(5) P&L, daily vol = $1M")
    print("-" * 64)
    print(f"  N = 250  days  |  99% VaR = {var_250:>14,.0f}   "
          f"99% ES = {es_250:>14,.0f}")
    print(f"  N = 1000 days  |  99% VaR = {var_1000:>14,.0f}   "
          f"99% ES = {es_1000:>14,.0f}")
    print()
    print(f"  ES / VaR ratio (N=250)  = {es_250 / var_250:.3f}")
    print(f"  ES / VaR ratio (N=1000) = {es_1000 / var_1000:.3f}")
    print()
    print("Notes:")
    print("  * Sign convention: VaR and ES are reported as positive losses.")
    print("  * ES > VaR by construction (ES is the mean of the tail beyond VaR).")
    print("  * The ES/VaR ratio reflects tail thickness; for a normal it is")
    print("    about 1.15 at 99%, for fat tails it is larger.")
    print("  * Increasing N from 250 to 1000 reduces sampling noise on the")
    print("    tail estimate; the VaR and ES numbers converge towards their")
    print("    population values rather than chasing individual observations.")


if __name__ == "__main__":
    main()
