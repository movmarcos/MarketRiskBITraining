# Module: Credit M12 — Credit Stress Testing
# Purpose:  Project portfolio Expected Loss over four quarters under a stylised
#           Severely Adverse macroeconomic scenario. Each facility carries its
#           own baseline PD, LGD, EAD; the scenario applies a per-quarter PD
#           and LGD multiplier path that captures the "shock and recovery"
#           shape typical of CCAR / DFAST nine-quarter projections, truncated
#           here to four quarters for didactic clarity. The output table shows
#           the per-quarter stressed EL per facility and the portfolio total.
# Caveat:   This is a *teaching* implementation. A production stress engine
#           routes macroeconomic variables (GDP, unemployment, HPI, equity
#           index, credit spreads) through fitted sensitivity coefficients per
#           segment, runs a nine-quarter balance-sheet projection that includes
#           originations, payoffs, charge-offs, and provisioning, and produces
#           tens of millions of stressed-EL cells. The flat PD/LGD multipliers
#           here stand in for the segment-and-time-varying conditional PD/LGD
#           shifts a real model produces; the goal is to make the per-quarter
#           shock-and-recovery shape visible, not to defend a regulatory figure.
# Depends:  Python 3.11+, numpy, pandas.
# Run:      python docs/code-samples/python/c12-stressed-el-projection.py

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MacroScenario:
    """A stylised four-quarter macroeconomic scenario.

    The scenario is summarised by its per-quarter multiplier vectors on PD and
    LGD. A production scenario would carry the underlying macro path (GDP,
    unemployment, HPI, etc.) and derive the multipliers via fitted sensitivity
    coefficients per facility segment; here we shortcut directly to the
    multipliers to keep the arithmetic visible.
    """

    name: str
    severity: str
    pd_multiplier_path: np.ndarray
    lgd_multiplier_path: np.ndarray
    gdp_yoy_path_pct: np.ndarray  # Documentation only; not used in arithmetic.

    def horizon_quarters(self) -> int:
        return int(self.pd_multiplier_path.shape[0])


def build_portfolio(seed: int = 42) -> pd.DataFrame:
    """Construct a 10-facility synthetic portfolio.

    Each row is a facility with a baseline PD, LGD, EAD, and a segment label.
    The segment label is informational only in this stylised model (a real
    model would key the macro sensitivity to the segment); we keep it for
    realism so the printout reads like a credit-portfolio extract.
    """
    rng = np.random.default_rng(seed)
    segments = [
        "Large Corporate", "Large Corporate", "Mid Corporate", "Mid Corporate",
        "CRE Office", "CRE Office", "CRE Industrial", "Retail Mortgage",
        "Retail Mortgage", "QRRE Credit Card",
    ]
    # Baseline PDs span 25bps (investment-grade) to 4% (sub-investment-grade).
    baseline_pd = np.array([
        0.0025, 0.0040, 0.0080, 0.0120, 0.0250, 0.0300, 0.0150, 0.0090,
        0.0060, 0.0400,
    ])
    # LGDs by collateral / seniority.
    baseline_lgd = np.array([
        0.45, 0.45, 0.50, 0.50, 0.35, 0.40, 0.30, 0.20, 0.20, 0.75,
    ])
    # EADs in dollars; broad spread to mimic a realistic concentration profile.
    baseline_ead = np.array([
        50_000_000, 25_000_000, 12_000_000, 8_000_000, 30_000_000, 20_000_000,
        15_000_000, 5_000_000, 4_000_000, 2_000_000,
    ], dtype=float)

    return pd.DataFrame({
        "facility_id": [f"FAC{idx:03d}" for idx in range(1, 11)],
        "segment": segments,
        "baseline_pd": baseline_pd,
        "baseline_lgd": baseline_lgd,
        "baseline_ead": baseline_ead,
    })


def severely_adverse_scenario() -> MacroScenario:
    """Stylised CCAR-style Severely Adverse path over four quarters.

    The PD path follows a shock-and-recovery shape: baseline in Q1 (the
    scenario begins to bite mid-Q1), peak stress at Q2-Q3, partial recovery
    by Q4. The LGD path lags PD slightly because collateral revaluations
    take time to feed into recovery assumptions. The GDP path is kept for
    documentation only — a real model would derive the multipliers from it.
    """
    return MacroScenario(
        name="Severely Adverse 2026Q2",
        severity="SEVERELY_ADVERSE",
        pd_multiplier_path=np.array([1.0, 2.5, 3.0, 2.0, 1.3]),
        lgd_multiplier_path=np.array([1.0, 1.4, 1.5, 1.3, 1.1]),
        gdp_yoy_path_pct=np.array([0.0, -2.0, -2.5, -1.0, 0.0]),
    )


