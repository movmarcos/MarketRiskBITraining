# Module: 14 — P&L Attribution
# Purpose:  Demonstrate a Taylor-series P&L attribution for a single vanilla
#           call option position. Given a set of Greeks (delta, gamma, vega,
#           theta) and a set of market moves (dS, dsigma, dt), decompose the
#           predicted P&L into per-Greek contributions, sum to the predicted
#           total, and compare against a "true" full-revaluation P&L. The
#           residual is the unexplained P&L — the quantity the FRTB PLA test
#           ultimately polices.
# Depends:  Python 3.11+, dataclasses (stdlib only).
# Run:      python docs/code-samples/python/14-pnl-attribution.py
#
# This script underpins the Module 14 narrative on P&L attribution: in a
# market-risk warehouse the daily attribution is computed against the start-
# of-day Greeks and the day's observed market moves, the per-Greek
# contributions are stored as rows of fact_pnl_attribution, and the residual
# is the line item that drives the PLA conversation with risk modelling.
#
# Reproducibility: no randomness; the numbers are deterministic.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Greeks:
    """Start-of-day Greeks for a single position.

    Sign and unit conventions:
      - delta:  per 1.0 move in the underlying spot S (dimensionless).
      - gamma:  per 1.0^2 move in the underlying spot S.
      - vega:   per 1.0 vol-point (1 percentage point) move in implied vol.
      - theta:  per 1.0 calendar day (signed; typically negative for long
                vanilla options).
      - rho:    per 1.0 percentage-point move in the relevant interest rate.
    """

    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float = 0.0


@dataclass(frozen=True)
class MarketMoves:
    """Observed market moves between yesterday's close and today's close.

    Units must agree with the Greeks. dS is in spot-price units, d_sigma in
    vol-points, dt in calendar days, dr in interest-rate percentage points.
    """

    d_spot: float
    d_sigma: float
    d_t: float = 1.0
    d_rate: float = 0.0


@dataclass(frozen=True)
class Attribution:
    """Per-component contributions to predicted P&L.

    All values are in the position's reporting currency; the components sum
    (by construction) to `predicted_total`. The unexplained P&L is the
    difference between actual_total and predicted_total and is reported as
    a separate row in fact_pnl_attribution.
    """

    delta_pnl: float
    gamma_pnl: float
    vega_pnl: float
    theta_pnl: float
    rho_pnl: float
    predicted_total: float
    actual_total: float
    unexplained: float


def attribute_pnl(
    greeks: Greeks,
    moves: MarketMoves,
    actual_pnl: float,
) -> Attribution:
    """Decompose predicted P&L into per-Greek contributions and a residual.

    The decomposition is the standard second-order Taylor expansion of the
    position value around yesterday's market state:

        dP ~= delta * dS + 0.5 * gamma * dS^2
              + vega * d_sigma + theta * dt + rho * dr

    Each term is one row of fact_pnl_attribution. The residual
    actual_pnl - predicted_total is the *unexplained* P&L; if it is small
    relative to actual_pnl the model is tracking reality, and if it is
    large the diagnostic checklist from Module 14 §5 starts.
    """
    delta_pnl = greeks.delta * moves.d_spot
    gamma_pnl = 0.5 * greeks.gamma * moves.d_spot * moves.d_spot
    vega_pnl = greeks.vega * moves.d_sigma
    theta_pnl = greeks.theta * moves.d_t
    rho_pnl = greeks.rho * moves.d_rate

    predicted = delta_pnl + gamma_pnl + vega_pnl + theta_pnl + rho_pnl
    unexplained = actual_pnl - predicted

    return Attribution(
        delta_pnl=delta_pnl,
        gamma_pnl=gamma_pnl,
        vega_pnl=vega_pnl,
        theta_pnl=theta_pnl,
        rho_pnl=rho_pnl,
        predicted_total=predicted,
        actual_total=actual_pnl,
        unexplained=unexplained,
    )


def format_table(attribution: Attribution) -> str:
    """Render the attribution as a small ASCII table for stdout.

    The table layout mirrors the row structure of fact_pnl_attribution:
    one row per attribution_component, plus the predicted/actual totals
    and the unexplained residual at the bottom.
    """
    rows = [
        ("delta_pnl", attribution.delta_pnl),
        ("gamma_pnl", attribution.gamma_pnl),
        ("vega_pnl", attribution.vega_pnl),
        ("theta_pnl", attribution.theta_pnl),
        ("rho_pnl", attribution.rho_pnl),
        ("predicted_total", attribution.predicted_total),
        ("actual_total", attribution.actual_total),
        ("unexplained", attribution.unexplained),
    ]
    width = max(len(name) for name, _ in rows)
    lines = [f"{'component'.ljust(width)}  {'pnl':>10}"]
    lines.append(f"{'-' * width}  {'-' * 10}")
    for name, value in rows:
        lines.append(f"{name.ljust(width)}  {value:>10.4f}")
    return "\n".join(lines)


def unexplained_ratio(attribution: Attribution) -> float:
    """Return the unexplained-as-percent-of-actual diagnostic.

    Returns +inf when actual_total is exactly zero and unexplained is not;
    returns 0.0 when both are zero. The PLA quality flag in the warehouse
    is typically |unexplained| / max(|actual|, eps), bucketed into green /
    amber / red zones.
    """
    if attribution.actual_total == 0.0:
        return float("inf") if attribution.unexplained != 0.0 else 0.0
    return abs(attribution.unexplained) / abs(attribution.actual_total)


if __name__ == "__main__":
    # Start-of-day Greeks for a single vanilla call. The numbers are
    # representative of an at-the-money short-dated option on a $100 stock.
    greeks = Greeks(
        delta=0.5,       # 50% delta
        gamma=0.02,      # gamma in option-units per spot^2
        vega=0.15,       # P&L per 1.0 vol-point change
        theta=-0.04,     # P&L per calendar day held (decay)
        rho=0.0,
    )

    # Observed market moves: spot up by 2 points, implied vol down by 0.5
    # vol-points, one calendar day elapsed, no rate move.
    moves = MarketMoves(d_spot=2.0, d_sigma=-0.5, d_t=1.0, d_rate=0.0)

    # The "true" full-revaluation P&L from the pricing engine. This number
    # would normally come from the front-office or middle-office revaluation
    # run; here it is hard-coded to demonstrate a small unexplained residual.
    actual_pnl = 1.05

    attribution = attribute_pnl(greeks, moves, actual_pnl)
    print("P&L attribution for one vanilla call position\n")
    print(format_table(attribution))
    print()
    ratio = unexplained_ratio(attribution)
    print(f"unexplained / |actual| = {ratio:.2%}")

    # Expected output (deterministic):
    #   delta_pnl        =  1.0000  (0.5 * 2)
    #   gamma_pnl        =  0.0400  (0.5 * 0.02 * 2^2)
    #   vega_pnl         = -0.0750  (0.15 * -0.5)
    #   theta_pnl        = -0.0400  (-0.04 * 1)
    #   rho_pnl          =  0.0000
    #   predicted_total  =  0.9250
    #   actual_total     =  1.0500
    #   unexplained      =  0.1250  (~11.9% of actual)
    #
    # An ~12% residual on a single position would not be alarming on a quiet
    # day, but a desk reporting it persistently for two weeks is the trigger
    # for the diagnostic checklist in Module 14 §5: check market data first,
    # then risk-factor coverage, then higher-order Greeks, then the model.
