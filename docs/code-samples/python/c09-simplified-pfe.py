# Module: Credit M09 — Exposure at Default
# Purpose:  Simulate the Potential Future Exposure (PFE) profile of a single
#           stylised interest-rate swap (10y, $10M notional, fixed-receive 3%,
#           floating-pay short rate). Use a one-factor Vasicek-style mean-
#           reverting short-rate process, simulate N paths, mark the swap to
#           market on a monthly grid, and report the time profile of the 95th
#           percentile of positive MTM — the canonical PFE definition.
# Caveat:   This is a *teaching* implementation. Production SA-CCR uses a
#           prescribed regulatory formula with asset-class add-ons; production
#           IMM uses a calibrated multi-factor model with collateral, netting,
#           and margin-period-of-risk modelling. The shape of the PFE profile
#           here is qualitatively right (rises with diffusion, falls toward
#           zero as the swap amortises in time); the levels are not.
# Depends:  Python 3.11+, numpy only.
# Run:      python docs/code-samples/python/c09-simplified-pfe.py

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SwapSpec:
    """A stylised vanilla interest-rate swap on a single curve.

    Conventions:
      - The bank is the *fixed receiver* / *floating payer*.
      - Positive MTM means the swap is in the bank's favour (the counterparty
        owes the bank). Only positive MTM contributes to credit exposure;
        negative MTM is the bank's own liability and is not at risk.
      - Notional and rates are in decimals; tenors in years.
    """

    notional_usd: float
    fixed_rate: float
    tenor_years: float
    payment_frequency_per_year: int = 4  # quarterly fixed leg


@dataclass(frozen=True)
class VasicekParams:
    """Parameters for a one-factor Vasicek short-rate model.

        dr_t = kappa * (theta - r_t) * dt + sigma * dW_t

    kappa: mean-reversion speed (1/years)
    theta: long-run mean short rate (decimal)
    sigma: instantaneous volatility (decimal per sqrt-year)
    r0:    initial short rate (decimal)
    """

    kappa: float
    theta: float
    sigma: float
    r0: float


def simulate_short_rate_paths(
    params: VasicekParams,
    horizon_years: float,
    steps_per_year: int,
    n_paths: int,
    seed: int = 17,
) -> tuple[np.ndarray, np.ndarray]:
    """Simulate Vasicek short-rate paths on a uniform monthly grid.

    Returns:
      times: 1-D array of length (n_steps + 1), in years from today.
      rates: 2-D array of shape (n_paths, n_steps + 1) with simulated short rates.

    The Euler-Maruyama scheme is adequate for the teaching purpose; production
    code uses the exact-discretisation of the Vasicek SDE (which is Gaussian
    in closed form) to avoid time-step bias.
    """
    rng = np.random.default_rng(seed)
    n_steps = int(round(horizon_years * steps_per_year))
    dt = 1.0 / steps_per_year
    sqrt_dt = np.sqrt(dt)

    times = np.linspace(0.0, horizon_years, n_steps + 1)
    rates = np.empty((n_paths, n_steps + 1), dtype=float)
    rates[:, 0] = params.r0

    for t in range(n_steps):
        z = rng.standard_normal(size=n_paths)
        drift = params.kappa * (params.theta - rates[:, t]) * dt
        diffusion = params.sigma * sqrt_dt * z
        rates[:, t + 1] = rates[:, t] + drift + diffusion

    return times, rates


def swap_mtm_under_simple_pricing(
    swap: SwapSpec,
    times: np.ndarray,
    rates: np.ndarray,
) -> np.ndarray:
    """Mark the swap to market at each (path, time) under a simple pricing model.

    The simplification: at each future time t, value the remaining fixed leg
    at the prevailing short rate r_t as a flat discount rate (no curve
    construction). This is wrong by construction — a real swap valuation
    builds a full discount curve from the simulated state — but it preserves
    the qualitative shape of the exposure profile (MTM diffuses with time,
    then collapses to zero as the remaining tenor shrinks).

    Returns an array of shape (n_paths, n_times) with the swap MTM in USD
    from the bank's perspective (positive = bank receives net).
    """
    remaining_years = np.clip(swap.tenor_years - times, 0.0, None)
    # Approximate annuity factor for the remaining tenor at flat rate r:
    #   A(r, T) = (1 - exp(-r * T)) / r, with the r -> 0 limit handled.
    # The swap fixed-rate value is (fixed_rate - r) * notional * A(r, T).
    mtm = np.empty_like(rates)
    for j, T in enumerate(remaining_years):
        if T <= 0.0:
            mtm[:, j] = 0.0
            continue
        r = rates[:, j]
        # Numerically stable annuity for small r:
        safe_r = np.where(np.abs(r) < 1e-8, 1e-8, r)
        annuity = (1.0 - np.exp(-safe_r * T)) / safe_r
        mtm[:, j] = (swap.fixed_rate - r) * swap.notional_usd * annuity

    return mtm


