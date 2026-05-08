# Module: 08 — Sensitivities Deep Dive
# Purpose:  Compute the delta of a vanilla European call two ways — analytic
#           (closed-form Black-Scholes) and numerical (central-difference
#           bump-and-revalue) — and confirm they agree to about six decimal
#           places for a benchmark option. Demonstrates the bumping convention
#           that produces fact_sensitivity rows in a typical risk warehouse.
# Depends:  Python 3.11+, standard library only (math).
# Run:      python docs/code-samples/python/08-numerical-delta.py

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class EuropeanCall:
    """A vanilla European call option, parameterised in the Black-Scholes world."""

    spot: float       # underlying price, S
    strike: float     # strike price, K
    vol: float        # annualised volatility, sigma (e.g. 0.20 for 20%)
    rate: float       # risk-free rate, r (continuously compounded, annual)
    ttm: float        # time to maturity in years, T


def _phi(x: float) -> float:
    """Standard-normal cumulative distribution function via math.erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black_scholes_call(opt: EuropeanCall) -> float:
    """Closed-form Black-Scholes price of a European call (no dividend)."""
    if opt.ttm <= 0.0:
        # Intrinsic value at or after expiry. Avoids log(0) and division by zero.
        return max(opt.spot - opt.strike, 0.0)
    d1 = (math.log(opt.spot / opt.strike)
          + (opt.rate + 0.5 * opt.vol * opt.vol) * opt.ttm) \
         / (opt.vol * math.sqrt(opt.ttm))
    d2 = d1 - opt.vol * math.sqrt(opt.ttm)
    return opt.spot * _phi(d1) - opt.strike * math.exp(-opt.rate * opt.ttm) * _phi(d2)


def analytic_delta(opt: EuropeanCall) -> float:
    """Closed-form delta of a European call: N(d1)."""
    if opt.ttm <= 0.0:
        return 1.0 if opt.spot > opt.strike else 0.0
    d1 = (math.log(opt.spot / opt.strike)
          + (opt.rate + 0.5 * opt.vol * opt.vol) * opt.ttm) \
         / (opt.vol * math.sqrt(opt.ttm))
    return _phi(d1)


def numerical_delta(opt: EuropeanCall, h: float = 1e-4) -> float:
    """Central-difference numerical delta: (V(S+h) - V(S-h)) / (2h).

    The bump ``h`` is in absolute price units. For a $100 spot this is 0.01% —
    small enough that the truncation error of the central difference is below
    the analytic-vs-numerical agreement we expect, large enough that the
    floating-point cancellation in the numerator is not yet dominant.
    """
    if h <= 0.0:
        raise ValueError("bump size h must be strictly positive")
    up = EuropeanCall(opt.spot + h, opt.strike, opt.vol, opt.rate, opt.ttm)
    dn = EuropeanCall(opt.spot - h, opt.strike, opt.vol, opt.rate, opt.ttm)
    return (black_scholes_call(up) - black_scholes_call(dn)) / (2.0 * h)


if __name__ == "__main__":
    benchmark = EuropeanCall(spot=100.0, strike=100.0, vol=0.20, rate=0.02, ttm=1.0)

    px = black_scholes_call(benchmark)
    d_an = analytic_delta(benchmark)
    d_num = numerical_delta(benchmark, h=1e-4)

    print(f"Benchmark option: S=K=100, sigma=20%, r=2%, T=1y")
    print(f"  Price (BS)            : {px:.8f}")
    print(f"  Delta (analytic, N(d1)): {d_an:.8f}")
    print(f"  Delta (numerical, h=1e-4, central): {d_num:.8f}")
    print(f"  Absolute disagreement : {abs(d_num - d_an):.2e}")

    # Demonstrate floating-point noise as the bump shrinks. Below ~1e-6 the
    # cancellation in (V(S+h) - V(S-h)) starts dominating the truncation
    # error, and the numerical delta gets *worse* not better.
    print()
    print("Bump size h | numerical delta  | error vs analytic")
    print("-" * 56)
    for exp in range(-1, -10, -1):
        h = 10.0 ** exp
        d = numerical_delta(benchmark, h=h)
        print(f"  1e{exp:+03d}     | {d:.10f}   | {abs(d - d_an):.2e}")
