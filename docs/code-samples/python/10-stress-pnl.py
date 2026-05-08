# Module: 10 — Stress Testing & Scenarios
# Purpose:  Apply a shock vector to a small sensitivities table and compute
#           sensitivity-based stressed P&L per position. Demonstrates the
#           Delta-only approximation (Δ · dS), then extends to the
#           Delta-Gamma approximation (Δ · dS + ½ Γ · dS²) for an option
#           position to show why option-heavy books require the second-order
#           term.
# Depends:  Python 3.11+, pandas, numpy.
# Run:      python docs/code-samples/python/10-stress-pnl.py
#
# Reproducibility note: the sensitivities and shock vector here are static
# inputs. In production the sensitivities would come from fact_sensitivity at
# a fixed (book, business_date, as_of_timestamp) snapshot, and the shock
# vector would come from a row of fact_scenario_shock keyed by scenario_id
# and business_date. The dot product is the loader logic; everything else is
# joins.

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

# A "long-format" sensitivities table is the production warehouse shape (see
# Module 8 §3.6). Here we pivot to a wide matrix for the linear-algebra
# convenience of the dot product. The wide form is fine for a worked example;
# in production prefer the long form and aggregate via GROUP BY.
SENSITIVITIES_LONG = pd.DataFrame(
    [
        # position_id, risk_factor,    delta_value
        ("POS_001", "USD_5Y_RATE",    -250_000.0),  # short USD 5Y rate
        ("POS_001", "EUR_USD_SPOT",         0.0),
        ("POS_001", "EQUITY_SPX",           0.0),
        ("POS_002", "USD_5Y_RATE",          0.0),
        ("POS_002", "EUR_USD_SPOT", 12_000_000.0),  # long EUR notional
        ("POS_002", "EQUITY_SPX",           0.0),
        ("POS_003", "USD_5Y_RATE",          0.0),
        ("POS_003", "EUR_USD_SPOT",         0.0),
        ("POS_003", "EQUITY_SPX",     800_000.0),   # long SPX delta
        ("POS_004", "USD_5Y_RATE",   -50_000.0),
        ("POS_004", "EUR_USD_SPOT",  2_000_000.0),
        ("POS_004", "EQUITY_SPX",     150_000.0),   # mixed-factor exposure
    ],
    columns=["position_id", "risk_factor", "delta_value"],
)

# Shock vector. Units are *factor-native*: rates in absolute decimal (50bp =
# 0.0050), FX as a relative return (-10% = -0.10), equity as a relative
# return (-20% = -0.20). The factor-native convention must match the bumping
# convention used to compute the deltas (see Module 8 §3.7) — mixing absolute
# and relative shocks against deltas computed under different conventions is
# the silent-bug machine of stress testing.
SHOCK_VECTOR: dict[str, float] = {
    "USD_5Y_RATE":  +0.0050,   # +50 bp parallel shift, absolute
    "EUR_USD_SPOT": -0.10,     # EUR weakens 10%, relative
    "EQUITY_SPX":   -0.20,     # SPX falls 20%, relative
}


@dataclass(frozen=True)
class OptionPosition:
    """A single option position carrying both delta and gamma against one factor.

    Used to extend the linear stress to a delta-gamma stress for the option
    half of the worked example. Real engines carry the full Hessian — see
    Module 8 §3.3.
    """

    position_id: str
    risk_factor: str
    delta: float   # currency per unit factor move
    gamma: float   # currency per (unit factor move)^2


OPTION_POSITION = OptionPosition(
    position_id="POS_OPT_001",
    risk_factor="EQUITY_SPX",
    delta=2_000_000.0,  # long 2M SPX delta
    gamma=5_000_000.0,  # long gamma — convexity softens the loss
)


# ---------------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------------

def stressed_pnl_linear(
    sensitivities_long: pd.DataFrame,
    shock_vector: dict[str, float],
) -> pd.DataFrame:
    """Compute per-position stressed P&L under the Delta-only approximation.

    For each position, stressed_pnl = Σ_factor (delta_factor × shock_factor).
    The implementation pivots the long-format input to a wide matrix, builds
    the shock as an aligned vector, and takes the row-wise dot product.

    Returns a DataFrame with one row per position and columns
    (position_id, stressed_pnl_linear).
    """
    if sensitivities_long.empty:
        raise ValueError("sensitivities_long is empty")

    wide = sensitivities_long.pivot(
        index="position_id",
        columns="risk_factor",
        values="delta_value",
    ).fillna(0.0)

    # Align the shock vector to the wide-frame columns. Any factor present in
    # the sensitivities but missing from the shock vector is implicitly
    # shocked by zero. In production this should be a hard error rather than
    # a silent zero — see pitfalls in the module narrative.
    shock_series = pd.Series(shock_vector).reindex(wide.columns).fillna(0.0)

    pnl = wide.values @ shock_series.values
    return pd.DataFrame(
        {"position_id": wide.index, "stressed_pnl_linear": pnl}
    )


