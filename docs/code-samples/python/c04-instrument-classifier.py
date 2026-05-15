# Module: Credit M04 — Credit Instruments
# Purpose:  Classify a credit instrument by (family, sub_type, secured, funded)
#           and return the dominant credit-risk drivers a credit warehouse
#           should expect to compute and store for that instrument. Used to
#           validate the instrument master against the PD / LGD / EAD feeds.
# Depends:  Python 3.11+, stdlib only.
# Run:      python docs/code-samples/python/c04-instrument-classifier.py

from __future__ import annotations

from typing import TypedDict


class CreditInstrumentProfile(TypedDict):
    """Risk-driver profile attached to a credit instrument."""

    family: str
    sub_type: str
    PD_drivers: list[str]
    LGD_drivers: list[str]
    EAD_treatment: str
    funded: bool
    secured: bool
    notes: str


# Dispatch keyed by (family, sub_type). Values describe the canonical risk-
# driver shape; the secured / funded flags refine LGD and EAD downstream.
# Keep keys narrow; extend by adding rows, not by special-casing in the
# function body.
_PROFILE_TABLE: dict[tuple[str, str], dict[str, list[str] | str]] = {
    ("LOAN", "TERM"): {
        "PD_drivers": ["obligor rating", "sector", "macro overlay"],
        "LGD_drivers": ["seniority", "collateral coverage", "workout cost"],
        "EAD_treatment": "outstanding principal at default",
    },
    ("LOAN", "REVOLVER"): {
        "PD_drivers": ["obligor rating", "sector", "utilisation trend"],
        "LGD_drivers": ["seniority", "collateral coverage", "workout cost"],
        "EAD_treatment": "drawn balance + CCF * undrawn commitment",
    },
    ("LOAN", "SYNDICATED"): {
        "PD_drivers": ["obligor rating", "sector", "agent-bank signals"],
        "LGD_drivers": ["seniority", "collateral coverage",
                        "syndicate workout dynamics"],
        "EAD_treatment": "participant share of (drawn + CCF * undrawn)",
    },
    ("LOAN", "LETTER_OF_CREDIT"): {
        "PD_drivers": ["obligor rating", "underlying transaction risk"],
        "LGD_drivers": ["seniority of reimbursement claim",
                        "collateral / cash margin"],
        "EAD_treatment": "commitment * CCF (typically high CCF when irrevocable)",
    },
    ("BOND", "CORPORATE_SENIOR_UNSECURED"): {
        "PD_drivers": ["issuer rating", "sector", "macro overlay"],
        "LGD_drivers": ["seniority (senior unsecured)", "industry recovery rates"],
        "EAD_treatment": "face value * (1 + accrued)",
    },
    ("BOND", "SOVEREIGN"): {
        "PD_drivers": ["sovereign rating", "country risk", "FX regime"],
        "LGD_drivers": ["restructuring history",
                        "selective-default mechanics"],
        "EAD_treatment": "face value * (1 + accrued); restructure-driven",
    },
    ("BOND", "SUBORDINATED"): {
        "PD_drivers": ["issuer rating", "trigger / write-down terms (if AT1/T2)"],
        "LGD_drivers": ["deep subordination",
                        "contractual write-down or conversion"],
        "EAD_treatment": "face value; write-down can pre-empt default",
    },
    ("CDS", "SINGLE_NAME"): {
        "PD_drivers": ["reference-entity rating",
                       "credit-spread implied PD"],
        "LGD_drivers": ["ISDA auction recovery", "deliverable obligation pool"],
        "EAD_treatment": ("notional (protection sold); for protection bought, "
                          "EAD against CDS counterparty via SA-CCR / IMM"),
    },
    ("CDS", "INDEX"): {
        "PD_drivers": ["constituent ratings", "index-level spread"],
        "LGD_drivers": ["per-constituent ISDA auction recovery"],
        "EAD_treatment": ("notional * (active constituent fraction); "
                          "counterparty EAD via SA-CCR / IMM"),
    },
    ("SECURITISATION", "RMBS_SENIOR"): {
        "PD_drivers": ["pool collateral PD", "prepayment behaviour",
                       "house-price index"],
        "LGD_drivers": ["tranche subordination",
                        "waterfall position", "servicer recovery"],
        "EAD_treatment": "outstanding tranche balance after waterfall",
    },
    ("SECURITISATION", "CLO_MEZZANINE"): {
        "PD_drivers": ["leveraged-loan pool PD", "OC / IC test breaches"],
        "LGD_drivers": ["tranche subordination",
                        "waterfall position when senior absorbs first"],
        "EAD_treatment": "outstanding tranche balance after waterfall",
    },
    ("SECURITISATION", "ABS_AUTO_SENIOR"): {
        "PD_drivers": ["pool collateral PD", "unemployment overlay",
                       "vehicle-value index"],
        "LGD_drivers": ["tranche subordination",
                        "vehicle recovery values"],
        "EAD_treatment": "outstanding tranche balance after waterfall",
    },
}


