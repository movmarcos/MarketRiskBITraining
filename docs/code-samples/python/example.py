"""Module: _template (generic illustrative snippet).

Description: Computes a rolling mean over a small synthetic series using
    numpy. Standalone-runnable — no external data required.

Requires: Python 3.11+, numpy.
"""

from __future__ import annotations

import numpy as np


def rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    """Return the simple rolling mean of `values` over `window` observations.

    The first `window - 1` entries are NaN, matching pandas' default behaviour.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    if values.ndim != 1:
        raise ValueError("values must be one-dimensional")

    result = np.full(values.shape, np.nan, dtype=float)
    if values.size >= window:
        cumsum = np.cumsum(values, dtype=float)
        windowed = cumsum[window - 1:].copy()
        windowed[1:] -= cumsum[:-window]
        result[window - 1:] = windowed / window
    return result


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    series = rng.normal(loc=0.0, scale=1.0, size=10)
    means = rolling_mean(series, window=3)
    for i, (raw, smoothed) in enumerate(zip(series, means)):
        print(f"t={i:2d}  value={raw: .4f}  rolling3={smoothed: .4f}")
