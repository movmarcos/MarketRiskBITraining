# Module: 01 — Market Risk Foundations
# Purpose:  Compute DV01 (dollar value of one basis point) for a zero-coupon
#           bond by repricing under a +1bp parallel shift of the yield curve.
# Depends:  Python standard library only.

from __future__ import annotations


def zero_coupon_price(face: float, yield_rate: float, years: float) -> float:
    """Continuously-compounded price of a zero-coupon bond.

    P = F * exp(-y * T). For pedagogical clarity we use continuous
    compounding; an annual-compounding variant would use F / (1 + y) ** T.
    """
    if face <= 0:
        raise ValueError("face must be positive")
    if years < 0:
        raise ValueError("years must be non-negative")
    return face * pow(2.718281828459045, -yield_rate * years)


def dv01(face: float, yield_rate: float, years: float) -> float:
    """DV01 = price change for a -1bp parallel shift in yield.

    Convention: DV01 is reported as a positive number for a long bond
    position because a *fall* in yields *increases* price. We compute
    P(y - 1bp) - P(y).
    """
    one_bp = 0.0001
    p_base = zero_coupon_price(face, yield_rate, years)
    p_down = zero_coupon_price(face, yield_rate - one_bp, years)
    return p_down - p_base


if __name__ == "__main__":
    face = 1_000_000.0     # $1m face
    y = 0.03               # 3% continuously-compounded yield
    t = 5.0                # 5 years to maturity

    price = zero_coupon_price(face, y, t)
    sensitivity = dv01(face, y, t)

    print(f"Price at y={y:.2%}, T={t:g}y: ${price:,.2f}")
    print(f"DV01 (per -1bp parallel shift): ${sensitivity:,.2f}")
    # Sanity: closed-form DV01 ~= P * T * 1bp = price * 5 * 0.0001
    print(f"Closed-form approximation P*T*1bp: ${price * t * 0.0001:,.2f}")