def classify_credit_instrument(
    family: str,
    sub_type: str,
    secured: bool,
    funded: bool,
) -> CreditInstrumentProfile:
    """Return the canonical risk-driver profile for a credit instrument.

    Parameters
    ----------
    family   : LOAN, BOND, CDS, SECURITISATION.
    sub_type : The specific instrument sub-type (TERM, REVOLVER, SOVEREIGN,
               SINGLE_NAME, RMBS_SENIOR, etc.). Must match a key in the
               dispatch table for the family.
    secured  : True if the instrument has a perfected security interest in
               identified collateral. Refines LGD downward.
    funded   : True for loans, drawn revolvers, bonds, and similar where
               principal is at risk on the books today. False for undrawn
               commitments, letters of credit, and CDS protection sold.

    Returns
    -------
    A CreditInstrumentProfile capturing the PD drivers, LGD drivers, and EAD
    treatment to expect in the warehouse. An unknown (family, sub_type) pair
    returns an empty driver list — the caller should treat that as a data-
    quality alert, not a default to "no risk".
    """
    key = (family.upper(), sub_type.upper())
    base = _PROFILE_TABLE.get(key)
    if base is None:
        return CreditInstrumentProfile(
            family=family.upper(),
            sub_type=sub_type.upper(),
            PD_drivers=[],
            LGD_drivers=[],
            EAD_treatment="UNKNOWN — verify against instrument master",
            funded=funded,
            secured=secured,
            notes="Unknown (family, sub_type); flagged for review",
        )

    lgd_drivers = list(base["LGD_drivers"])
    if secured:
        lgd_drivers.insert(0, "collateral haircut and realisation")
    notes = []
    if not funded and family.upper() in {"LOAN"}:
        notes.append("Undrawn commitment; EAD via CCF.")
    if family.upper() == "CDS":
        notes.append("Generates counterparty credit risk on the protection seller.")
    if family.upper() == "SECURITISATION":
        notes.append("Tranche-level grain; do not model as a single bond.")

    return CreditInstrumentProfile(
        family=family.upper(),
        sub_type=sub_type.upper(),
        PD_drivers=list(base["PD_drivers"]),
        LGD_drivers=lgd_drivers,
        EAD_treatment=str(base["EAD_treatment"]),
        funded=funded,
        secured=secured,
        notes=" ".join(notes) if notes else "",
    )


if __name__ == "__main__":
    samples = [
        # (label,                          family,           sub_type,                 secured, funded)
        ("Vanilla 5y term loan",           "LOAN",           "TERM",                   False,   True),
        ("$50M revolver, drawn $20M",      "LOAN",           "REVOLVER",               False,   True),
        ("Syndicated TLB participation",   "LOAN",           "SYNDICATED",             True,    True),
        ("Senior unsecured corp bond",     "BOND",           "CORPORATE_SENIOR_UNSECURED", False, True),
        ("EM sovereign bond",              "BOND",           "SOVEREIGN",              False,   True),
        ("CDS protection sold (5y)",       "CDS",            "SINGLE_NAME",            False,   False),
        ("RMBS AAA senior tranche",        "SECURITISATION", "RMBS_SENIOR",            True,    True),
        ("CLO BBB mezzanine tranche",      "SECURITISATION", "CLO_MEZZANINE",          True,    True),
    ]

    label_w = max(len(label) for label, *_ in samples)
    print(f"{'Instrument'.ljust(label_w)}  EAD treatment")
    print(f"{'-' * label_w}  {'-' * 60}")
    for label, family, sub_type, secured, funded in samples:
        prof = classify_credit_instrument(family, sub_type, secured, funded)
        print(f"{label.ljust(label_w)}  {prof['EAD_treatment']}")

    print()
    print("Detail for the revolver:")
    detail = classify_credit_instrument("LOAN", "REVOLVER", False, True)
    for k, v in detail.items():
        print(f"  {k}: {v}")
