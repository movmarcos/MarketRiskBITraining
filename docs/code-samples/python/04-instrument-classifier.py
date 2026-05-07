# Module: 04 — Financial Instruments Primer
# Purpose:  Classify a financial instrument by (asset_class, payoff_type,
#           optionality) and return the dominant risk drivers a market-risk
#           warehouse should expect to compute and store for that instrument.
#           Used to validate the instrument master against the risk feed.
# Depends:  Python 3.11+, stdlib only.
# Run:      python docs/code-samples/python/04-instrument-classifier.py

from __future__ import annotations


# Dispatch keyed by (asset_class, payoff_type, optionality). Values are the
# dominant risk drivers a market-risk system should be sourcing for the
# instrument. Keep the keys narrow and the values ordered by economic weight.
_DRIVER_TABLE: dict[tuple[str, str, str], list[str]] = {
    # Rates
    ("RATES", "LINEAR", "NONE"):       ["IR delta", "IR curve shape", "basis"],
    ("RATES", "NONLINEAR", "VANILLA"): ["IR delta", "IR vega", "IR convexity"],
    ("RATES", "NONLINEAR", "EXOTIC"):  ["IR delta", "IR vega", "IR convexity",
                                         "smile / SABR params"],
    # FX
    ("FX",    "LINEAR", "NONE"):       ["FX spot delta", "IR delta (both legs)"],
    ("FX",    "NONLINEAR", "VANILLA"): ["FX spot delta", "FX vega",
                                         "IR delta (both legs)"],
    ("FX",    "NONLINEAR", "EXOTIC"):  ["FX spot delta", "FX vega",
                                         "FX vanna", "FX volga",
                                         "IR delta (both legs)"],
    # Credit
    ("CREDIT", "LINEAR", "NONE"):      ["IR delta", "credit spread (CS01)",
                                         "recovery"],
    ("CREDIT", "NONLINEAR", "VANILLA"): ["IR delta", "credit spread (CS01)",
                                          "jump-to-default"],
    # Equity
    ("EQUITY", "LINEAR", "NONE"):      ["equity delta", "dividend exposure"],
    ("EQUITY", "NONLINEAR", "VANILLA"): ["equity delta", "equity gamma",
                                          "equity vega", "dividend exposure",
                                          "rho"],
    ("EQUITY", "NONLINEAR", "EXOTIC"):  ["equity delta", "equity gamma",
                                          "equity vega", "skew / smile",
                                          "correlation", "barrier risk"],
    # Commodity
    ("COMMODITY", "LINEAR", "NONE"):       ["commodity delta",
                                              "term-structure (curve) risk"],
    ("COMMODITY", "NONLINEAR", "VANILLA"): ["commodity delta",
                                              "commodity vega",
                                              "term-structure (curve) risk"],
}


def classify_instrument(
    asset_class: str,
    payoff_type: str,
    optionality: str,
) -> list[str]:
    """Return the dominant risk drivers for an instrument.

    Parameters
    ----------
    asset_class : one of RATES, FX, CREDIT, EQUITY, COMMODITY.
    payoff_type : LINEAR or NONLINEAR. A vanilla swap is LINEAR; any option is
                  NONLINEAR.
    optionality : NONE, VANILLA, or EXOTIC. NONE applies to non-option products
                  (bond, swap, forward, future). VANILLA applies to plain
                  European/American puts and calls, vanilla swaptions, vanilla
                  caps/floors. EXOTIC covers barriers, autocallables, baskets,
                  path-dependent payoffs.

    Returns
    -------
    A list of risk-driver labels suitable for cross-checking against the
    sensitivities the warehouse actually stores for the instrument. The list
    is empty if the combination is unknown — the caller should treat that as
    a data-quality alert, not a default to "no risk".
    """
    key = (asset_class.upper(), payoff_type.upper(), optionality.upper())
    return list(_DRIVER_TABLE.get(key, []))


if __name__ == "__main__":
    samples = [
        # (label,                 asset_class, payoff_type, optionality)
        ("Vanilla IRS (5y)",      "RATES",     "LINEAR",    "NONE"),
        ("IR cap (3y, USD)",      "RATES",     "NONLINEAR", "VANILLA"),
        ("FX forward (EUR/USD)",  "FX",        "LINEAR",    "NONE"),
        ("FX option (EUR/USD)",   "FX",        "NONLINEAR", "VANILLA"),
        ("Equity vanilla (AAPL)", "EQUITY",    "LINEAR",    "NONE"),
        ("Equity barrier (SPX)",  "EQUITY",    "NONLINEAR", "EXOTIC"),
        ("CDS (single name)",     "CREDIT",    "LINEAR",    "NONE"),
        ("Corporate bond",        "CREDIT",    "LINEAR",    "NONE"),
    ]

    width = max(len(label) for label, *_ in samples)
    print(f"{'Instrument'.ljust(width)}  Risk drivers")
    print(f"{'-' * width}  {'-' * 60}")
    for label, ac, pt, opt in samples:
        drivers = classify_instrument(ac, pt, opt)
        print(f"{label.ljust(width)}  {', '.join(drivers)}")