def pfe_profile(
    mtm: np.ndarray,
    confidence: float = 0.95,
) -> np.ndarray:
    """Compute the PFE profile at the given confidence level.

    PFE_t = quantile_{confidence}(max(MTM_t, 0))

    Only the positive part of the MTM contributes to credit exposure (a
    negative MTM is the bank's liability, not its asset). The 95th percentile
    is the standard regulatory PFE quantile; some firms use the 97.5th or
    the expected positive exposure (EPE = mean of max(MTM, 0)) alongside.
    """
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie in (0, 1)")
    positive = np.maximum(mtm, 0.0)
    return np.quantile(positive, confidence, axis=0)


def expected_positive_exposure(mtm: np.ndarray) -> np.ndarray:
    """Compute the Expected Positive Exposure profile: mean of max(MTM, 0)."""
    return np.maximum(mtm, 0.0).mean(axis=0)


def _format_usd(value: float) -> str:
    return f"${value:>14,.0f}"


def main() -> None:
    swap = SwapSpec(
        notional_usd=10_000_000.0,
        fixed_rate=0.03,
        tenor_years=10.0,
        payment_frequency_per_year=4,
    )
    params = VasicekParams(
        kappa=0.15,
        theta=0.03,
        sigma=0.012,
        r0=0.03,
    )

    times, rates = simulate_short_rate_paths(
        params=params,
        horizon_years=swap.tenor_years,
        steps_per_year=12,
        n_paths=1_000,
        seed=17,
    )
    mtm = swap_mtm_under_simple_pricing(swap=swap, times=times, rates=rates)
    pfe = pfe_profile(mtm, confidence=0.95)
    epe = expected_positive_exposure(mtm)

    current_exposure = float(max(mtm[:, 0].mean(), 0.0))

    print("Simplified PFE profile — 10y vanilla IRS, $10M notional")
    print("=======================================================")
    print(f"  Fixed rate (bank receives) = {swap.fixed_rate:.2%}")
    print(f"  Vasicek params: kappa={params.kappa}, theta={params.theta}, "
          f"sigma={params.sigma}, r0={params.r0}")
    print(f"  Paths simulated           = {rates.shape[0]:,}")
    print(f"  Grid                      = monthly over 10 years "
          f"({rates.shape[1] - 1} steps)")
    print()
    print(f"  Current exposure (t=0)    = {_format_usd(current_exposure)}")
    print(f"  Peak PFE (95%)            = {_format_usd(float(pfe.max()))} "
          f"at t = {times[int(pfe.argmax())]:.2f} years")
    print(f"  Peak EPE                  = {_format_usd(float(epe.max()))} "
          f"at t = {times[int(epe.argmax())]:.2f} years")
    print()

    print("Profile snapshot (annual sampling):")
    print("  t (yrs) | PFE 95%           | EPE")
    print("  --------+-------------------+-------------------")
    for year in range(0, int(swap.tenor_years) + 1):
        idx = year * 12
        if idx >= len(times):
            idx = len(times) - 1
        print(f"  {times[idx]:>6.1f}  | {_format_usd(float(pfe[idx]))}  "
              f"| {_format_usd(float(epe[idx]))}")
    print()
    print("Notes")
    print("-----")
    print("  * Current exposure is the t=0 mark; for a freshly-traded at-par")
    print("    swap this is essentially zero. EAD under SA-CCR or IMM combines")
    print("    the current exposure with the add-on / PFE component.")
    print("  * The PFE profile rises with diffusion (uncertainty grows with the")
    print("    sqrt of time) and falls toward zero as the swap amortises in")
    print("    remaining tenor. The peak typically sits around 1/3 to 1/2 of")
    print("    the swap's life.")
    print("  * Production SA-CCR replaces this Monte Carlo with a prescribed")
    print("    formula keyed to supervisory asset-class add-ons. Production IMM")
    print("    extends the simulation to multi-factor curves, FX, collateral,")
    print("    netting sets, and margin-period-of-risk adjustments. This script")
    print("    is a teaching scaffold, not a calibration.")


if __name__ == "__main__":
    main()
