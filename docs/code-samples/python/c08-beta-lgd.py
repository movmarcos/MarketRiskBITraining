# Module: Credit M08 — Loss Given Default
# Purpose:  Fit a beta distribution to a small synthetic dataset of realised
#           LGDs for a single seniority/collateral segment. Report the fitted
#           parameters (alpha, beta), the implied mean, median, and 95th
#           percentile, and compare to the naive sample-mean estimator. Two
#           paths are demonstrated: scipy's MLE fit (preferred when available)
#           and a numpy-only method-of-moments fallback that produces useful
#           estimates from the sample mean and variance alone.
# Depends:  Python 3.11+, numpy. scipy optional (used when present).
# Run:      python docs/code-samples/python/c08-beta-lgd.py

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    from scipy import stats  # type: ignore[import-not-found]

    _HAS_SCIPY = True
except ImportError:  # pragma: no cover - fallback path
    _HAS_SCIPY = False


@dataclass(frozen=True)
class BetaFit:
    """Container for a beta-distribution fit on a sample of realised LGDs.

    All LGD values are decimals in [0, 1]; 0% = full recovery, 100% = total
    loss. Quote in percent at the presentation layer.
    """

    method: str  # 'MLE' or 'MOM'
    alpha: float
    beta: float
    sample_size: int
    sample_mean: float
    sample_std: float
    fit_mean: float
    fit_median: float
    fit_p95: float


def _generate_realised_lgds(seed: int = 11) -> np.ndarray:
    """Build a synthetic sample of realised LGDs for a senior-unsecured corporate bucket.

    The true distribution is intentionally right-skewed with a mean around 45%,
    matching the rough empirical shape of senior-unsecured corporate workouts
    (see Moody's Annual Recovery Studies). Returns a 1-D array of LGDs in
    [0, 1] for 40 closed workout cases.
    """
    rng = np.random.default_rng(seed)
    # True parameters chosen so mean ~ 0.45, with a meaningful right tail.
    true_alpha, true_beta = 2.0, 2.4
    sample = rng.beta(a=true_alpha, b=true_beta, size=40)
    # Clip to (eps, 1-eps) so the MLE fit doesn't trip on boundary values.
    eps = 1e-4
    return np.clip(sample, eps, 1.0 - eps)


def fit_mle(sample: np.ndarray) -> BetaFit:
    """Maximum-likelihood fit using scipy.stats.beta.

    Forces the support to be [0, 1] by fixing floc=0 and fscale=1. Without
    these constraints scipy will treat the location and scale as free
    parameters and produce a distribution on a shifted/scaled support, which
    is wrong for LGD.
    """
    if not _HAS_SCIPY:
        raise RuntimeError("scipy not available; use fit_mom() instead")

    alpha, beta, _floc, _fscale = stats.beta.fit(sample, floc=0.0, fscale=1.0)
    dist = stats.beta(alpha, beta)
    return BetaFit(
        method="MLE",
        alpha=float(alpha),
        beta=float(beta),
        sample_size=int(sample.size),
        sample_mean=float(sample.mean()),
        sample_std=float(sample.std(ddof=1)),
        fit_mean=float(dist.mean()),
        fit_median=float(dist.median()),
        fit_p95=float(dist.ppf(0.95)),
    )


def fit_mom(sample: np.ndarray) -> BetaFit:
    """Method-of-moments fit using numpy only.

    For a beta distribution with mean m and variance v on [0, 1]:

        alpha = m * (m * (1 - m) / v - 1)
        beta  = (1 - m) * (m * (1 - m) / v - 1)

    The shared factor (m * (1 - m) / v - 1) must be positive for a valid
    beta; with a sample variance close to m * (1 - m) the sample is more
    uniform than any beta on [0, 1] and the method-of-moments breaks down.
    Real production code falls back to MLE or a regularised estimator in
    that case; this scaffold raises so the failure is visible.
    """
    m = float(sample.mean())
    v = float(sample.var(ddof=1))
    if not 0.0 < m < 1.0:
        raise ValueError(f"sample mean {m} outside (0, 1); cannot fit beta")
    if v <= 0.0:
        raise ValueError("sample variance is zero; no spread to fit")

    common = m * (1.0 - m) / v - 1.0
    if common <= 0.0:
        raise ValueError(
            f"sample variance {v:.4f} >= m*(1-m) = {m * (1 - m):.4f}; "
            "method-of-moments cannot produce a valid beta"
        )

    alpha = m * common
    beta = (1.0 - m) * common

    # Compute analytical fit-mean, fit-median (approx), and 95th percentile
    # via numerical inversion of the beta CDF. To stay numpy-only we use a
    # bisection on the regularised incomplete beta function, which numpy
    # does not ship, so we approximate the percentiles by sampling.
    rng = np.random.default_rng(0)
    draws = rng.beta(a=alpha, b=beta, size=200_000)
    return BetaFit(
        method="MOM",
        alpha=float(alpha),
        beta=float(beta),
        sample_size=int(sample.size),
        sample_mean=m,
        sample_std=float(sample.std(ddof=1)),
        fit_mean=alpha / (alpha + beta),
        fit_median=float(np.median(draws)),
        fit_p95=float(np.quantile(draws, 0.95)),
    )


def _format_pct(value: float) -> str:
    """Render a probability/fraction as a percent string for human reading."""
    return f"{value * 100:>6.2f}%"


def main() -> None:
    sample = _generate_realised_lgds(seed=11)

    print(f"Realised LGDs: n = {sample.size} closed workout cases (senior-unsecured corporate).")
    print(f"  sample mean = {_format_pct(float(sample.mean()))}")
    print(f"  sample std  = {_format_pct(float(sample.std(ddof=1)))}")
    print(f"  sample min  = {_format_pct(float(sample.min()))}")
    print(f"  sample max  = {_format_pct(float(sample.max()))}")
    print()

    if _HAS_SCIPY:
        mle = fit_mle(sample)
        print("Maximum-likelihood beta fit (preferred when scipy is available)")
        print("-----------------------------------------------------------")
        print(f"  alpha       = {mle.alpha:.4f}")
        print(f"  beta        = {mle.beta:.4f}")
        print(f"  fit mean    = {_format_pct(mle.fit_mean)}")
        print(f"  fit median  = {_format_pct(mle.fit_median)}")
        print(f"  fit 95th    = {_format_pct(mle.fit_p95)}")
        print()
    else:
        print("scipy not available; skipping MLE fit.\n")

    mom = fit_mom(sample)
    print("Method-of-moments beta fit (numpy-only fallback)")
    print("------------------------------------------------")
    print(f"  alpha       = {mom.alpha:.4f}")
    print(f"  beta        = {mom.beta:.4f}")
    print(f"  fit mean    = {_format_pct(mom.fit_mean)}")
    print(f"  fit median  = {_format_pct(mom.fit_median)}")
    print(f"  fit 95th    = {_format_pct(mom.fit_p95)}")
    print()

    print("Comparison to the naive sample-mean estimator")
    print("---------------------------------------------")
    print(f"  naive point LGD = {_format_pct(float(sample.mean()))}")
    print("  The naive estimator collapses the entire distribution to a single")
    print("  number. The fitted beta retains the asymmetry and the tail: the")
    print("  95th-percentile LGD is the figure the capital team needs for")
    print("  downturn scenarios, and the median is what a typical workout")
    print("  produces. Reporting only the mean discards both.")


if __name__ == "__main__":
    main()
