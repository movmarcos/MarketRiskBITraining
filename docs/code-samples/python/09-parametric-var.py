# Module: 09 — Value at Risk
# Purpose:  Compute one-day 99% parametric VaR for a two-asset portfolio
#           two ways: (1) a closed-form analytic formula based on the
#           portfolio variance and the standard-normal quantile, and
#           (2) a Monte Carlo estimate using a Cholesky factorisation of
#           the asset covariance matrix to generate correlated normal
#           returns. The two numbers should agree closely for large N.
# Depends:  Python 3.11+, numpy.
# Run:      python docs/code-samples/python/09-parametric-var.py
#
# Sign convention follows 09-historical-var.py: VaR is a positive loss
# number. P&L is signed (positive = profit, negative = loss).

from __future__ import annotations

import numpy as np


# Inline standard-normal inverse CDF using only numpy + math, to avoid a
# scipy dependency. The Beasley-Springer-Moro approximation is accurate
# to ~1e-7 across the relevant tail and is the production standard for
# this kind of helper.
def _inv_norm_cdf(p: float) -> float:
    """Inverse standard-normal CDF via Beasley-Springer-Moro."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02,
         -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02,
         -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01,
         2.445134137142996e+00, 3.754408661907416e+00]

    p_low = 0.02425
    p_high = 1.0 - p_low

    if p < p_low:
        q = (-2.0 * np.log(p)) ** 0.5
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) \
               / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    if p <= p_high:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q \
               / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    q = (-2.0 * np.log(1.0 - p)) ** 0.5
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) \
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)


def covariance_matrix(vols: np.ndarray, corr: float) -> np.ndarray:
    """2x2 covariance matrix from per-asset annualised vols and a single
    pairwise correlation. Generalises trivially to NxN if needed."""
    if vols.shape != (2,):
        raise ValueError("this helper assumes exactly two assets")
    cov = np.array([
        [vols[0] ** 2,           corr * vols[0] * vols[1]],
        [corr * vols[0] * vols[1], vols[1] ** 2          ],
    ])
    return cov


def analytic_var(weights: np.ndarray,
                 cov_annual: np.ndarray,
                 portfolio_value: float,
                 confidence: float,
                 horizon_days: int = 1,
                 trading_days_per_year: int = 252) -> float:
    """Closed-form parametric VaR for a portfolio of normally distributed
    returns. VaR = z_alpha * sigma_portfolio * portfolio_value, scaled to
    the requested horizon by sqrt(horizon / trading_days_per_year)."""
    sigma_p_annual = float(np.sqrt(weights @ cov_annual @ weights))
    sigma_p_horizon = sigma_p_annual * np.sqrt(horizon_days / trading_days_per_year)
    z = _inv_norm_cdf(confidence)
    return z * sigma_p_horizon * portfolio_value


def monte_carlo_var(weights: np.ndarray,
                    cov_annual: np.ndarray,
                    portfolio_value: float,
                    confidence: float,
                    n_paths: int,
                    horizon_days: int = 1,
                    trading_days_per_year: int = 252,
                    seed: int = 42) -> float:
    """Monte Carlo VaR via Cholesky-factorised correlated normals.

    Returns are assumed jointly normal with mean zero and covariance
    `cov_annual`, scaled to the horizon by the square-root-of-time rule.
    The Cholesky factor L satisfies L L.T = cov_horizon; multiplying L
    into a matrix of i.i.d. standard normals produces correlated draws
    with the right covariance structure."""
    rng = np.random.default_rng(seed)
    cov_horizon = cov_annual * (horizon_days / trading_days_per_year)
    L = np.linalg.cholesky(cov_horizon)
    iid = rng.standard_normal(size=(2, n_paths))
    correlated = L @ iid                                  # shape (2, n_paths)
    portfolio_returns = weights @ correlated              # shape (n_paths,)
    pnl = portfolio_returns * portfolio_value             # signed P&L
    threshold = np.quantile(pnl, 1.0 - confidence)
    return float(-threshold)


def main() -> None:
    # Two-asset book: 60% asset A (15% annual vol), 40% asset B (20% annual vol),
    # correlation 0.3, portfolio mark-to-market = $10M.
    vols = np.array([0.15, 0.20])
    corr = 0.30
    weights = np.array([0.6, 0.4])
    portfolio_value = 10_000_000.0
    confidence = 0.99
    cov_annual = covariance_matrix(vols, corr)

    var_analytic = analytic_var(weights, cov_annual, portfolio_value, confidence)

    print("Parametric VaR — two-asset portfolio, 1-day 99%")
    print("-" * 64)
    print(f"  Vols (annual):        A = {vols[0]:.0%}   B = {vols[1]:.0%}")
    print(f"  Correlation:          {corr:.2f}")
    print(f"  Weights:              A = {weights[0]:.0%}   B = {weights[1]:.0%}")
    print(f"  Portfolio value:      ${portfolio_value:,.0f}")
    print()
    print(f"  Analytic 1-day 99% VaR:  ${var_analytic:,.0f}")
    print()

    for n_paths in (1_000, 10_000, 100_000, 1_000_000):
        var_mc = monte_carlo_var(weights, cov_annual, portfolio_value,
                                 confidence, n_paths=n_paths)
        rel_err = (var_mc - var_analytic) / var_analytic
        print(f"  Monte Carlo VaR  N = {n_paths:>9,}   "
              f"VaR = ${var_mc:>12,.0f}   rel. err = {rel_err:+.3%}")

    print()
    print("Notes:")
    print("  * Analytic and Monte Carlo agree because the simulation is drawn")
    print("    from the same normal distribution the analytic formula assumes.")
    print("  * Relative error shrinks as O(1/sqrt(N)); the tail quantile is")
    print("    noisier than the mean, so the convergence is slower than the")
    print("    nominal Monte Carlo rate would suggest.")
    print("  * Divergence between analytic and MC at higher confidence (99.9%,")
    print("    99.97%) reflects sample-size starvation in the deep tail and is")
    print("    a recurring reason production engines run >=1M paths for FRTB.")


if __name__ == "__main__":
    main()
