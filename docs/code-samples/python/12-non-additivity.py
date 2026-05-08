# Module: 12 — Aggregation, Hierarchies & Additivity
# Purpose:  Demonstrate empirically that VaR is NOT additive across portfolios.
#           Build two synthetic 250-day return series with controlled
#           correlation (-0.3 and +0.7), compute one-day 99% historical VaR
#           for portfolio A alone, portfolio B alone, and the combined
#           portfolio A+B. Show that VaR(A) + VaR(B) substantially exceeds
#           VaR(A+B) under negative correlation (the "diversification benefit"),
#           and approaches equality under high positive correlation.
# Depends:  Python 3.11+, numpy.
# Run:      python docs/code-samples/python/12-non-additivity.py
#
# This script underpins the Module 12 narrative on non-additivity: in a BI
# warehouse you cannot store per-portfolio VaR and SUM it to get firm-wide
# VaR; the answer would systematically over-state the firm's risk by the
# diversification benefit. The only correct path is to recompute VaR at the
# requested aggregation grain from the underlying P&L vectors.
#
# Reproducibility: numpy.random.default_rng(42) seeds the synthetic returns.

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def historical_var(pnl: np.ndarray, confidence: float = 0.99) -> float:
    """One-day historical VaR at the given confidence level.

    Sign convention: VaR is reported as a positive loss number. The input
    `pnl` is signed P&L (positive = profit, negative = loss).
    """
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")
    if pnl.size == 0:
        raise ValueError("pnl is empty")
    threshold = np.quantile(pnl, 1.0 - confidence)
    return float(-threshold)


def correlated_returns(
    n_days: int,
    correlation: float,
    vol_a: float,
    vol_b: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate two return series with the requested pairwise correlation.

    Returns are drawn from a bivariate normal with the given vols and
    correlation, then each series is independently rescaled so its empirical
    standard deviation matches the requested vol exactly. The rescale step
    is what makes the per-portfolio VaR numbers reproducible at this sample
    size; without it sampling noise on the std swamps the correlation effect.
    """
    if not -1.0 <= correlation <= 1.0:
        raise ValueError("correlation must be in [-1, 1]")
    rng = np.random.default_rng(seed)
    cov = np.array(
        [
            [vol_a ** 2, correlation * vol_a * vol_b],
            [correlation * vol_a * vol_b, vol_b ** 2],
        ]
    )
    samples = rng.multivariate_normal(mean=[0.0, 0.0], cov=cov, size=n_days)
    a, b = samples[:, 0], samples[:, 1]
    a = a * (vol_a / a.std(ddof=1))
    b = b * (vol_b / b.std(ddof=1))
    return a, b


@dataclass(frozen=True)
class VarRow:
    """A single row of the demonstration table."""

    correlation: float
    var_a: float
    var_b: float
    var_a_plus_b: float

    @property
    def sum_of_vars(self) -> float:
        return self.var_a + self.var_b

    @property
    def diversification_benefit(self) -> float:
        return self.sum_of_vars - self.var_a_plus_b

    @property
    def benefit_pct(self) -> float:
        return 100.0 * self.diversification_benefit / self.sum_of_vars


def measure(
    correlation: float,
    n_days: int = 250,
    vol_a: float = 1_000_000.0,
    vol_b: float = 800_000.0,
    confidence: float = 0.99,
    seed: int = 42,
) -> VarRow:
    """Build two correlated portfolios and measure the three VaRs."""
    a, b = correlated_returns(
        n_days=n_days,
        correlation=correlation,
        vol_a=vol_a,
        vol_b=vol_b,
        seed=seed,
    )
    combined = a + b  # equally-weighted dollar-sized portfolio
    return VarRow(
        correlation=correlation,
        var_a=historical_var(a, confidence),
        var_b=historical_var(b, confidence),
        var_a_plus_b=historical_var(combined, confidence),
    )


def print_table(rows: list[VarRow]) -> None:
    print("99% one-day historical VaR — synthetic 250-day returns")
    print("Portfolio A: vol = $1.0M / day   Portfolio B: vol = $0.8M / day")
    print("=" * 88)
    header = (
        f"{'rho':>6}  {'VaR(A)':>12}  {'VaR(B)':>12}  "
        f"{'VaR(A)+VaR(B)':>16}  {'VaR(A+B)':>12}  {'div benefit':>14}  {'pct':>6}"
    )
    print(header)
    print("-" * 88)
    for row in rows:
        print(
            f"{row.correlation:>+6.2f}  "
            f"{row.var_a:>12,.0f}  "
            f"{row.var_b:>12,.0f}  "
            f"{row.sum_of_vars:>16,.0f}  "
            f"{row.var_a_plus_b:>12,.0f}  "
            f"{row.diversification_benefit:>14,.0f}  "
            f"{row.benefit_pct:>5.1f}%"
        )
    print("=" * 88)


def main() -> None:
    correlations = [-0.30, 0.00, 0.70, 0.99]
    rows = [measure(correlation=c) for c in correlations]
    print_table(rows)
    print()
    print("Reading the table:")
    print("  * At rho = -0.30, the diversification benefit is large: gains in A")
    print("    tend to offset losses in B and vice versa, so the combined tail")
    print("    is materially smaller than the sum of the per-portfolio tails.")
    print("  * At rho = 0.00 (independent), some diversification still applies")
    print("    because losses are not perfectly synchronised on tail days.")
    print("  * At rho = 0.70 the benefit shrinks substantially; the two")
    print("    portfolios mostly move together and the tails coincide.")
    print("  * At rho ~ 1, the benefit collapses to zero: VaR is sub-linear at")
    print("    worst, and additive in the perfect-comonotonic case. This is the")
    print("    'all correlations go to 1 in a crisis' scenario regulators stress.")
    print()
    print("Implication for warehouse design:")
    print("  Storing per-book VaR and SUM-ing it gives the rho = 1 answer,")
    print("  systematically over-stating risk in normal conditions and giving")
    print("  the wrong shape of error in stress. The correct pattern is to")
    print("  store the underlying P&L vectors (fact_scenario_pnl) and recompute")
    print("  VaR at the required aggregation grain — see Module 12 §3.4.")


if __name__ == "__main__":
    main()