def project_stressed_el(
    portfolio: pd.DataFrame,
    scenario: MacroScenario,
) -> pd.DataFrame:
    """Compute stressed EL per facility per projection quarter.

    Returns a long-format dataframe with one row per (facility, quarter) and
    the columns stressed_pd, stressed_lgd, stressed_ead, stressed_el,
    bau_el, and stress_minus_bau. The Q0 row carries the baseline
    figures (multiplier = 1.0) for comparison.

    Arithmetic per facility f and quarter q:
        stressed_pd_fq  = baseline_pd_f  * pd_multiplier[q]
        stressed_lgd_fq = baseline_lgd_f * lgd_multiplier[q] (capped at 1.0)
        stressed_ead_fq = baseline_ead_f (unchanged in this stylised model)
        stressed_el_fq  = stressed_pd_fq * stressed_lgd_fq * stressed_ead_fq
        bau_el_fq       = baseline_pd_f  * baseline_lgd_f  * baseline_ead_f
    """
    if scenario.pd_multiplier_path.shape != scenario.lgd_multiplier_path.shape:
        raise ValueError("PD and LGD multiplier paths must align")

    rows: list[dict[str, object]] = []
    n_quarters = scenario.horizon_quarters()
    for q_idx in range(n_quarters):
        pd_mult = scenario.pd_multiplier_path[q_idx]
        lgd_mult = scenario.lgd_multiplier_path[q_idx]
        stressed_pd = (portfolio["baseline_pd"] * pd_mult).clip(upper=1.0)
        stressed_lgd = (portfolio["baseline_lgd"] * lgd_mult).clip(upper=1.0)
        stressed_ead = portfolio["baseline_ead"]
        stressed_el = stressed_pd * stressed_lgd * stressed_ead
        bau_el = (
            portfolio["baseline_pd"]
            * portfolio["baseline_lgd"]
            * portfolio["baseline_ead"]
        )
        for f_idx, row in portfolio.iterrows():
            rows.append({
                "facility_id": row["facility_id"],
                "segment": row["segment"],
                "projection_quarter": f"Q{q_idx}",
                "pd_mult": pd_mult,
                "lgd_mult": lgd_mult,
                "stressed_pd": float(stressed_pd.iloc[f_idx]),
                "stressed_lgd": float(stressed_lgd.iloc[f_idx]),
                "stressed_ead": float(stressed_ead.iloc[f_idx]),
                "stressed_el": float(stressed_el.iloc[f_idx]),
                "bau_el": float(bau_el.iloc[f_idx]),
                "stress_minus_bau": float(stressed_el.iloc[f_idx] - bau_el.iloc[f_idx]),
            })
    return pd.DataFrame(rows)


def portfolio_summary(stressed: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-quarter stressed EL to portfolio level."""
    summary = (
        stressed.groupby("projection_quarter", as_index=False)
        .agg(
            portfolio_bau_el=("bau_el", "sum"),
            portfolio_stressed_el=("stressed_el", "sum"),
            portfolio_stress_uplift=("stress_minus_bau", "sum"),
        )
    )
    summary["uplift_multiple"] = (
        summary["portfolio_stressed_el"] / summary["portfolio_bau_el"]
    )
    return summary


def format_report(
    portfolio: pd.DataFrame,
    scenario: MacroScenario,
    summary: pd.DataFrame,
) -> str:
    """Render the projection as a human-readable report."""
    lines = [
        f"Stressed EL projection — scenario: {scenario.name}",
        "=" * 70,
        f"  Severity        = {scenario.severity}",
        f"  Horizon         = {scenario.horizon_quarters()} quarters (incl. Q0 baseline)",
        f"  Portfolio size  = {len(portfolio)} facilities",
        f"  Portfolio EAD   = ${portfolio['baseline_ead'].sum():>14,.0f}",
        "",
        "  Per-quarter macro path and multipliers:",
        "    quarter | GDP YoY | PD mult | LGD mult",
        "    --------+---------+---------+---------",
    ]
    for q_idx in range(scenario.horizon_quarters()):
        lines.append(
            f"      Q{q_idx:<2}  |  {scenario.gdp_yoy_path_pct[q_idx]:>+5.1f}% |  "
            f"{scenario.pd_multiplier_path[q_idx]:>4.2f}x  |  "
            f"{scenario.lgd_multiplier_path[q_idx]:>4.2f}x"
        )
    lines.extend([
        "",
        "  Portfolio-level stressed EL path:",
        "    quarter | BAU EL          | stressed EL     | uplift           | x-multiple",
        "    --------+-----------------+-----------------+------------------+-----------",
    ])
    for _, row in summary.iterrows():
        lines.append(
            f"      {row['projection_quarter']:<3} | "
            f"${row['portfolio_bau_el']:>13,.0f} | "
            f"${row['portfolio_stressed_el']:>13,.0f} | "
            f"${row['portfolio_stress_uplift']:>14,.0f} | "
            f"{row['uplift_multiple']:>6.2f}x"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    portfolio = build_portfolio()
    scenario = severely_adverse_scenario()
    stressed = project_stressed_el(portfolio, scenario)
    summary = portfolio_summary(stressed)
    print(format_report(portfolio, scenario, summary))