def stressed_pnl_delta_gamma(
    position: OptionPosition,
    shock_vector: dict[str, float],
) -> tuple[float, float, float]:
    """Compute stressed P&L for one option under Delta-only and Delta-Gamma.

    Returns (linear_pnl, gamma_term, delta_gamma_pnl).

    The Delta-Gamma approximation is the second-order Taylor expansion:

        ΔPV ≈ Δ · dS + ½ Γ · dS²

    For long-gamma positions (long options), the gamma term is *positive*
    against any non-zero shock — the convexity of the option payoff means
    the linear term over-states the loss (or under-states the gain). For
    short-gamma positions, the gamma term is negative and amplifies the loss.
    """
    dS = shock_vector.get(position.risk_factor, 0.0)
    linear = position.delta * dS
    gamma_term = 0.5 * position.gamma * (dS ** 2)
    return linear, gamma_term, linear + gamma_term


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_book_summary(stress_df: pd.DataFrame) -> None:
    """Pretty-print the per-position and total stressed P&L."""
    print("Per-position stressed P&L (Delta-only, linear approximation)")
    print("-" * 64)
    for _, row in stress_df.iterrows():
        print(
            f"  {row['position_id']:>10s}  "
            f"stressed P&L = {row['stressed_pnl_linear']:>+16,.0f} USD"
        )
    total = stress_df["stressed_pnl_linear"].sum()
    print("-" * 64)
    print(f"  {'TOTAL':>10s}  stressed P&L = {total:>+16,.0f} USD")
    print()


def print_option_extension(
    linear: float, gamma_term: float, total: float, shock: float
) -> None:
    """Print the Delta-only vs Delta-Gamma comparison for the option."""
    print("Delta-Gamma extension — single option position")
    print("-" * 64)
    print(f"  Shock applied (EQUITY_SPX, relative): {shock:+.1%}")
    print(f"  Linear (Δ·dS) term:        {linear:>+16,.0f} USD")
    print(f"  Gamma  (½·Γ·dS²) term:     {gamma_term:>+16,.0f} USD")
    print(f"  Delta-Gamma stressed P&L:  {total:>+16,.0f} USD")
    print()
    delta_pct = abs(gamma_term / linear) * 100 if linear != 0 else float("nan")
    print(f"  Gamma term as % of linear: {delta_pct:.1f}%")
    print(
        "  Long-gamma positions show a positive gamma term, partially "
        "offsetting losses from the linear term — this is exactly the "
        "convexity benefit a Delta-only stress misses."
    )


def main() -> None:
    print("Module 10 — Stressed P&L from sensitivities × shock vector")
    print("=" * 64)
    print("Shock vector:")
    for factor, value in SHOCK_VECTOR.items():
        print(f"  {factor:>15s} = {value:+.4f}")
    print()

    stress_df = stressed_pnl_linear(SENSITIVITIES_LONG, SHOCK_VECTOR)
    print_book_summary(stress_df)

    linear, gamma_term, total = stressed_pnl_delta_gamma(
        OPTION_POSITION, SHOCK_VECTOR
    )
    print_option_extension(
        linear, gamma_term, total, SHOCK_VECTOR[OPTION_POSITION.risk_factor]
    )

    print()
    print("Notes:")
    print("  * Stressed P&L is additive across positions for a single shock.")
    print("    Sum across desks freely — unlike VaR (Module 9), stress under")
    print("    one fixed scenario does not require diversification adjustment.")
    print("  * The Delta-only approximation is exact for linear instruments")
    print("    (vanilla swaps, cash equity, FX forwards) and approximate for")
    print("    options. For option-heavy books, add the gamma term.")
    print("  * In production, write the result to fact_stress with grain")
    print("    (book_sk, scenario_id, business_date, as_of_timestamp).")


if __name__ == "__main__":
    main()
