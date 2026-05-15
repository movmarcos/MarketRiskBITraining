# Module: Credit M07 — Probability of Default
# Purpose:  Compute an empirical 1-year PD per rating bucket per observation
#           year from a synthetic cohort dataset, then average across years to
#           produce a TTC-style empirical PD per bucket. Designed to make the
#           Low-Default-Portfolio (LDP) problem visible: AAA buckets produce
#           zero observed defaults across most years, which is the data shape
#           that motivates Bayesian shrinkage / pooling in production models.
# Depends:  Python 3.11+, numpy, pandas. Stdlib only otherwise.
# Run:      python docs/code-samples/python/c07-empirical-pd.py

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CalibrationResult:
    """Per-bucket empirical PD plus the supporting cohort counts.

    All probabilities are stored as decimals in [0, 1]; quote in basis
    points at the presentation layer (1 bp = 0.0001).
    """

    per_year: pd.DataFrame  # columns: rating_bucket, observation_year, n_obligors, n_defaults, pd_year
    per_bucket: pd.DataFrame  # columns: rating_bucket, n_years, total_obligors, total_defaults, pd_avg, pd_pooled


def _generate_cohort(seed: int = 42) -> pd.DataFrame:
    """Build a synthetic (obligor_id, rating_bucket, observation_year, defaulted_within_12_months) panel.

    Five rating buckets x five years x 10-20 obligors per cell. PDs are set
    so AAA is genuinely an LDP segment (true PD ~ 1 bp) and CCC has plenty
    of defaults (true PD ~ 25%). The empirical method below should recover
    something close to the true PDs for the noisier buckets and produce
    obviously unstable estimates for AAA.
    """
    rng = np.random.default_rng(seed)
    buckets: dict[str, float] = {
        "AAA": 0.0001,
        "A": 0.0030,
        "BBB": 0.0090,
        "BB": 0.0400,
        "CCC": 0.2500,
    }
    years = [2021, 2022, 2023, 2024, 2025]
    rows: list[dict[str, object]] = []
    obligor_seq = 0
    for bucket, true_pd in buckets.items():
        for year in years:
            n_in_cell = int(rng.integers(low=10, high=21))  # 10-20 obligors per cell
            defaults = rng.binomial(n=1, p=true_pd, size=n_in_cell)
            for d in defaults:
                obligor_seq += 1
                rows.append(
                    {
                        "obligor_id": f"OBL{obligor_seq:05d}",
                        "rating_bucket": bucket,
                        "observation_year": year,
                        "defaulted_within_12_months": int(d),
                    }
                )
    return pd.DataFrame(rows)


def calibrate_empirical_pd(cohort: pd.DataFrame) -> CalibrationResult:
    """Compute per-bucket per-year default rates and bucket-level averages.

    Two bucket-level statistics are produced:

    * ``pd_avg``     — simple average of yearly PDs. Equal weight per year.
                      The classical TTC estimator: each year of the cycle
                      counts equally regardless of how many obligors lived
                      through it.
    * ``pd_pooled``  — total defaults / total obligor-years across the
                      window. More efficient when cell sizes vary; biased
                      toward years with more obligors.

    Reporting both is the honest answer when the calibration team and the
    BI team need to agree on a single number — the difference between them
    is itself a diagnostic for cohort-size imbalance.
    """
    if not {"rating_bucket", "observation_year", "defaulted_within_12_months"}.issubset(cohort.columns):
        raise ValueError("cohort must have rating_bucket, observation_year, defaulted_within_12_months columns")

    per_year = (
        cohort.groupby(["rating_bucket", "observation_year"], as_index=False)
        .agg(
            n_obligors=("obligor_id", "count"),
            n_defaults=("defaulted_within_12_months", "sum"),
        )
        .assign(pd_year=lambda df: df["n_defaults"] / df["n_obligors"])
        .sort_values(["rating_bucket", "observation_year"])
        .reset_index(drop=True)
    )

    per_bucket = (
        per_year.groupby("rating_bucket", as_index=False)
        .agg(
            n_years=("observation_year", "nunique"),
            total_obligors=("n_obligors", "sum"),
            total_defaults=("n_defaults", "sum"),
            pd_avg=("pd_year", "mean"),
        )
        .assign(pd_pooled=lambda df: df["total_defaults"] / df["total_obligors"])
    )

    bucket_order = ["AAA", "A", "BBB", "BB", "CCC"]
    per_bucket["rating_bucket"] = pd.Categorical(per_bucket["rating_bucket"], categories=bucket_order, ordered=True)
    per_bucket = per_bucket.sort_values("rating_bucket").reset_index(drop=True)

    return CalibrationResult(per_year=per_year, per_bucket=per_bucket)


def _format_bp(pd_value: float) -> str:
    """Render a probability as a basis-point string for human reading."""
    return f"{pd_value * 10_000:>8.1f} bp"


def main() -> None:
    cohort = _generate_cohort(seed=42)
    print(f"Synthetic cohort: {len(cohort):,} obligor-years across "
          f"{cohort['rating_bucket'].nunique()} buckets and "
          f"{cohort['observation_year'].nunique()} years.\n")

    result = calibrate_empirical_pd(cohort)

    print("Per-bucket per-year default rates")
    print("---------------------------------")
    pivot = result.per_year.pivot(index="rating_bucket", columns="observation_year", values="pd_year")
    pivot = pivot.reindex(["AAA", "A", "BBB", "BB", "CCC"])
    print(pivot.round(4).to_string())
    print()

    print("Bucket-level empirical PDs (TTC-style)")
    print("--------------------------------------")
    for _, row in result.per_bucket.iterrows():
        bucket = row["rating_bucket"]
        n_def = int(row["total_defaults"])
        n_obs = int(row["total_obligors"])
        avg = _format_bp(float(row["pd_avg"]))
        pooled = _format_bp(float(row["pd_pooled"]))
        print(f"  {bucket:<4}  defaults={n_def:>3}/{n_obs:<4}  pd_avg={avg}   pd_pooled={pooled}")
    print()

    aaa = result.per_bucket.loc[result.per_bucket["rating_bucket"] == "AAA"].iloc[0]
    if int(aaa["total_defaults"]) == 0:
        print("Note: zero observed defaults in the AAA bucket across the entire window.")
        print("      The empirical PD is 0 bp, which is structurally implausible. This")
        print("      is the Low-Default-Portfolio (LDP) problem in miniature: the")
        print("      empirical estimator collapses, and the calibration team must")
        print("      reach for pooling, Bayesian shrinkage toward an expert prior, or")
        print("      a regulatory margin of conservatism.")


if __name__ == "__main__":
    main()
