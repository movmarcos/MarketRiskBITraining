# Credit Module 9 — Exposure at Default

!!! abstract "Module Goal"
    Exposure at Default (EAD) is the third of the three drivers in the Expected Loss identity (PD × LGD × EAD) and the one where the data engineer has the most leverage. For a fully-drawn term loan EAD is trivial — it is the outstanding principal. For a revolver, a letter of credit, a derivative, or any contingent obligation, EAD is *a model output*: the firm has to forecast what will be drawn or owed between today and the moment of default. This module treats EAD as the data problem it is — how the warehouse stores the drawn-vs-undrawn snapshot that feeds CCF calibration, how derivatives EAD is decomposed into current exposure plus PFE, how SA-CCR and IMM differ at the conceptual level, where wrong-way risk fits in, and how `fact_ead_calculation` accommodates all of these on a single grain.

---

## 1. Learning objectives

By the end of this module, you should be able to:

- **Define** Exposure at Default across funded and unfunded exposures, distinguishing the trivial cases from the model-output cases.
- **Apply** the Credit Conversion Factor (CCF) to revolving facilities to convert an undrawn commitment into an expected EAD.
- **Distinguish** current exposure from Potential Future Exposure (PFE) for derivatives, and articulate why both are needed for an EAD figure.
- **Identify** wrong-way risk and recognise when an exposure deserves a WWR flag in the warehouse.
- **Design** the `fact_ead_calculation` table at a grain that supports book EAD, SA-CCR EAD, and IMM EAD simultaneously without proliferating fact tables.
- **Trace** the drawn-vs-undrawn snapshot from the loan-accounting system through `fact_facility_drawn_undrawn` to the CCF calibration team.

## 2. Why this matters

EAD is the dollar amount at risk. It sounds like the easiest of the three credit parameters — "what is the outstanding?" — and for the simplest products (a fully-disbursed term loan amortising on a fixed schedule) the answer really is that simple. For everything else — and "everything else" is the bulk of a real credit book — EAD is a *forecast*, not a fact. A $100M revolver that is currently undrawn could be undrawn at default, fully drawn at default, or anywhere in between, and the firm has to commit to a single EAD figure today so the PD × LGD × EAD product produces an expected-loss number that downstream consumers can actually use. The CCF (credit conversion factor) is the bridge from the snapshot the loan system reports to the EAD the credit warehouse stores; the data engineer's job is to give the model team the historical drawdown timelines they need to calibrate the CCF, and to store the resulting EAD on a row shape that a regulatory consumer, an internal credit committee, and an IFRS 9 ECL model can all read without re-deriving anything.

Get EAD wrong and the entire expected-loss chain is wrong by the same factor. A 20% understatement of EAD across a $5B revolver portfolio is a $1B understatement of the firm's gross exposure and a proportional understatement of the IFRS 9 stage 2 / stage 3 provisions and of the Basel IRB capital number. Unlike PD (which is an obligor attribute and is therefore correlated across many facilities) and unlike LGD (which has a workout-team validation cycle that catches errors years after the fact), EAD errors are *immediate* and *facility-specific* — a CCF that is wrong for corporate revolvers will be wrong on day one and will stay wrong until someone notices that the realised drawdown experience over a recession or two has diverged from the calibrated figure. The data engineer who owns the drawn-vs-undrawn pipeline is the early-warning system for this problem.

The third reason EAD matters is structural: it is the only one of the three credit parameters whose data the firm *already* has on its own books. PD requires obligor financial statements, ratings, and macro context that the firm may have to source externally; LGD requires the workout team's recovery experience that the firm has to track for years; EAD requires the loan-accounting system, the derivative position store, and the collateral system — all of which the firm operates itself. The friction is not data availability; it is data *shape*. A facility-level snapshot of drawn and undrawn balances, refreshed daily, joined to a counterparty-level CCF calibration and to a derivative-level current-exposure-plus-PFE calculation, is the goal. Most of this module is about how to land that goal in a warehouse a regulator will accept and a consumer can query without writing reconciliation tickets.

The fourth and least-discussed reason EAD matters is *operational*. The EAD pipeline is the most-read of the three credit-parameter pipelines on a normal business day. The PD pipeline produces a number that updates monthly or quarterly per obligor; the LGD pipeline produces numbers that mostly do not change for years (until a defaulted-case workout closes). The EAD pipeline produces numbers that change *every business day* for every facility — every drawdown, every repayment, every new trade, every MTM movement, every collateral exchange ripples through to the EAD figure. A credit-committee surveillance pack is a daily artefact; an IFRS 9 ECL provision is a quarterly artefact; a regulatory capital number is a quarterly artefact with daily monitoring. All three consume EAD with a daily refresh expectation. Latency budgets that are generous for PD and LGD ("the new figure is available within two business days of month-end") are intolerable for EAD — the surveillance team wants today's EAD by start-of-business tomorrow, and a pipeline that misses the SLA produces a credit-committee briefing with stale exposure figures. The data engineer's operational discipline around the EAD pipeline (monitoring, late-arriving data handling, intraday refresh for the highest-priority counterparties) is what makes the firm's daily credit surveillance possible.

!!! info "Honesty disclaimer"
    This module reflects general industry knowledge of EAD methodology as of mid-2026. Specific CCF calibration choices, derivative-EAD methodology (SA-CCR formulas vs. internal models), and wrong-way-risk classification practice vary substantially by firm, by jurisdiction, and by product family (a US bank holding company under the Federal Reserve's IMM-approved framework treats derivatives EAD very differently from a mid-tier European bank using the standardised SA-CCR formula). Deep model territory — the SA-CCR add-on formulas in full, the calibration of the multi-factor IMM models, the granular treatment of margin-period-of-risk adjustments and initial-margin add-ons — is beyond this module's scope; pointers in further reading. The goal here is to give the data professional enough vocabulary and pattern recognition to support the credit-risk model team and the regulatory-reporting team without becoming one. Where the author's confidence drops (typically inside SA-CCR's asset-class-specific add-on parameters or jurisdiction-specific WWR capital treatment), the module says so explicitly.

## 3. Core concepts

A reading map:

- §3.1 pins the formal definition and the funded-vs-unfunded distinction that drives the rest of the module.
- §3.2 walks EAD across the instrument families introduced in [Credit Instruments](04-credit-instruments.md) — term loans, revolvers, letters of credit, bonds, derivatives, securitisation tranches — and shows where the data-engineering work concentrates.
- §3.3 treats the CCF: what it is, what data its calibration needs, and how the warehouse stores both the calibrated values and the historical drawdown experience the calibration ran on.
- §3.4 introduces derivatives EAD as current exposure plus PFE.
- §3.5 covers SA-CCR and IMM at the conceptual level the data engineer needs.
- §3.6 covers wrong-way risk and its general/specific flavours.
- §3.7 introduces netting and collateral effects on EAD as a teaser for the dedicated Collateral & Netting module.
- §3.8 walks the drawn-vs-undrawn fact-table pattern, the foundation of every CCF calibration the firm ever runs.
- §3.9 lands on the storage shape: `fact_ead_calculation`, the unified EAD row that accommodates book, SA-CCR, and IMM figures on a single grain.
- §3.10 closes with the operational cadence — daily batch, intraday refresh, event-driven recalculation — that distinguishes the EAD pipeline from the slower PD and LGD pipelines.

### 3.1 Definition

**Exposure at Default** for a facility is the expected gross exposure the firm will have to the obligor at the moment of default. Three things to pin immediately:

- **Units.** EAD is a dollar amount (or the reporting-currency equivalent). It is stored as a signed numeric in the warehouse, but the sign convention should be *always positive from the firm's perspective* — a positive EAD means the firm is owed money or will be owed money at default. Negative EADs are nonsense (a firm cannot have a negative gross exposure to a counterparty); the rare apparent-negative case for a derivative netting set whose net MTM is in the counterparty's favour is handled by flooring the EAD at zero, not by storing a negative number.
- **"Gross" qualifier.** EAD is gross of LGD — it is the amount the firm is *exposed to*, not the amount it expects to *lose*. The expected loss is EAD × LGD; EAD on its own is the denominator of the loss-given-default ratio, not a loss figure. A consumer who sees a $50M EAD and reads it as a $50M loss has misread the column; the data dictionary must spell this out.
- **"At default" qualifier.** EAD is the exposure *at the time of default*, not today. For a fully-drawn term loan with no further draws available, today's exposure equals the at-default exposure (modulo amortisation between now and default). For a revolver, the at-default exposure typically exceeds today's drawn balance because obligors tend to draw down their available lines as they slide toward default — the "drawn-down-in-distress" pattern is the entire reason CCFs exist.

The default *event* itself is the same Basel "unlikely to pay" or "90 days past due" trigger that the [PD module](07-probability-of-default.md) and the [LGD module](08-loss-given-default.md) reference; EAD measures *what is owed when that event fires*.

!!! info "Definition: EAD vs. exposure (general use) vs. notional"
    These three terms surface in different reports and sometimes get conflated. **Exposure** in general use can mean almost anything — current MTM, drawn balance, headline notional, gross-of-collateral net-of-netting, depending on the speaker. **Notional** is the contractual reference amount — the face value of a swap or the original commitment of a loan — and is rarely the right credit-risk number for derivatives (a $100M notional IRS rarely has a $100M EAD). **EAD** is the specific credit-risk concept: the expected gross exposure at the time of default, with the precise methodology depending on the instrument family (§3.2) and the regulatory framework (§3.5). A column labelled `exposure_usd` on a fact table without further qualification is a data-dictionary failure waiting to be discovered; `ead_usd` with the methodology and aggregation level explicit is the disciplined alternative.

A small comparison table to keep visible at the BI layer:

| Term | Meaning | Typical context | When EAD differs |
|---|---|---|---|
| Notional | Contractual face / reference amount | Trade booking, market-risk | Derivatives (EAD << notional); revolvers (EAD < notional unless 100% CCF) |
| Drawn balance | Currently disbursed principal | Loan accounting, daily reporting | Revolvers (EAD > drawn); contingent obligations (EAD > 0 while drawn = 0) |
| Current exposure | Positive MTM (for derivatives) | Daily credit surveillance, trader view | Long-dated derivatives (EAD > current via PFE); collateralised (EAD < current via collateral relief) |
| Commitment | Total amount the bank is contractually bound to provide | Credit-limit reporting | Always: EAD includes a fraction of the undrawn commitment via CCF |
| EAD | The specific at-default exposure, methodology-stamped | Capital, ECL, regulatory reporting | (This is the column with the disciplined definition) |

!!! info "Definition: funded vs. unfunded exposure"
    **Funded exposure** is the part of a facility where the firm has already disbursed cash — the drawn balance on a loan, the bought face value of a bond, the principal of a securitisation tranche the firm holds. The cash is at risk now.

    **Unfunded exposure** is the part of a facility where the firm has *committed* to disburse cash on demand but has not yet done so — the undrawn portion of a revolver, the contingent liability of an issued standby letter of credit, the unfunded portion of a syndicated commitment. The cash is not at risk *yet* but the firm has bound itself to provide it under contractually-defined circumstances. CCF is the bridge from unfunded to a forecasted exposure-at-default figure.

### 3.2 EAD by instrument family

The work the EAD pipeline has to do varies enormously by instrument family. The table below summarises the canonical decomposition, with the typical CCF range the model team would calibrate to. The CCF figures are *indicative ranges* drawn from published regulatory-floor numbers and from peer-bank disclosures; your own calibration will differ, and the calibration is the model team's job, not the data engineer's.

| Instrument family | EAD formula | Typical CCF range | Data shape required |
|---|---|---|---|
| Term loan (fully drawn) | Outstanding principal | n/a (no undrawn) | Daily outstanding from loan accounting |
| Revolver / credit line | drawn + CCF × undrawn | 40-75% corporate, 50-100% retail | Daily drawn + undrawn snapshot |
| Letter of credit / standby | issued amount × CCF | 50-100% (varies by type) | Issued LC inventory + CCF table |
| Guarantee / surety | guaranteed amount × CCF | 100% (typically) | Guarantee inventory |
| Bond (held) | Face value (or market value, per convention) | n/a | Position store |
| OTC derivative (uncollateralised) | current exposure + PFE | n/a (PFE replaces CCF) | MTM feed + risk-factor simulation |
| OTC derivative (collateralised) | (current exposure − collateral) + add-on | n/a | MTM + collateral + PFE |
| Exchange-traded derivative | Initial margin posted | n/a | Exchange margin feed |
| Securitisation tranche | Outstanding principal × prepayment adjustment | n/a | Position + prepayment model |
| Repo / SFT | (cash lent − collateral value) × haircut | n/a (haircut replaces CCF) | Trade store + collateral schedule |

Walking the rows briefly.

**Term loan.** The trivial case. The loan-accounting system reports the outstanding principal daily; EAD equals that figure (allowing for the scheduled amortisation between today and the projected default date if the firm cares to be precise — most do not, since the model PD horizon is typically one year and amortisation within a year is small for the majority of corporate term loans). The data engineer's only obligation is to keep the daily outstanding snapshot landed reliably.

**Revolver / credit line.** The marquee case for the CCF. Today's drawn balance is observable; tomorrow's drawn balance is not. The standard formula:

$$
\text{EAD}_\text{revolver} = \text{drawn}_t + \text{CCF} \times \text{undrawn}_t
$$

where the CCF is the fraction of the *currently undrawn* commitment that the model team expects to be drawn between today and default. A facility currently drawn $15M of a $50M commitment with a 60% CCF has an EAD of $15M + 0.60 × $35M = $36M — more than twice today's drawn balance, reflecting the empirically observed pattern that distressed obligors draw down their available lines.

**Letter of credit / standby.** A *contingent* obligation: the firm has issued a guarantee that it will pay a beneficiary if the obligor fails to perform on the underlying contract. The exposure crystallises only if the LC is called. The CCF here is the probability-weighted expected fraction of the LC face value that will be drawn between today and the obligor's default. Commercial LCs (backing trade transactions, usually short-dated, typically self-liquidating) carry lower CCFs than financial standby LCs (backing financial obligations of the obligor to third parties). The Basel standardised CCF for commercial LCs is 20% and for financial standby LCs is 100%; internal models can produce numbers in between, but the regulatory floor matters for capital reporting.

**Guarantee / surety.** Typically treated as a 100% CCF exposure — if the firm has guaranteed the obligation, the assumption is that on the obligor's default the firm will be called to pay in full. Some refinements (parent guarantees with multiple subsidiaries, surety bonds with claim-specific triggers) carry lower effective CCFs, but the conservative default is 100%.

**Bond (held).** EAD on a held bond depends on the convention. The Basel standardised approach uses *face value* as EAD (the principal the bond will pay at maturity if it does not default; the figure that would be owed in a bankruptcy claim). IFRS 9 ECL uses *amortised cost* (close to face for bonds bought near par; below face for bonds bought at a discount; above face for bonds bought at a premium). Trading-book bonds use *fair value*. The warehouse should carry the bond's outstanding face value as a measure on `fact_position` regardless of accounting convention, so any EAD definition can be derived; the choice between face / amortised cost / fair value belongs in the reporting layer.

**OTC derivative (uncollateralised).** The most data-intensive case. EAD = current exposure (today's positive MTM, floored at zero) plus Potential Future Exposure (the modelled-or-formulaic estimate of the additional exposure that could accumulate between today and default). Section 3.4 treats this in depth.

**OTC derivative (collateralised).** Collateral posted by the counterparty reduces the current-exposure component; the PFE component is replaced or supplemented by a *margin-period-of-risk* add-on that captures the exposure accumulated over the days between the last collateral exchange and the close-out of the position after default. Section 3.7 introduces the netting-and-collateral interaction; the dedicated [Collateral & Netting](#) module (upcoming) covers the mechanics in full.

**Exchange-traded derivative.** Cleared through a central counterparty (CCP) and continuously margined. The EAD from the bank's perspective to the counterparty is essentially zero (the CCP stands in the middle); the residual exposure is to the CCP itself, and the EAD on that exposure is typically the bank's posted initial margin (the amount the CCP could keep in the worst case). Different conceptually from bilateral derivative EAD; the data engineer should not conflate them.

**Securitisation tranche.** EAD is the outstanding principal of the tranche, adjusted for expected prepayments of the underlying pool. The prepayment adjustment is itself a model output and depends on the underlying asset class (auto-loan ABS prepay differently from mortgage RMBS); the data engineer's job is to carry both the contractual principal and the prepayment-adjusted figure, with the model version that produced the adjustment.

**Repo / securities-financing transaction.** EAD is the *imbalance* between the cash leg and the collateral leg: the amount by which the cash lent exceeds the collateral received (or vice versa), grossed up by a haircut that anticipates how much the collateral value could fall before the firm can liquidate it. SFT-EAD calculations have their own dedicated regulatory framework (the Comprehensive Approach for collateral, with prescribed supervisory haircuts) that runs parallel to the derivatives SA-CCR.

A note on **product variation within families**. The table is necessarily a coarse summary; within each row there are sub-cases that change the EAD treatment. Within "revolver", an *unconditionally cancellable* line (the bank can revoke the undrawn commitment at any time without notice) carries a much lower CCF under Basel — typically 10% — than an *uncommitted but not cancellable* line. Within "letter of credit", a *commercial* LC (backing a trade transaction with self-liquidating cash flow) carries 20% CCF; a *financial* standby LC (backing a financial obligation, where the underlying is itself credit-sensitive) carries 100%. Within "OTC derivative", a *bilaterally cleared* trade with daily variation margin and a 10-day margin period of risk produces a different SA-CCR EAD than the same trade *cleared through a CCP* with intraday margining. The data engineer's job is not to memorise every sub-case but to ensure the trade-level metadata carries enough attributes (`commitment_type`, `lc_type`, `clearing_status`, `margin_frequency`) that the methodology engine can pick the right formula.

The data-engineering takeaway: *one* fact table cannot store EAD in a single number column without losing the methodology. The pattern this module recommends — `fact_ead_calculation` with an `ead_type` column distinguishing BOOK / SA-CCR / IMM, and per-row methodology metadata — accommodates all of the families above on a single grain. Section 3.9 lays it out.

### 3.3 The Credit Conversion Factor and its calibration data

The CCF is the empirical bridge from a snapshot of today's drawn-vs-undrawn balance to a forecast of the drawn balance at default. The Basel framework defines it formally:

$$
\text{CCF} = \frac{\mathbb{E}[\text{drawn at default}] - \text{drawn at observation}}{\text{undrawn at observation}}
$$

— the *additional* drawdown between observation and default, expressed as a fraction of the available undrawn commitment. A CCF of zero means the obligor on average does not draw further before default (rare for revolvers, common for term loans with no available re-draw); a CCF of 100% means the obligor draws the full available commitment before defaulting (common for badly-monitored facilities in stressed obligors); a CCF in the 40-75% range is typical for well-monitored corporate revolvers across the cycle.

For each segment of the book — corporate revolvers, retail credit lines, working-capital facilities, project-finance commitments, etc. — the calibration team needs a panel of historical observations of the form `(facility_id, observation_date, undrawn_at_observation, drawn_at_default, days_between_observation_and_default)`. The CCF for the segment is computed (in the simplest form) as the EAD-weighted average of `(drawn_at_default − drawn_at_observation) / undrawn_at_observation` across the panel. More sophisticated calibrations apply econometric models that condition on macro state, obligor rating, time-to-default, and remaining commitment tenor; the warehouse's job is to enable both the simple and the sophisticated calibrations by carrying the underlying drawdown timeline at sufficient granularity.

"Sufficient granularity" in practice means **monthly snapshots of every active facility's drawn and undrawn balance**, retained for the full history the calibration team needs (typically 5-7 years for cycle coverage). Daily snapshots are nicer but typically excessive — the calibration is run quarterly or annually, drawdowns within a month are usually noise, and the storage cost of daily snapshots across a multi-million-facility retail book quickly outweighs the calibration precision gained. The compromise most large banks reach: **daily for active corporate facilities, monthly for retail, end-of-period for closed facilities**, with the as-of-snapshot date stamped on every row.

A second-order point on **CCF segmentation**. A single CCF for the firm's entire revolver book is the wrong abstraction — corporate revolvers and retail credit lines have CCFs that differ by 20+ percentage points, and rated-vs-unrated corporate revolvers can also differ materially. The calibration team will segment on (at minimum) product type, obligor type (corporate / SME / retail), and obligor rating bucket. The data engineer's role: ensure `dim_facility` and `dim_obligor` carry the columns the segmentation requires, and ensure the segmentation key is stable across time (a CCF calibrated on a segment whose membership definition has drifted is a bad CCF). The Common Pitfalls section returns to single-CCF-for-all-revolvers as the most common source of EAD error.

A third-order point on **point-in-time vs. through-the-cycle CCF**. The same PIT vs. TTC distinction that the [PD module](07-probability-of-default.md) treats applies to the CCF. A PIT CCF for corporate revolvers in a recession year might be 70% (everyone draws down); a TTC CCF for the same segment might be 55% (cycle average). Basel IRB capital uses the long-run downturn CCF (similar logic to the downturn-LGD requirement); IFRS 9 ECL uses point-in-time-conditional CCFs. Two columns on `fact_ead_calculation` — `applied_ccf` and `applied_ccf_basis` (PIT / TTC / DOWNTURN) — let both downstream consumers read the right figure without re-deriving from the calibration data.

A fourth-order point on **observation windows and survivorship**. CCF calibration has a structural survivorship problem that the PD calibration does not have to the same degree. A CCF observation is meaningful only if the facility *defaulted* — the calibrator needs to compare drawn-at-default to drawn-at-observation, which requires the default event to have happened. Facilities that *did not* default contribute no observations to the CCF panel, even though their drawdown experience is informative about how facilities behave in normal times. The standard treatment: pool defaulted facilities across multiple cohorts (12-month-pre-default, 6-month-pre-default, 3-month-pre-default observation windows for each defaulted facility) to multiply the effective sample size, then check that the implied CCFs at the different windows are consistent. A meaningful divergence (12-month CCF much lower than 3-month CCF) is the empirical signal of the "drawn-down-in-distress" pattern; a small divergence suggests the obligor's drawdown behaviour is roughly steady through the year before default. The data engineer's role: keep the snapshot pipeline at sufficient granularity that the calibrator can pick any pre-default window and have data, rather than being forced into a single canonical window.

### 3.4 Current exposure vs. PFE for derivatives

For derivatives the EAD decomposition has two parts:

$$
\text{EAD}_\text{derivative} = \text{Current Exposure} + \text{Potential Future Exposure}
$$

**Current exposure** is the maximum of today's mark-to-market and zero. For an at-par freshly-traded swap, the current exposure is essentially zero (the swap is priced to zero MTM at trade). For a five-year-old in-the-money swap, the current exposure is the positive MTM the bank would crystallise if the counterparty defaulted today. The MTM feed from the derivatives pricing system is the data engineer's input; the floor at zero converts an MTM that could be positive or negative into a *credit exposure* that is by definition non-negative.

**Potential Future Exposure** is the modelled estimate of the *additional* exposure that could accumulate between today and the eventual default. Two facts about PFE drive the data-engineering work:

- **PFE is a profile over time, not a single number.** Exposure to a derivative diffuses with time — uncertainty about future interest rates, FX rates, and credit spreads compounds, and an at-par swap that has zero MTM today could have +$5M MTM in two years. The PFE profile typically rises with the square root of time (the standard diffusion shape) until the swap's remaining life begins to compress the exposure, then falls toward zero at maturity. The PFE at *any single point in time* is a quantile (typically the 95th or 97.5th percentile) of the distribution of positive MTM at that time across simulated paths. The *peak PFE* over the swap's life is often the headline number the credit-committee surveillance pack quotes; the *expected positive exposure (EPE) profile* — the mean of max(MTM, 0) at each time — is the figure that feeds the regulatory capital calculation in many jurisdictions.
- **PFE depends on the netting set, not on the individual trade.** A single trade has positive and negative exposures depending on the path; a portfolio of trades with the same counterparty under an enforceable netting agreement has *net* exposure that is much smaller than the sum of individual gross exposures. PFE must be computed at the netting-set grain — the dedicated [Collateral & Netting](#) module returns to this.

A stylised PFE profile diagram for a 10-year interest-rate swap, the kind of shape that recurs across every vanilla-derivative exposure:

```text
                Stylised PFE profile — 10y vanilla IRS, single trade
                (vertical axis: PFE 95% in $M; horizontal axis: time in years)

   PFE
   $2M  |          *  *  *
        |       *           *
        |     *                *
   $1M  |   *                     *
        |  *                          *
        | *                              *
        |*                                  *
   $0M  +-+--+--+--+--+--+--+--+--+--+--+--+--> t
        0  1  2  3  4  5  6  7  8  9 10

         Rises with diffusion in the early life (uncertainty grows with
         sqrt-t), peaks around the swap's quarter-to-mid life, then falls
         toward zero at maturity as the remaining tenor compresses the
         exposure. The peak typically sits around 1/3 to 1/2 of the swap's
         life — the exact location depends on the rate-process volatility,
         the swap's payment frequency, and the discount factor's behaviour.
```

The actual numerical PFE profile produced by the Example 2 Monte-Carlo simulation in §4 produces a peak around year 2.5-3 for the chosen Vasicek parameters and a fall-off toward year 10, which matches the qualitative shape above. The shape is robust to the modelling choice (any sensible diffusion model produces something similar); the *level* of the peak is highly sensitive to the volatility assumption and to the calibration of the discount and forecasting curves, which is why the production SA-CCR formula and the production IMM model produce different numbers from the simplified scaffold in §4.

The data engineer does not run the PFE model. The data engineer stores the model's outputs on `fact_ead_calculation` with sufficient metadata that a downstream consumer can:

- Read the headline EAD figure (current + PFE, possibly netted, possibly collateral-reduced) for capital reporting.
- Read the PFE profile points (the 95th percentile at each time-bucket, the EPE at each time-bucket) for credit-committee surveillance.
- Re-derive any of the above from the underlying MTM feed and the stored PFE inputs, for forensic reconstruction or for model validation.

A note on **the quantile-vs-mean ambiguity at the PFE layer**. "PFE" in everyday credit-team usage almost always refers to the *peak* of the time profile at a specified confidence quantile (the maximum across time of the 95th percentile of positive MTM). "EPE" — Expected Positive Exposure — refers to the *time-average* of the *mean* of positive MTM. "EEPE" — Effective Expected Positive Exposure — is the regulatory variant that takes the running maximum of EPE up to each time point before averaging, which the regulatory capital formula consumes. A consumer who says "give me the EAD" without specifying which of (peak PFE, EPE, EEPE) they want is asking an ambiguous question; the warehouse should expose all three on `fact_ead_calculation` rows (often as a small set of measures rather than separate rows: `peak_pfe_usd`, `epe_usd`, `eepe_usd`) and let the consumer pick. The most common silent bug at the derivatives EAD layer is reporting the peak PFE in a context that wants EEPE, which inflates the figure by a factor of 2-3× and produces a surprising capital surplus that, on investigation, turns out to be a labelling error rather than a real over-collateralisation.

### 3.5 SA-CCR and IMM at the conceptual level

Two regulatory methodologies dominate derivatives EAD:

- **SA-CCR** (Standardised Approach for Counterparty Credit Risk), published as BCBS 279 in 2014 and binding for most internationally-active banks from 2017 onwards. SA-CCR replaced the older Current Exposure Method (CEM), which used a similar add-on structure but with cruder asset-class buckets and no recognition of netting beyond a naive 60% factor. SA-CCR is a *prescribed formula*: the regulator publishes the exact computation, asset-class-specific add-on parameters (the "supervisory factors"), and the rules for aggregating across trades within a netting set. The EAD under SA-CCR is:

    $$
    \text{EAD}_\text{SA-CCR} = \alpha \cdot (\text{Replacement Cost} + \text{Potential Future Exposure}_\text{SA-CCR})
    $$

    where $\alpha = 1.4$ is a fixed multiplier (the regulator's adjustment for the difference between the formula's output and the historical IMM-implied EAD), Replacement Cost is the current netted-and-collateralised MTM floored at zero, and the SA-CCR PFE is built from asset-class add-ons weighted by supervisory-prescribed factors. The formula is mechanical and reproducible; the data inputs (current MTM, collateral, trade attributes that drive the asset-class classification, netting-set membership) are the bank's responsibility.

- **IMM** (Internal Model Method) is the bank's own Monte-Carlo simulation of derivatives exposure. Subject to regulatory approval (the supervisor inspects the model, the backtesting, the model-governance framework), IMM produces an EAD that uses the bank's calibrated multi-factor model rather than the prescribed SA-CCR formula. IMM is more accurate (the bank can capture cross-asset correlations, instrument-specific features, and netting effects that SA-CCR approximates) and typically produces a lower capital number than SA-CCR for the same portfolio, which is the incentive to invest in obtaining IMM approval. The output is an *effective EAD* derived from the simulated EPE profile, with regulatory adjustments (the alpha multiplier, the margin-period-of-risk floor) layered on top.

A small comparison the BI layer should keep visible:

| Aspect | SA-CCR | IMM |
|---|---|---|
| Approval required | No — default standardised method | Yes — supervisory model approval |
| Methodology | Prescribed formula (BCBS 279) | Bank's own Monte Carlo simulation |
| Calibration | Supervisory factors fixed by regulator | Bank-calibrated risk-factor model |
| Capital outcome | Typically higher | Typically lower (the incentive to invest) |
| Floor relationship | Acts as floor for IMM banks | Floored by SA-CCR per Basel III output floor |
| Reproducibility | Deterministic given inputs | Stochastic (seed-fixed for published runs) |
| Implementation cost | Low to moderate | High (model development + ongoing validation) |
| Typical user | Mid-tier banks; all banks pre-IMM | Largest internationally-active banks |

For the data engineer, the distinction matters because the input requirements differ:

- **SA-CCR** needs: current MTM per trade, collateral per netting set, the asset-class classification of each trade (Interest Rate, FX, Credit, Equity, Commodity), the residual maturity, the notional, and a handful of trade-specific flags (e.g. whether the trade is a basis swap, a volatility-referenced trade). The formula then produces the EAD deterministically. The data engineer's challenge is the *classification* problem — getting every trade tagged with the right SA-CCR asset class and the right SA-CCR sub-bucket — and the *netting-set* problem (correctly identifying which trades are covered by which legal netting agreement).
- **IMM** needs: the same inputs as SA-CCR, plus a calibrated risk-factor evolution model (volatilities, correlations, mean-reversion parameters per risk factor), plus a trade-revaluation function that can mark each trade to market under each simulated state of the world. The model team owns the risk-factor calibration and the revaluation logic; the data engineer's role is to land the simulation outputs (typically the EPE profile and the PFE profile per netting set) onto `fact_ead_calculation` with the model version and the simulation date stamped, so a consumer can read the IMM EAD alongside the SA-CCR EAD and a reconciliation team can compare them.

A practical observation on **dual-track storage**. Most IMM-approved banks compute *both* SA-CCR and IMM and store both on `fact_ead_calculation`. The IMM figure feeds the regulatory capital (where the bank has supervisor approval to use it); the SA-CCR figure is the *floor* (the regulator requires that the IMM EAD not fall below the SA-CCR figure by more than a defined margin, to prevent gaming). A consumer who reads only one of the two misses the relationship; the warehouse should expose both with an explicit `ead_type` and let the consumer pick.

A second observation on **the practical scope of "derivatives" for EAD purposes**. SA-CCR and IMM apply to derivatives that produce *bilateral exposure*: OTC swaps, OTC forwards, OTC options, repos, and securities-financing transactions where the bank's exposure depends on the future movement of market variables. Cash bonds, loans, and other funded exposures use the simpler "outstanding × face value" or "drawn + CCF × undrawn" formulas of §3.2. The boundary between SA-CCR-eligible and not is occasionally fuzzy — a long-dated FX forward used to hedge a loan repayment is *technically* a derivative but is sometimes treated as part of the loan exposure for SA-CCR purposes; a synthetic CDS used to hedge a held bond is technically a derivative but is sometimes treated as a credit-risk transfer that reduces the bond's EAD. The data engineer's role is to keep the trade-classification tag (`ead_methodology_scope` or similar) consistent across the warehouse, so a trade that the regulatory-reporting team treats as SA-CCR-scope arrives on `fact_ead_calculation` with the right `ead_type`.

A third observation on **the margin-period-of-risk** adjustment. Collateralised derivatives still carry exposure between collateral exchanges: if the counterparty defaults today, the bank does not actually liquidate the position today — it goes through a close-out process that takes some number of days (the margin period of risk, typically 10 business days for OTC derivatives under standard CSAs, longer for less-liquid asset classes or for portfolios with disputed collateral calls). During those days the position's MTM can move, and the bank's effective exposure is the post-collateral net plus the MTM movement over the margin-period-of-risk window. SA-CCR and IMM both bake this in; the data engineer's role is to ensure the trade-level metadata carries the right margin-period-of-risk and the right collateral-call frequency for the methodology to consume. A misclassified trade (treated as daily-margined when it is actually weekly-margined) under-states the EAD by the difference between the two margin periods, which can be material for the long-dated portfolios.

### 3.6 Wrong-way risk

Wrong-way risk (WWR) is the credit-risk concept that the exposure to a counterparty can be *positively correlated* with the counterparty's probability of default — when the counterparty is most likely to fail, the exposure to them is largest. WWR makes the conventional EAD × PD product an under-statement of the expected loss, because the conventional product assumes the EAD and the PD are independent; under WWR, the EAD conditional on default is larger than the unconditional EAD.

Two flavours, with very different drivers and treatments:

- **General WWR.** The exposure and the PD are correlated through a common macro factor, but neither *causes* the other. The textbook example: a bank lends to an oil-exporting country that pegs its revenues to oil prices, and a sharp fall in oil prices simultaneously increases the country's PD (it loses its hard-currency revenue source) and increases the exposure (any FX-related derivative the country is on the right side of moves into-the-money for the bank). The correlation is driven by the macro environment that affects both legs; neither leg's movement causes the other. General WWR is hard to identify mechanically — it usually requires the credit officer's judgement, supported by the model team's correlation analysis — and is captured in capital terms through a small add-on (the regulator's bet that the conventional product systematically under-states exposure for high-correlation cases).
- **Specific WWR.** The exposure and the PD are correlated through a *structural* link in the trade itself — the counterparty's default would *cause* the exposure to be larger, or the existence of the exposure is itself a symptom of the counterparty's distress. The textbook example: a CDS sold by an affiliate of the reference entity, where the reference entity's default both triggers the CDS payout and raises the affiliate's PD (since the affiliates' fortunes are correlated). Specific WWR is regulatorily *more* punitive than general WWR — the Basel framework requires that the EAD for specific-WWR exposures be computed assuming the default has already occurred, which typically increases the EAD substantially. Specific WWR is also rarer (most trades do not have a structural correlation; the firm has to actively go looking) but materially more capital-intensive when it does arise.

The data engineer's role: carry a WWR flag on `fact_ead_calculation` and the upstream `fact_trade`, with the controlled vocabulary distinguishing the two flavours. A boolean flag is the minimum acceptable shape (`is_wwr = TRUE` / `FALSE`); a categorical column distinguishing `NONE` / `GENERAL` / `SPECIFIC` is better; a severity column (`LOW` / `MEDIUM` / `HIGH`) layered on top of the categorical is what the largest banks tend to settle on. The exercise on WWR design in §6 walks through the trade-offs.

A second observation on **how WWR enters the warehouse**. The classification is rarely automatic. A credit officer or a model-validation team flags trades or counterparties as WWR; the flag lands in a reference-data table (`dim_wwr_classification` or similar) and joins onto `fact_ead_calculation` at the trade or counterparty grain. The historical evolution of the flag — when was a counterparty first classified as WWR, when was the classification lifted, what was the rationale for each change — is itself a bitemporal data problem. The same patterns from the [Probability of Default](07-probability-of-default.md) module's treatment of rating histories apply; the WWR classification is a slowly-changing dimension that needs SCD-type-2 handling.

A third observation on **the capital arithmetic for WWR**. The Basel framework treats general WWR through a small uplift on the EAD computation for the affected trades — typically through the SA-CCR alpha multiplier being applied at the higher (1.4) value with no offset, where some trade categories would otherwise qualify for relief. Specific WWR is treated more punitively: the EAD for a specific-WWR trade is computed *as if the default has already occurred* (the counterparty's PD = 1 conditional state), which typically produces an EAD multiple times the unconditional figure. The capital calculation then applies the normal risk weight to that much-larger EAD, producing a capital charge that can be 3-10× the equivalent non-WWR trade's charge. The data engineer's role is again to flag the trades and let the model team apply the methodology; the warehouse should never silently apply the WWR uplift in the EAD column without preserving the unconditional figure too, because consumers may need both (the unconditional EAD for management reporting, the WWR-adjusted EAD for regulatory capital).

A fourth observation on **portfolio-level WWR concentration**. Even when individual trades carry no specific WWR flag, the *portfolio* may have a general WWR exposure if the counterparty mix concentrates in a single macro factor (a portfolio of emerging-market FX trades all on the same regional currency block, a portfolio of energy-sector commodity swaps all referencing oil). The data engineer's contribution to portfolio-level WWR is a denormalised concentration view that aggregates EADs by macro-factor exposure (region × asset class × counterparty type), surfacing the concentrations the credit-committee surveillance pack should investigate. The boundary between "general WWR that deserves an EAD uplift" and "a normal concentration that deserves a limit-management response" is judgemental and belongs to the credit-policy team, not the data engineer.

### 3.7 Netting and collateral effects on EAD

Two operational realities reshape EAD for derivatives before any model produces a number. The dedicated [Collateral & Netting](#) module (upcoming in Phase 4) treats the mechanics in full; this section introduces the data-engineering shape EAD needs.

**Netting agreements.** A bilateral trading relationship governed by an ISDA Master Agreement (or its repo equivalent, the GMRA, or the securities-lending GMSLA) allows positive and negative exposures across trades with the same counterparty to *net* — the bank's exposure to the counterparty is the net positive position across all trades within the netting set, not the gross of positive positions ignoring the negative offsets. The reduction can be dramatic: a counterparty with 200 trades, 100 of which are +$1M MTM and 100 of which are −$1M MTM, has a gross positive exposure of $100M and a net exposure of $0 if all 200 are in the same netting set. EAD must be computed at the *netting-set* grain, not the trade grain. The data engineer's contribution: a `dim_netting_set` dimension carrying the legal agreement identifier and the as-of validity period (netting agreements are negotiated, amended, and occasionally terminated; the membership of a netting set is bitemporal), and a `netting_set_id` column on every trade-level fact that participates.

**Collateral.** Posted collateral reduces the EAD by the collateral's value, adjusted for a haircut that anticipates how much the collateral could fall in value before the bank could liquidate it. For a netting set with a net positive MTM of $20M backed by $15M of cash collateral with a 0% haircut, the *replacement cost* component of the SA-CCR or IMM EAD is $5M (the under-collateralised excess). If the collateral is non-cash (e.g. $15M of US Treasuries with a 2% haircut), the effective collateral value is $15M × 0.98 = $14.7M and the replacement cost is $5.3M. The PFE add-on on top of replacement cost is also collateral-aware: a fully-collateralised portfolio still has PFE because between collateral exchanges the MTM can move, but the PFE is much smaller than for an uncollateralised portfolio.

The data engineer's contribution to the collateral side: a `fact_collateral_value` table carrying the collateral piece's value, the haircut applied, and the netting set it backs, all bitemporally — collateral valuations move daily for financial collateral, less frequently for non-financial; the haircut schedule itself moves as the regulator updates supervisory haircuts; the collateral-to-netting-set assignment moves as the bank rebalances posted collateral. The dedicated module treats the lifecycle.

The takeaway for EAD: the warehouse must store EAD figures at three nested grains depending on the consumer's need.

- **Trade grain.** Raw current exposure per trade (positive MTM floored at zero), pre-netting and pre-collateral. Useful for trader and PnL attribution, not for credit.
- **Netting-set grain.** Netted MTM, pre-collateral. The intermediate figure SA-CCR's replacement-cost formula consumes.
- **Netting-set grain with collateral.** Netted MTM minus haircut-adjusted collateral, plus a PFE add-on that reflects the post-collateral dynamics. This is the EAD figure that feeds the regulatory capital calculation.

The data engineer's `fact_ead_calculation` carries all three (typically as multiple rows with an `ead_aggregation_level` column distinguishing them), so a downstream consumer can read whichever level matches their use case without re-deriving from raw inputs.

A second-order point on **the legal-vs-operational distinction in netting**. A netting agreement is *enforceable* only if the relevant legal opinion confirms that it would hold up in the counterparty's jurisdiction in a default scenario; an unenforceable netting agreement provides no EAD relief regardless of what the contract document says. The legal team maintains the list of jurisdictions with positive netting opinions (typically published by ISDA in their annual netting-opinion update); the data engineer's role is to flag netting sets whose counterparty jurisdiction is *not* on the list and exclude them from the netting recognition in the EAD calculation. A common silent bug: a netting set is assumed enforceable in the warehouse, but the counterparty's legal jurisdiction changed (a re-domiciliation, a regulatory carve-out) and the agreement is no longer enforceable; the netting relief should drop away but the warehouse continues to apply it. The reconciliation against the legal team's quarterly opinion update catches this.

A third-order point on **collateral re-hypothecation**. When the bank *posts* collateral to a counterparty (rather than receiving it), the collateral the bank pledges can sometimes be re-hypothecated by the counterparty — used by them as collateral against their own obligations to third parties. Re-hypothecated collateral that cannot be recovered from a bankrupt counterparty creates a second exposure (the bank's claim on the re-hypothecated collateral) that sits alongside the derivative exposure. The data engineer's role: track posted collateral on `fact_collateral_value` with the re-hypothecation flag, and flag the additional exposure to the credit team when the counterparty is on a heightened-risk list.

### 3.8 The drawn-vs-undrawn fact table

The foundational data shape for CCF calibration and for revolver-EAD reporting is `fact_facility_drawn_undrawn`. The grain is `(facility_id, business_date)` for active facilities, with daily refresh for corporate facilities and typically monthly refresh for retail facilities. A minimal column set:

```sql
CREATE TABLE fact_facility_drawn_undrawn (
    facility_id             VARCHAR(64)              NOT NULL,
    business_date           DATE                     NOT NULL,
    drawn_usd               NUMERIC(18, 2)           NOT NULL,    -- principal currently outstanding
    undrawn_usd             NUMERIC(18, 2)           NOT NULL,    -- commitment less drawn
    total_commitment_usd    NUMERIC(18, 2)           NOT NULL,    -- the bank's binding obligation
    available_to_draw_usd   NUMERIC(18, 2),                       -- can differ from undrawn (covenant blocks etc.)
    facility_status         VARCHAR(16)              NOT NULL,    -- ACTIVE / MATURED / CLOSED / CANCELLED
    source_system           VARCHAR(32)              NOT NULL,
    as_of_timestamp         TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (facility_id, business_date, as_of_timestamp),
    CHECK (drawn_usd >= 0),
    CHECK (undrawn_usd >= 0),
    CHECK (drawn_usd + undrawn_usd <= total_commitment_usd + 0.01)  -- tiny rounding tolerance
);
```

Three observations on the shape:

- **`drawn + undrawn` is not always exactly `total_commitment`.** A facility may have a "borrowing base" mechanism that adjusts the available drawing capacity below the headline commitment (asset-based lending, where the commitment is conditional on the value of pledged inventory and receivables); a facility may be subject to a covenant block that prevents further draws until the obligor cures a covenant breach. The `available_to_draw_usd` column captures the *actually drawable* figure, which can be lower than `undrawn_usd`. The CCF calibration should use the drawable figure, not the contractual undrawn, because an obligor cannot draw what is not available.
- **`facility_status` is load-bearing for calibration.** A CCF calibration sample built from `WHERE facility_status = 'ACTIVE'` misses the cases that closed during the observation window; a calibration built from `WHERE facility_status IN ('ACTIVE', 'MATURED', 'CLOSED')` includes them. The standard pattern: include all facilities that were active *at the observation date* and follow each one through whatever happened next, default or no default. The data engineer's responsibility is to keep `facility_status` correct and bitemporal, so a calibration that reruns later on the same panel reproduces the same observations.
- **The `as_of_timestamp` axis enables bitemporal restatement.** A drawn balance reported on business date 2026-04-15 may later be corrected (a missed transaction, a misposted draw); the correction appends a new row with a later `as_of_timestamp` rather than overwriting the original. The latest-as-of CTE pattern (see Example 1) selects the most recent version for each natural key.

For the corporate book the row volume is manageable — a few thousand active facilities × daily snapshots × 5 years of retention is in the low tens of millions of rows, well within standard analytic-warehouse partitioning. For a global retail book with ten million credit-card accounts, daily snapshots would produce tens of billions of rows; the monthly cadence is the standard concession, with daily reserved for newly-defaulted accounts where the CCF calibration team wants the higher-resolution timeline.

A fourth observation on **reconciliation to the source-of-truth loan system**. `fact_facility_drawn_undrawn` is derived data — the source of truth lives in the loan-accounting system, which the firm operates as the official record of every drawn balance. The warehouse fact is an extract, processed and conformed for analytical use; any discrepancy between the fact and the source system is a data-quality break that surfaces at end-of-day reconciliation. The standard pattern: a daily DQ test that sums `drawn_usd` across the warehouse fact for a given business date and compares it to the sum from the loan-system general-ledger feed, with a tolerance of (say) 0.01% of total drawn balance. A break that exceeds the tolerance is investigated before any downstream consumer reads the warehouse figure; persistent breaks indicate a feed lineage problem (a missing source row, a misposted correction, a timezone mismatch on the cut-off) that the data engineer fixes. The reconciliation log is itself audit evidence and is retained alongside the fact.

The CCF calibration team's standard query against this fact table looks something like: "for every facility that defaulted in the window 2018-2025, give me the drawn and undrawn balances at the 12-month, 6-month, 3-month, and 1-month markers before the default date". The data engineer's job is to make that query fast (typically by adding a denormalised `months_to_default` column on the fact at write-time, or by materialising a `fact_pre_default_drawdown` view that pre-computes the markers) and reproducible across re-runs.

### 3.9 Storage shape: `fact_ead_calculation`

The unifying fact table for EAD figures across all the families of §3.2 is `fact_ead_calculation`. The grain is `(facility_id, business_date, ead_type, as_of_timestamp)`, with `ead_type` distinguishing the methodology (`BOOK` / `SA-CCR` / `IMM` / `INTERNAL`) and the row carrying both the headline EAD figure and the decomposition that produced it.

```sql
CREATE TABLE fact_ead_calculation (
    facility_id              VARCHAR(64)              NOT NULL,
    business_date            DATE                     NOT NULL,
    ead_type                 VARCHAR(16)              NOT NULL,    -- 'BOOK' / 'SA-CCR' / 'IMM' / 'INTERNAL'
    ead_aggregation_level    VARCHAR(16)              NOT NULL,    -- 'TRADE' / 'FACILITY' / 'NETTING_SET'
    ead_usd                  NUMERIC(18, 2)           NOT NULL,    -- the headline figure
    current_exposure_usd     NUMERIC(18, 2),                       -- positive MTM floored at zero, or drawn
    pfe_usd                  NUMERIC(18, 2),                       -- PFE component for derivatives
    applied_ccf              NUMERIC(6, 4),                        -- CCF used (revolvers, LCs)
    applied_ccf_basis        VARCHAR(16),                          -- 'PIT' / 'TTC' / 'DOWNTURN'
    undrawn_usd              NUMERIC(18, 2),                       -- for revolver-style facilities
    collateral_value_usd     NUMERIC(18, 2),                       -- haircut-adjusted collateral
    netting_set_id           VARCHAR(64),                          -- non-NULL for derivative rows
    wwr_classification       VARCHAR(16),                          -- 'NONE' / 'GENERAL' / 'SPECIFIC'
    wwr_severity             VARCHAR(8),                           -- 'LOW' / 'MEDIUM' / 'HIGH' (optional)
    model_version            VARCHAR(32)              NOT NULL,
    source_system            VARCHAR(32)              NOT NULL,
    as_of_timestamp          TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_from               TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_to                 TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (facility_id, business_date, ead_type, ead_aggregation_level, as_of_timestamp),
    CHECK (ead_usd >= 0),
    CHECK (ead_type IN ('BOOK', 'SA-CCR', 'IMM', 'INTERNAL')),
    CHECK (ead_aggregation_level IN ('TRADE', 'FACILITY', 'NETTING_SET'))
);
```

A few design observations on this shape:

- **One facility on one business date can have multiple rows.** A derivative facility with both a SA-CCR EAD (the regulatory floor) and an IMM EAD (the bank's internal model) lands two rows on the same business date, distinguished by `ead_type`. A consumer reading "the EAD for FAC001 today" must filter on `ead_type` to pick the right one. The data dictionary should be explicit about which type each downstream consumer reads (regulatory capital reads IMM where approved, falls back to SA-CCR; IFRS 9 reads INTERNAL; daily credit-committee surveillance reads BOOK).
- **`ead_aggregation_level` separates the per-trade, per-facility, and per-netting-set figures.** The same MTM data lands at three grains; the consumer picks the level they need without re-deriving. A naive design that stored only the netting-set-grain figure would force a trader who needs the per-trade contribution to re-compute from `fact_position`; the explicit per-trade row makes the contribution queryable.
- **`applied_ccf` and `applied_ccf_basis` materialise the CCF used.** A consumer who wants to reproduce the EAD figure (or to test the sensitivity to a different CCF) needs the rate that was applied; storing it on the row removes the join to `dim_ccf_calibration` for the most common queries.
- **`collateral_value_usd` is the *haircut-adjusted* figure.** The raw collateral value sits on `fact_collateral_value`; the figure on `fact_ead_calculation` is post-haircut and reflects the effective collateral that reduced the EAD. The haircut itself (and the methodology version that produced it) belongs in the collateral fact, not duplicated here.
- **`wwr_classification` and `wwr_severity` are columns, not separate rows.** A trade is WWR or it is not; the classification does not produce a different EAD row. The columns let a consumer filter for WWR exposures (e.g. "show me all the SA-CCR EADs flagged as SPECIFIC WWR") without joining out to a reference table for the common case.
- **`model_version` is mandatory.** Reproducing an EAD figure six months later requires knowing the calibration version of the CCF (for revolvers), the SA-CCR or IMM methodology version (for derivatives), and any internal-EAD model version (for the BOOK or INTERNAL rows). A single column carries the joint version identifier; the version-to-methodology mapping sits on a `dim_ead_methodology` reference table.

The combination of these design choices produces a fact table that grows linearly with the number of active facilities × the number of EAD types × the number of aggregation levels × the business-date axis × the bitemporal restatement axis. For a global investment bank the row volume is on the order of a few hundred million to a few billion rows over a 5-year retention horizon — large but tractable with standard partitioning (`business_date`-range partitioned, clustered by `facility_id`, with `as_of_timestamp` excluded from the cluster key because the latest-as-of CTE pattern scans past it).

A second-order observation on **reconciliation**. The SA-CCR EAD for a netting set computed from the bank's data should reconcile to a regulatory reporting figure (the COREP C 34.XX templates in Europe, the FFIEC 101 in the US) within a tight tolerance — the regulator's submission template is the authoritative external statement of the SA-CCR EAD, and the warehouse figure must match. The data engineer's reconciliation job: a daily DQ test that joins `fact_ead_calculation WHERE ead_type = 'SA-CCR'` to the regulatory submission staging area and flags any difference above (say) 0.5%. The same pattern for IMM: the warehouse figure must reconcile to the model team's official IMM output, again within a tight tolerance. Reconciliation breaks at the EAD layer are the most common reason a quarterly regulatory submission slips, and the data engineer who keeps the reconciliation green is the unsung hero of every clean filing.

A third-order observation on **the relationship between `fact_ead_calculation` and downstream EL fact tables**. The Expected Loss module (M10) introduces `fact_expected_loss` at `(facility_id, business_date, calculation_basis, as_of_timestamp)` grain, with the EL figure derived from the product PD × LGD × EAD. The natural lineage: a single row on `fact_expected_loss` joins back to one row on `fact_pd_assignment`, one row on `fact_lgd_assignment`, and one row on `fact_ead_calculation`, with the join keys carrying the methodology versions for all three. The data engineer's contribution is to ensure the three feeder rows have matching `business_date` and matching methodology bases (a PIT PD joined to a PIT LGD joined to a PIT EAD; a downturn-LGD joined to a downturn-EAD for regulatory capital; an IFRS 9 PD-LGD-EAD trio for the ECL). A mismatched basis is the most common silent bug at the EL layer; the warehouse should expose a `fact_el_basis_reconciliation` view that surfaces any EL row whose three feeder rows have inconsistent basis tags.

A fifth observation on **the cardinality math for `fact_ead_calculation`**. The grain `(facility_id, business_date, ead_type, ead_aggregation_level, as_of_timestamp)` produces row counts that grow on multiple axes. For a global bank with 500,000 active facilities, three EAD types (BOOK, SA-CCR, IMM), three aggregation levels (TRADE, FACILITY, NETTING_SET), daily business dates, and an as-of axis that picks up ~1.1 rows per business date on average (most days the row is written once; restatements account for the 0.1), the daily row insert is roughly 500,000 × 3 × 3 × 1.1 ≈ 5 million rows. Over a 5-year retention horizon that is roughly 5 million × 252 × 5 ≈ 6 billion rows. The volume is comfortably tractable for a modern columnar warehouse with date-range partitioning but is not negligible — partition pruning, clustering on `facility_id`, and a latest-as-of materialised view are typically required for the surveillance queries to perform within the SLA. The data engineer's capacity planning should size for this volume from the start; the alternative — discovering at year three that the partitioning strategy doesn't scale — produces an expensive backfill.

A fourth-order observation on **bitemporal restatement under regulatory inquiry**. Regulators occasionally ask the bank to *re-state* historical EAD figures — sometimes because a methodology error has been discovered, sometimes because a regulatory parameter has been corrected with retroactive effect, sometimes because a target review-of-internal-models exercise has identified an issue requiring re-run. The bitemporal pattern (the `as_of_timestamp` axis on `fact_ead_calculation`) is precisely what enables this without rewriting history: the corrected figures land as new rows with later as-of timestamps; the original rows remain queryable; a forensic reconstruction of "what the warehouse said about EAD on business-date X as of system-date Y" is exact. The cost is that consumers must always filter on the latest as-of for the relevant system-date, never assume the natural-key uniquely identifies a row. The conventions are the same as for PD's rating-restatement pattern; the difference for EAD is that restatements happen more frequently (every CCF re-calibration produces a restatement candidate; every SA-CCR methodology update produces one) and the data engineer should expect them as routine, not as exceptional.

### 3.10 Operational cadence and intraday refresh

EAD's daily-refresh expectation creates an operational profile that differs materially from the PD and LGD pipelines. The standard cadence for a large bank's EAD pipeline:

- **Overnight batch (T+0 evening to T+1 morning).** The bulk of the EAD figures are produced here:
    - Loan-accounting feeds land between 18:00 and 22:00 local time and feed `fact_facility_drawn_undrawn`.
    - Derivative MTM feeds land between 20:00 and 23:00 and feed `fact_position` for the derivatives book.
    - Collateral valuations land between 21:00 and 02:00 (collateral valuations frequently include overnight market-data inputs).
    - The SA-CCR engine runs once all derivative and collateral inputs have landed, typically completing by 04:00.
    - The IMM engine (where applicable) runs on the same inputs, completing by 06:00 — the longer runtime reflects the Monte Carlo path generation.
    - The CCF engine applies calibrated CCFs to revolver and LC inventory, typically completing by 03:00.
    - `fact_ead_calculation` is fully populated by 06:00 local time, in time for the surveillance pack's 07:00 distribution.

- **Intraday refresh windows.** For the highest-priority counterparties (typically the top 50-100 by EAD), the bank may run intraday refreshes — say at 12:00 and 16:00 — to catch large drawdowns or significant MTM movements. The intraday refresh updates a subset of facilities; the same `fact_ead_calculation` table receives the new rows with the appropriate `business_date` (typically still T+0 if the refresh is intraday) and a later `as_of_timestamp` that reflects the refresh time. Consumers reading "the latest EAD" get the intraday-refreshed figure for the subset; consumers reading "the end-of-day EAD" get the overnight batch figure.

- **Event-driven refresh.** Specific events — a large drawdown on a watch-listed facility, a credit downgrade of a top counterparty, a margin call that breaches a threshold — trigger an immediate EAD recalculation for the affected counterparty, regardless of the regular schedule. The event-driven row is again written with a later `as_of_timestamp`; downstream consumers see the new figure on the next read.

- **End-of-period special runs.** Month-end, quarter-end, and year-end produce additional reconciliation runs against external feeds (the regulatory submission staging, the general ledger close, the external auditor's tie-out). These runs may produce restated figures that land days later than the business-date they correspond to — the bitemporal pattern is exactly what accommodates the late arrival without rewriting history.

The data engineer's contribution to this cadence is to keep each of the inputs flowing reliably, to monitor the SLAs (each upstream feed has a documented "must land by" time), and to alert the credit-risk team if any feed slips. A typical alert hierarchy:

1. **INFO**: the feed landed on time but produced unusual row volume (>3σ from rolling average).
2. **WARNING**: the feed is more than 30 minutes late.
3. **CRITICAL**: the feed is more than 2 hours late, or has not landed by the surveillance-pack cut-off.

The CRITICAL alerts get the on-call data engineer paged; the WARNING alerts get triaged in the morning stand-up. The discipline of running this on-call rotation is what makes the daily credit surveillance trustworthy — the surveillance team can read the morning pack knowing that any feed slip would have triggered a pager call overnight.

## 4. Worked examples

### Example 1 — SQL: revolver EAD via the CCF formula

The first example builds a small portfolio of corporate revolvers, applies a segment-specific CCF, and rolls the resulting EAD up to obligor and industry. The goal is to make the CCF arithmetic explicit, to show the bitemporal latest-as-of join pattern in context, and to expose the most common revolver-EAD reconciliation gotchas. SQL dialect: Snowflake-compatible standard SQL; the date arithmetic is portable to any analytic warehouse.

A minimal schema:

```sql
CREATE TABLE dim_facility (
    facility_id              VARCHAR(64)              NOT NULL,
    obligor_id               VARCHAR(64)              NOT NULL,
    industry_code            VARCHAR(8)               NOT NULL,    -- NAICS-style 2-digit
    facility_type            VARCHAR(16)              NOT NULL,    -- 'REVOLVER', 'TERM_LOAN', 'LC', ...
    total_commitment_usd     NUMERIC(18, 2)           NOT NULL,
    ccf                      NUMERIC(6, 4)            NOT NULL,    -- segment-calibrated CCF
    valid_from               TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_to                 TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (facility_id, valid_from)
);

CREATE TABLE fact_facility_drawn_undrawn (
    facility_id              VARCHAR(64)              NOT NULL,
    business_date            DATE                     NOT NULL,
    drawn_usd                NUMERIC(18, 2)           NOT NULL,
    undrawn_usd              NUMERIC(18, 2)           NOT NULL,
    facility_status          VARCHAR(16)              NOT NULL,
    as_of_timestamp          TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (facility_id, business_date, as_of_timestamp)
);
```

Sample rows — five facilities across three obligors and two industries, all observed on 2026-05-07:

```sql
INSERT INTO dim_facility VALUES
    ('FAC101', 'OBL01', '32', 'REVOLVER',   50000000.00, 0.60, TIMESTAMP '2024-01-01 00:00 UTC', NULL),
    ('FAC102', 'OBL01', '32', 'REVOLVER',   30000000.00, 0.60, TIMESTAMP '2024-01-01 00:00 UTC', NULL),
    ('FAC103', 'OBL02', '32', 'REVOLVER',  100000000.00, 0.55, TIMESTAMP '2024-01-01 00:00 UTC', NULL),
    ('FAC104', 'OBL02', '32', 'TERM_LOAN',  75000000.00, 0.00, TIMESTAMP '2024-01-01 00:00 UTC', NULL),
    ('FAC105', 'OBL03', '52', 'REVOLVER',   25000000.00, 0.70, TIMESTAMP '2024-01-01 00:00 UTC', NULL);

INSERT INTO fact_facility_drawn_undrawn VALUES
    ('FAC101', DATE '2026-05-07', 15000000.00, 35000000.00, 'ACTIVE', TIMESTAMP '2026-05-08 02:00 UTC'),
    ('FAC102', DATE '2026-05-07', 10000000.00, 20000000.00, 'ACTIVE', TIMESTAMP '2026-05-08 02:00 UTC'),
    ('FAC103', DATE '2026-05-07', 45000000.00, 55000000.00, 'ACTIVE', TIMESTAMP '2026-05-08 02:00 UTC'),
    ('FAC104', DATE '2026-05-07', 75000000.00,        0.00, 'ACTIVE', TIMESTAMP '2026-05-08 02:00 UTC'),
    ('FAC105', DATE '2026-05-07',  5000000.00, 20000000.00, 'ACTIVE', TIMESTAMP '2026-05-08 02:00 UTC'),
    -- A correction landed a day later for FAC103: the previous undrawn figure missed a $5M drawdown.
    ('FAC103', DATE '2026-05-07', 50000000.00, 50000000.00, 'ACTIVE', TIMESTAMP '2026-05-09 02:00 UTC');
```

The query — per-facility EAD using `drawn + CCF × undrawn`, then aggregated to obligor and industry, with bitemporal latest-as-of handling:

```sql
WITH latest_snapshot AS (
    SELECT
        facility_id,
        business_date,
        drawn_usd,
        undrawn_usd,
        facility_status,
        ROW_NUMBER() OVER (
            PARTITION BY facility_id, business_date
            ORDER BY as_of_timestamp DESC
        ) AS rn
    FROM fact_facility_drawn_undrawn
    WHERE business_date = DATE '2026-05-07'
),
facility_ead AS (
    SELECT
        f.facility_id,
        f.obligor_id,
        f.industry_code,
        f.facility_type,
        f.total_commitment_usd,
        f.ccf,
        s.drawn_usd,
        s.undrawn_usd,
        s.drawn_usd + f.ccf * s.undrawn_usd AS ead_usd
    FROM       dim_facility            f
    INNER JOIN latest_snapshot         s ON s.facility_id = f.facility_id
                                        AND s.rn = 1
                                        AND s.facility_status = 'ACTIVE'
    WHERE TIMESTAMP '2026-05-07 23:59 UTC' BETWEEN f.valid_from AND COALESCE(f.valid_to, TIMESTAMP '9999-12-31 00:00 UTC')
)
SELECT
    obligor_id,
    industry_code,
    SUM(drawn_usd)            AS total_drawn_usd,
    SUM(undrawn_usd)          AS total_undrawn_usd,
    SUM(total_commitment_usd) AS total_commitment_usd,
    SUM(ead_usd)              AS total_ead_usd
FROM facility_ead
GROUP BY ROLLUP (industry_code, obligor_id)
ORDER BY industry_code NULLS LAST, obligor_id NULLS LAST;
```

The expected output (manually-traced from the inputs above):

| industry_code | obligor_id | total_drawn_usd | total_undrawn_usd | total_commitment_usd | total_ead_usd |
|---|---|---|---|---|---|
| 32 | OBL01 |   25,000,000 |  55,000,000 |  80,000,000 |  58,000,000 |
| 32 | OBL02 |  125,000,000 |  50,000,000 | 175,000,000 | 152,500,000 |
| 32 | NULL  |  150,000,000 | 105,000,000 | 255,000,000 | 210,500,000 |
| 52 | OBL03 |    5,000,000 |  20,000,000 |  25,000,000 |  19,000,000 |
| 52 | NULL  |    5,000,000 |  20,000,000 |  25,000,000 |  19,000,000 |
| NULL | NULL |  155,000,000 | 125,000,000 | 280,000,000 | 229,500,000 |

A line-by-line trace of the per-facility EADs that feed those aggregates:

- **FAC101.** Drawn $15M, undrawn $35M, CCF 60%. EAD = 15M + 0.60 × 35M = $36M.
- **FAC102.** Drawn $10M, undrawn $20M, CCF 60%. EAD = 10M + 0.60 × 20M = $22M.
- **FAC103.** *Note the bitemporal correction.* The original 2026-05-08 snapshot reported drawn $45M / undrawn $55M; a restated snapshot on 2026-05-09 corrected this to drawn $50M / undrawn $50M. The `latest_snapshot` CTE picks the restated version. EAD = 50M + 0.55 × 50M = $77.5M (not the $75.25M the original snapshot would have produced).
- **FAC104.** Term loan, fully drawn, CCF 0. EAD = 75M + 0 × 0 = $75M (the term-loan trivial case from §3.2).
- **FAC105.** Drawn $5M, undrawn $20M, CCF 70% (retail-style higher CCF). EAD = 5M + 0.70 × 20M = $19M.

Obligor-level aggregates:

- **OBL01** (industry 32): $36M + $22M = $58M.
- **OBL02** (industry 32): $77.5M + $75M = $152.5M.
- **OBL03** (industry 52): $19M.

Industry-level rollups: industry 32 = $58M + $152.5M = $210.5M; industry 52 = $19M; firmwide = $229.5M.

A walkthrough of the gotchas the query handles:

- **Bitemporal "latest as-of" join.** The `latest_snapshot` CTE picks the most recent `as_of_timestamp` per `(facility_id, business_date)` pair. Without it, FAC103 would appear twice in the join and double-count. This is the same pattern used in [LGD's worked example](08-loss-given-default.md) and in [PD's empirical-default-rate query](07-probability-of-default.md).
- **Dimension validity filter.** The `dim_facility` row's `valid_from` / `valid_to` window is checked against the business date to pick the correct attributes (a facility whose CCF was re-calibrated mid-year would have two SCD-type-2 rows, and the right one for 2026-05-07 must be picked).
- **`facility_status = 'ACTIVE'` filter.** A closed or matured facility should not contribute to EAD even if its last drawn-undrawn snapshot is in the panel; the status filter excludes it.
- **`ROLLUP` for the obligor and industry totals in one pass.** The `ROLLUP(industry_code, obligor_id)` produces obligor-level rows, industry-level subtotals (obligor_id NULL), and a grand total (both NULL) — useful for the credit-committee surveillance pack that wants all three views in a single query.
- **The term-loan row (FAC104) participates.** Term loans go through the same formula with CCF = 0, which collapses to drawn-only. A separate code path for term loans would be needed if the schema distinguished them; setting CCF to zero on `dim_facility` for term loans is the cleaner pattern.

A subtlety on the CCF-as-a-dim-column choice. Storing the CCF on `dim_facility` is the simplest pattern but assumes the CCF is a per-facility attribute. In practice the CCF is a *segment* attribute: every facility in a given segment gets the same CCF, and the segment is derived from (product type × obligor type × rating bucket). A more sophisticated warehouse would carry the CCF on a `dim_ccf_calibration` table keyed by the segment, joined into the EAD query via the segment-derivation logic. The simpler pattern shown here is fine for teaching and acceptable for small portfolios; large books with hundreds of segments tend to prefer the calibration-table pattern because re-calibration then updates one row per segment rather than thousands of facility rows.

A second subtlety on the **ROLLUP** subtotal rows. The query produces obligor-level rows (one per obligor-industry combination), industry-level subtotal rows (where `obligor_id IS NULL`), and a grand-total row (both NULL). A consumer pivoting this output into a credit-committee surveillance pack typically wants the obligor rows on the main grid and the subtotals on a header/footer; a query that does not distinguish them (or that produces them in separate queries) doubles the warehouse round-trips. The `ROLLUP` is the disciplined pattern; the alternative `GROUPING SETS((industry_code, obligor_id), (industry_code), ())` produces the same output with explicit set-by-set control and is preferred when the rollup hierarchy is non-trivial. The data engineer should pick one and use it consistently across the surveillance pack so consumers know what to expect in the result set.

A third subtlety on **currency handling**. The example uses USD throughout; a real bank with multi-currency exposures must convert each row to a reporting currency at a defined FX rate. The standard pattern: store balances in the *facility currency* on `fact_facility_drawn_undrawn` (so the source-of-truth tie-back to the loan-accounting system is exact), join in a `fact_fx_rate` table at the business date, and convert at query time or via a materialised reporting-currency view. The choice between query-time and materialised-view conversion is a performance trade-off; query-time is more flexible (the consumer can ask for any reporting currency) and slower (more compute per query); materialised-view is faster (the conversion is pre-computed) and rigid (only the reporting currencies materialised are queryable). Most large banks materialise USD, EUR, and GBP reporting-currency views as standard and accept the query-time cost for any other currency. The CCF arithmetic in the example is dimensionally correct in any currency — the CCF is a unitless fraction — but the *aggregation* across multiple currencies requires the FX conversion to happen before the sum, not after.

### Example 2 — Python: simplified PFE simulation for a single interest-rate swap

The second example simulates the PFE profile of a single 10-year vanilla interest-rate swap using a one-factor Vasicek short-rate model. The goal is to make the PFE-as-a-time-profile concept concrete — to show that PFE is not a single number but a curve over the swap's remaining life, and that the peak typically sits around a third to a half of the way through.

```python
--8<-- "code-samples/python/c09-simplified-pfe.py"
```

A reading guide. The script does five things:

1. **Defines a stylised vanilla IRS.** $10M notional, 10-year tenor, 3% fixed rate received from the counterparty against a floating leg priced off the simulated short rate. The bank's perspective: positive MTM means the swap is in the bank's favour and contributes to credit exposure; negative MTM is the bank's liability and is floored at zero for PFE purposes.
2. **Simulates short-rate paths under a one-factor Vasicek model.** The mean-reversion speed (κ = 0.15), long-run mean (θ = 3%), and volatility (σ = 1.2% per √year) are chosen to produce a plausible-looking rate distribution; production calibrations would derive these from market caps/swaption prices, but the qualitative shape of the resulting PFE profile is robust to the parameter choice. 1,000 paths simulated over 120 monthly time steps.
3. **Marks the swap to market on each path at each time step.** A deliberately simplified pricing model: treat the prevailing short rate at each future time as a flat discount-and-forwarding rate, value the remaining fixed leg as an annuity, and report the spread to the contracted 3% fixed rate. A real swap valuation builds a full discount curve from the simulated state; the simplification preserves the qualitative shape (MTM diffuses with time, then collapses to zero as remaining tenor shrinks) without the full curve-construction overhead. The implementation notes in the script's docstring spell out the simplification.
4. **Computes the PFE profile (95th percentile of positive MTM at each time step).** The standard regulatory PFE quantile; some firms use 97.5%. Also computes the Expected Positive Exposure profile (mean of positive MTM) as a second-line metric — EPE is the figure that feeds the regulatory capital formula in many jurisdictions and tends to be substantially smaller than PFE.
5. **Reports the time profile.** Annual sampling printed to stdout, with the peak PFE and peak EPE flagged. The expected output for the given parameters has peak PFE around year 2.5-3, falling to zero at year 10.

A representative run produces output like:

```text
Simplified PFE profile — 10y vanilla IRS, $10M notional
=======================================================
  Fixed rate (bank receives) = 3.00%
  Vasicek params: kappa=0.15, theta=0.03, sigma=0.012, r0=0.03
  Paths simulated           = 1,000
  Grid                      = monthly over 10 years (120 steps)

  Current exposure (t=0)    = $             0
  Peak PFE (95%)            = $     1,921,594 at t = 2.50 years
  Peak EPE                  = $       478,612 at t = 2.92 years

Profile snapshot (annual sampling):
  t (yrs) | PFE 95%           | EPE
  --------+-------------------+-------------------
     0.0  | $             0  | $             0
     1.0  | $     1,493,630  | $       357,675
     2.0  | $     1,890,018  | $       448,750
     3.0  | $     1,800,498  | $       464,329
     4.0  | $     1,849,052  | $       446,856
     5.0  | $     1,509,964  | $       371,256
     6.0  | $     1,399,799  | $       338,240
     7.0  | $     1,020,464  | $       256,959
     8.0  | $       673,349  | $       166,542
     9.0  | $       346,530  | $        83,425
    10.0  | $             0  | $             0
```

A few things worth noting in the output. The current exposure at t=0 is essentially zero — an at-par newly-traded swap has no immediate MTM in either direction, which is by design (the fixed rate was chosen to make the swap zero-cost at inception). The PFE grows rapidly in the early life (the diffusion of the short-rate process accumulates), peaks around year 2.5-3 (where the diffusion's growth is roughly balanced by the remaining-tenor's compression of the annuity factor), then falls toward zero as the swap approaches maturity. The peak PFE is about 19% of notional, in line with the rule of thumb that single-trade peak PFEs sit in the 10-25% range for vanilla 10-year IRSs at typical rate volatilities.

The EPE profile is much lower (peak around $0.48M vs. PFE peak of $1.92M) because the EPE is an average and the PFE is a tail quantile — the distribution of positive MTM has most of its mass near zero and a long right tail. The 4× ratio between peak PFE and peak EPE is roughly what the regulator's empirical studies see in production portfolios, and is the conceptual justification for the SA-CCR α = 1.4 multiplier (which is calibrated to bridge the EPE-style figure that the formula produces and the realised-loss-given-default figure that the historical data supports).

The acknowledgement is structural. Production SA-CCR replaces this Monte Carlo with a prescribed formula keyed to supervisory asset-class add-ons; production IMM extends the simulation to multi-factor curves, FX, equity, credit, and commodity factors, with cross-asset correlations, collateral, netting sets, and margin-period-of-risk adjustments. The 200-line script above is a teaching scaffold, not a calibration; its purpose is to make the *shape* of the PFE concept concrete, not to produce a regulatorily-defensible number. The data engineer who has run the script and looked at the output has the right mental model for what arrives on `fact_ead_calculation` from the production IMM or SA-CCR engine.

A practical observation on **storing the profile, not just the peak**. Production warehouses typically store the full PFE profile (the 95th percentile at each monthly bucket out to the swap's maturity), not just the peak figure. The profile is what the credit-committee surveillance pack visualises ("here is the PFE on our top-20 counterparty over the next 10 years"); the peak is the headline number. Both belong in the warehouse, with the peak as a derived measure and the profile as a child fact (`fact_pfe_profile` keyed by netting-set and time bucket). The relationship is the same as for VaR's headline-vs-decomposition treatment in [Value at Risk](../modules/09-value-at-risk.md) — the consumer reads the level they need and the warehouse carries enough detail to support every level.

A second practical observation on **reproducibility of the simulation output**. The Monte Carlo simulation produces a different numerical PFE each time it runs unless the random seed is fixed. Production systems typically fix the seed for any *published* PFE figure (so two runs of the same model on the same inputs produce identical results, which is what auditors expect) and re-seed only for sensitivity testing. The warehouse should carry the seed on `fact_ead_calculation` (or on the parent `dim_pfe_calibration` row), so a forensic reconstruction can re-run the simulation and verify the figure exactly. A simulation result whose seed is not stored is a result that cannot be reproduced, which is the wrong default for any number that feeds a regulatory submission.

A third practical observation on **path-count scaling**. The script uses 1,000 paths for teaching; production IMM models typically use 5,000-20,000 paths per netting set per business date, with the path count chosen to drive the Monte Carlo standard error of the EPE / PFE estimates below a regulatory-acceptable tolerance (typically 1-2% of the headline figure). For a bank with 10,000 active netting sets and 10,000 paths each at a daily refresh, the simulation produces 100 million path-level MTM observations per day. The data engineer does not store the path-level data (it is regenerated on each run); the warehouse stores the *aggregated* quantile and mean outputs (`fact_pfe_profile` at the netting-set × time-bucket grain) which are orders of magnitude smaller. The dimensioning of the simulation grid is itself an engineering decision: too few paths produces noisy EAD that fails the daily DQ tests; too many paths produces a compute bill that the firm's risk-tech budget will not absorb.

## 5. Common pitfalls

!!! warning "Watch out"
    1. **Applying a single CCF to all revolvers.** CCF varies materially by segment — corporate vs. retail can differ by 20+ percentage points, rated vs. unrated corporate by 10+, investment-grade vs. sub-investment-grade by 10+. A firm-wide CCF for the revolver book is a politically convenient simplification that systematically misstates the EAD for every segment it covers. The calibration team should produce a CCF per segment and the warehouse should carry the segment-specific figure on `fact_ead_calculation` with `applied_ccf` materialised so the consumer sees which CCF was applied to which facility.
    2. **Confusing current exposure with EAD for derivatives.** A trader's pre-trade screen typically quotes the current MTM ("the swap is +$2M to us today"); the credit-risk team's EAD figure for the same swap might be +$2M (current) + $5M (PFE) = +$7M. Reporting the +$2M as the EAD misses the PFE component, which is often the larger of the two for long-dated derivatives. The data dictionary must distinguish `current_exposure_usd` from `ead_usd` on the fact table, and the consumer must read the right one for the use case.
    3. **Double-counting netted exposures.** A naive sum of positive trade-level MTMs across a counterparty ignores the netting agreement that allows positive and negative MTMs to offset within the netting set. For a counterparty with 200 trades split roughly 50/50 between positive and negative MTM, the gross-of-netting figure can be 5-10× the net figure. EAD must be computed at the netting-set grain (see §3.7); a query that sums `current_exposure_usd` across trades without a `netting_set_id` group-by produces a gross-of-netting figure that is wrong for credit reporting.
    4. **Ignoring wrong-way risk on highly-correlated derivatives.** A CDS sold by an affiliate of the reference entity, an FX forward with an emerging-market sovereign whose currency is correlated with the trade's payoff direction, an equity option on the counterparty's own stock — all are textbook WWR cases that increase the effective EAD substantially. A warehouse that does not flag WWR exposures (`wwr_classification`) leaves the regulatory capital under-stated and the credit-committee surveillance blind to a class of risk that has produced multiple historical losses (the GFC's monoline insurer collapses are the canonical case).
    5. **Using stale collateral haircuts.** Supervisory haircuts on collateral are periodically updated by the regulator (e.g. when sovereign-debt credit ratings change, when market volatility breaches a defined threshold); internal haircuts may be re-calibrated more frequently. A warehouse that hard-codes the haircut at trade-capture time and never refreshes it produces an EAD that drifts away from the methodology's actual value. The haircut should be looked up from a bitemporal `dim_haircut` reference each business date and applied freshly; the change history is then auditable.
    6. **Missing the off-balance-sheet contingent obligations.** A bank's EAD report that covers loans, drawn revolvers, and held bonds but omits issued letters of credit, undrawn revolver capacity, guarantees, and committed-but-undrawn lines understates the firm's true credit exposure by 30-60% for a typical commercial-bank book. The contingent obligations *are* EAD (with their respective CCFs applied) and must land on `fact_ead_calculation` alongside the on-balance-sheet items. The data engineer's reconciliation: the sum of `ead_usd` for a counterparty should reconcile to the credit-officer's view of "total exposure to this counterparty" within a tolerance, and a gap typically signals a missing off-balance-sheet feed.
    7. **Treating SA-CCR add-ons as constants when they depend on remaining maturity.** The SA-CCR add-on factors are not single numbers per asset class — they depend on the trade's residual maturity (the "maturity factor"), on whether the trade is margined, on the margin period of risk, and on a handful of other trade-specific attributes. A loader that applies a single add-on factor per asset class produces an EAD that drifts from the correct figure as the trade ages. The full SA-CCR formula reference (BCBS 279) belongs in the model team's documentation; the data engineer's job is to ensure all the inputs the formula needs are landed on the trade record and refreshed daily.

## 6. Exercises

1. **CCF calculation.** A $50M corporate revolver is currently drawn $15M (so undrawn = $35M). The applicable CCF is 60%. Compute the EAD. Then compute the EAD if the facility is fully drawn ($50M) and if it is fully undrawn ($0M). What is the policy implication of the three figures?

    ??? note "Solution"
        Applying `EAD = drawn + CCF × undrawn`:

        - **Currently drawn $15M, undrawn $35M.** EAD = 15 + 0.60 × 35 = $36M.
        - **Fully drawn $50M, undrawn $0M.** EAD = 50 + 0.60 × 0 = $50M.
        - **Fully undrawn $0M, undrawn $50M.** EAD = 0 + 0.60 × 50 = $30M.

        Three observations on the figures.

        First, the *current* EAD ($36M) sits between the fully-drawn ($50M) and fully-undrawn ($30M) endpoints, weighted by the current drawn balance. This is the expected behaviour: a partially-drawn facility's EAD is a linear combination of the two endpoints, with the CCF determining the weighting of the undrawn component.

        Second, the policy implication is significant for capital planning. A facility that today shows $15M drawn is contributing $36M of EAD to the firm's credit exposure — more than twice the *visible* current usage. A risk officer who reads the loan-system report ("this counterparty has $15M outstanding") and treats that as the EAD is understating the credit exposure by $21M, or 58%. The undrawn commitment is *committed capital* in the regulatory sense and must be sized accordingly. The same logic applies firmwide: a firm with $1B of drawn revolver balances and $4B of undrawn commitments at a 60% CCF has a revolver EAD of $1B + 0.60 × $4B = $3.4B, more than three times the drawn-only figure. Capital, IFRS 9 provisions, and credit-committee limits should all reflect the $3.4B figure, not the $1B.

        Third, the fully-undrawn case ($30M EAD on a $50M commitment) is the most counterintuitive. A facility that has *never been drawn* is still creating $30M of credit exposure — the firm has committed to disburse the cash on demand and the calibration says 60% of the time, in default cases, the counterparty will have drawn the full $50M before defaulting. A relationship manager who sees an unused $50M commitment and thinks "no exposure" has misread the contract; the *commitment itself* is the risk.

2. **PFE reasoning.** A 5-year interest-rate swap has a current MTM of +$2M (in the bank's favour). The PFE 95th percentile over the remaining life is $8M. The counterparty defaults today. What is the bank's loss exposure? What about if the counterparty defaults 3 years from now?

    ??? note "Solution"
        **Today's default.** The bank's loss exposure is the current MTM crystallised at default: $2M. The PFE figure ($8M) is the *future* exposure — the modelled estimate of what the exposure *could grow to* between now and a future default — and is *not* the loss figure for a default that happens today. The bank's claim in the counterparty's bankruptcy is the $2M positive MTM (subject to whatever LGD the recovery process eventually realises on the $2M; if the LGD is 60% the realised loss is $2M × 0.60 = $1.2M).

        **Default 3 years from now.** The bank's loss exposure is the *realised* MTM at that future date, which is a random variable. The PFE 95th percentile of $8M represents the worst-case realisation in a 95% confidence band — five times out of a hundred the exposure at the default date would exceed $8M; ninety-five times out of a hundred it would be $8M or below. The *expected* exposure at that future date (the EPE) is materially lower than the 95th-percentile figure — typically 20-30% of the PFE peak — so the *expected* loss is something like (0.25 × $8M) × LGD = $2M × LGD, not $8M × LGD.

        The conceptual distinction the question is probing: PFE is an input to the EAD figure that the *regulatory capital* formula consumes (capital must be sized to a stressed scenario, hence the use of a tail quantile); but PFE is not the *expected* loss for a specific default event at a specific time. The EPE figure or the realised MTM is what feeds the expected-loss calculation. A consumer who treats the PFE 95th percentile as the expected exposure has over-estimated the EAD by a factor of 3-5× for vanilla derivatives.

        A subtlety: the PFE profile is a *curve*, not a single number. The $8M figure quoted in the question is the *peak* of the curve over the swap's remaining life; the PFE *at* the 3-year mark may be lower (e.g. $7M) if the peak sits before or after year 3, and the exposure at the *actual* default date should be read from the profile at that specific date, not from the peak. A consumer who uses the peak everywhere over-states the exposure at every point that is not the peak.

3. **WWR design.** Your warehouse currently flags wrong-way risk with a single boolean column (`is_wwr`). The credit policy team wants to track three severity levels (LOW / MEDIUM / HIGH). Sketch the dimensional and fact-table changes needed and discuss the historical-data implications.

    ??? note "Solution"
        The minimum required changes:

        - **Replace `is_wwr` boolean with two columns on `fact_ead_calculation`.** A `wwr_classification` enum (`NONE` / `GENERAL` / `SPECIFIC`) and a `wwr_severity` enum (`LOW` / `MEDIUM` / `HIGH`, NULL when `wwr_classification = 'NONE'`). The two-column design separates the *kind* of WWR (general macro correlation vs. structural specific correlation) from the *intensity* (whether the correlation is weak, moderate, or strong). Both are needed because they answer different questions: regulatory capital differentiates GENERAL from SPECIFIC; credit-committee escalation thresholds differentiate LOW / MEDIUM / HIGH.
        - **Add a `dim_wwr_classification` reference dimension.** Keyed by `(wwr_classification, wwr_severity)`, carrying the methodology rationale, the regulatory treatment (capital add-on factor, escalation pathway), the credit-policy thresholds that classify a trade into each cell, and the as-of validity window for the methodology version. The classification logic itself (the rules that map a trade's attributes to a severity level) belongs in the dimension table, not hard-coded into the loader.
        - **Add `fact_wwr_classification_history`.** A bitemporal fact at `(facility_id_or_trade_id, business_date, as_of_timestamp)` grain carrying the classification and severity as of each business date, with the rationale and the classifier (the credit officer or the algorithm that produced the classification). This is the historical record of how the classification has evolved; it joins onto `fact_ead_calculation` for current-state queries and is queried directly for trend reporting ("how many SPECIFIC-HIGH classifications did we have over time?").

        Historical-data implications:

        - **Backfill is non-trivial.** The existing `is_wwr` boolean carries only two states; there is no signal in the historical record to populate the three severity levels. The credit policy team would need to define a default mapping (e.g. all historical `is_wwr = TRUE` rows become `GENERAL-MEDIUM` by default, with manual escalation to `HIGH` or `SPECIFIC` for the cases the team can identify in retrospect), or accept that the pre-migration history is summarised at the coarser granularity. The data engineer should document the cut-over date explicitly and provide a view that translates the old boolean to the new schema for historical queries.
        - **Regulatory reporting impact.** If the regulatory submission templates reference `is_wwr` directly, those submissions need to be re-pointed at `wwr_classification` (with a derivation such as `wwr_classification != 'NONE'` providing the boolean for backward compatibility). The dual-running period (where both the old and new shapes are populated) typically runs for one or two quarterly cycles to give the regulatory-reporting team time to re-test.
        - **Model-validation impact.** Any internal model that consumed `is_wwr` as a feature needs to be re-validated against the new schema. A model trained on a boolean cannot directly consume a three-level severity without re-training; the cleanest pattern is to keep the boolean as a derived view (`is_wwr = (wwr_classification != 'NONE')`) for legacy consumers while new model versions consume the richer column. The data engineer should provide both views and version the schema change explicitly so the model team can sequence its re-training.

        The deeper question the exercise probes: a schema change that adds analytical depth (more categorical levels) almost always comes with a historical-data debt (the new dimensions did not exist when the historical data was captured). The right pattern is to be honest about the cut-over date, to keep the old shape queryable via a view, and to accept that some pre-migration analyses cannot be re-run on the richer schema. Pretending the historical data can be costlessly upgraded to the new granularity is the single most common WWR-schema-migration mistake.

4. **CCF segmentation reasoning.** Your firm calibrates a single CCF of 60% for its entire revolver book. A new analysis splits the book by obligor type (corporate vs. retail) and finds calibrated CCFs of 55% (corporate) and 80% (retail). What is the EAD impact of moving from the single CCF to the segmented CCFs, and what is the data-engineering work required?

    ??? note "Solution"
        The EAD impact depends on the share of undrawn commitment in each segment. Suppose the firm's revolver book has $5B of undrawn commitment split as $4B corporate / $1B retail (a roughly typical mix for a US commercial bank).

        - **Single CCF (60%).** Undrawn contribution to EAD = 0.60 × $5B = $3B.
        - **Segmented CCFs (55% corporate, 80% retail).** Undrawn contribution = 0.55 × $4B + 0.80 × $1B = $2.2B + $0.8B = $3.0B.

        The headline figures are nearly identical (both $3B) — which is *exactly the point* the single-CCF defenders typically make. The aggregate EAD is unchanged; the segmentation merely reshuffles where the EAD is recognised. But the segmentation matters for three other reasons that are not visible in the firmwide aggregate.

        First, the *capital* impact is non-trivial. Retail revolvers typically carry higher risk weights than corporate revolvers under the IRB capital formula; an EAD that is correctly classified to retail attracts more capital per dollar of EAD than the same dollar of corporate EAD. The single-CCF approach systematically misallocates EAD between the two and therefore mis-sizes the capital for each.

        Second, the *IFRS 9 ECL* impact runs in the opposite direction. Retail facilities typically have higher PDs than corporate facilities of the same nominal commitment; a CCF that under-states retail EAD ($0.60 × $1B = $0.6B instead of the correct $0.80 × $1B = $0.8B) flows through to an IFRS 9 ECL that under-states retail loss provisions. The firm's stage-2 transition triggers and stage-3 provisions are both calibrated against expected losses; an EAD that is wrong by segment produces ECL that is wrong by segment, even if the firmwide totals reconcile.

        Third, the *managerial* impact is that the segmented CCFs let the firm see *where* its revolver risk concentrates. A firm with a 30% retail share by undrawn commitment and an 80% retail CCF has *more than half* its undrawn-EAD coming from a segment it might not have realised was so material. Limit-setting, capital allocation, and product-pricing decisions should all be informed by the segmented view; the single-CCF view obscures the distribution.

        The data-engineering work to support the segmentation:

        - **`dim_facility.facility_segment_id`** column populated from the joint key (product type × obligor type × rating bucket × jurisdiction), with the segment-derivation logic in a stable place (typically a `dim_segmentation` reference dimension that the model team owns).
        - **`dim_ccf_calibration`** table keyed by `(segment_id, calibration_version, valid_from, valid_to)` carrying the calibrated CCF and the calibration metadata (sample size, calibration window, downturn-vs-cycle-average basis).
        - **Loader logic** that joins facilities to segments to CCFs at write-time, populates `applied_ccf` and `applied_ccf_basis` on each `fact_ead_calculation` row, and rejects any facility whose segment cannot be derived (the loader's data-quality check that catches segmentation gaps).
        - **Reconciliation report** that compares the segmented-EAD aggregate to the previously-published single-CCF aggregate and explains the difference at the segment level. A 0.1% firmwide difference (the typical noise floor between two methodology versions) is fine; a 5% difference signals an unintended methodology change that needs investigation before publication.

5. **Reconciliation reasoning.** Your warehouse reports a SA-CCR EAD of $1.2B for a portfolio of OTC derivatives. The regulatory-reporting submission for the same date reports $1.05B for the same portfolio. The model team's IMM EAD is $850M. Walk through the reconciliation questions you would ask.

    ??? note "Solution"
        Three numbers, three reconciliation questions, and a process for narrowing the gaps.

        **The $150M gap between warehouse SA-CCR and regulatory submission SA-CCR.** Both figures are supposed to be the same methodology applied to the same portfolio; the gap should be at most a small reconciling-items list. Questions to ask:

        - **Scope.** Does the regulatory submission cover exactly the same trades the warehouse SA-CCR figure covers? A common gap is excluded trades — for example, intra-group trades that are eliminated for consolidated reporting but included in the warehouse, or non-EU trades excluded from an EU regulatory template but in the warehouse. The reconciling-items list usually exposes a handful of trade-category differences.
        - **As-of timing.** The regulatory submission is typically run from a frozen end-of-period snapshot; the warehouse figure is the latest bitemporal version, which may include corrections that landed after the submission cut-off. The reconciliation should be performed against the *as-of-submission-cut-off* warehouse snapshot, not against the latest version.
        - **Methodology version.** The SA-CCR formula has parameters that are occasionally updated (supervisory haircuts, asset-class factor changes); a methodology mismatch between warehouse and submission produces a systematic gap. The `model_version` column on `fact_ead_calculation` should match the version the submission was prepared under.
        - **Aggregation level.** The submission aggregates EAD at the obligor or netting-set level; the warehouse may carry per-trade rows that need to be aggregated before comparison. A naive sum of per-trade EADs over-states the netted figure (the netting recognition happens at the netting-set grain, not the trade grain).

        **The $200M gap between warehouse SA-CCR and IMM.** This is the more interesting gap because the two figures are *different* methodologies applied to the same portfolio. The IMM figure (the internal model) should generally produce a lower EAD than the SA-CCR figure (the regulatory standardised formula) for portfolios where the bank's model captures correlation and netting effects that SA-CCR's prescribed factors approximate. A 17% gap (SA-CCR / IMM ≈ 1.41) is *roughly the alpha multiplier* baked into SA-CCR — the regulator's deliberate conservatism that ensures SA-CCR is at least the historical-IMM equivalent. So this gap is expected and approximately right. Questions to ask:

        - **Is the IMM figure regulatory-approved for this portfolio?** If not, the SA-CCR figure is the binding regulatory number and the IMM figure is informational only. If yes, the bank reports IMM × max(IMM-floor) for capital, where the floor is typically a percentage of the SA-CCR figure (the "Basel I floor" or the "output floor" depending on jurisdiction).
        - **Is the IMM model backtest within tolerance?** The regulator requires that the IMM model's predicted exposures backtest well against realised exposures; persistent under-prediction by IMM relative to realised would invalidate the IMM EAD and force a fall-back to SA-CCR.

        **The cross-check.** The warehouse should expose all three figures on `fact_ead_calculation` (with `ead_type` distinguishing SA-CCR vs. IMM vs. an INTERNAL view if the bank maintains one), let the reconciliation pipeline join them on `(netting_set_id, business_date)`, and surface the reconciling items via a daily DQ report. The data engineer's role: keep the join clean, surface the gaps, and let the model team and the regulatory-reporting team work the differences. A gap-free reconciliation is rare; a gap that *grows over time* without explanation is the signal that something has drifted in one of the three pipelines.

## 7. Further reading

- Basel Committee on Banking Supervision, *The standardised approach for measuring counterparty credit risk exposures* (BCBS 279), March 2014 (with subsequent amendments) — the canonical SA-CCR final standard. Dense, formula-heavy, and the authoritative reference for any SA-CCR implementation question.
- Gregory, J., *The xVA Challenge: Counterparty Credit Risk, Funding, Collateral, and Capital*, 4th edition, Wiley, 2020 — the practitioner reference for derivatives EAD methodology, with thorough treatment of SA-CCR, IMM, netting, collateral, and the broader xVA framework. The chapters on PFE modelling and on wrong-way risk are especially clear.
- Pykhtin, M. & Zhu, S., *A Guide to Modelling Counterparty Credit Risk*, GARP Risk Review (July/August 2007) — the foundational practitioner article on counterparty-credit-risk modelling. Pre-dates SA-CCR but the conceptual framework (EPE, PFE, netting, collateral, margin period of risk) remains the canonical exposition.
- Brigo, D., Morini, M. & Pallavicini, A., *Counterparty Credit Risk, Collateral and Funding: With Pricing Cases for All Asset Classes*, Wiley, 2013 — the mathematical-finance reference for counterparty credit modelling. Heavier on the maths than Gregory but essential for any model team building an IMM implementation from scratch.
- International Swaps and Derivatives Association (ISDA) documentation on SA-CCR implementation — published whitepapers and working-group notes covering practical SA-CCR questions (asset-class classification edge cases, netting-set definition, collateral treatment under variation-margin vs. initial-margin regimes). The ISDA SIMM documentation is the parallel reference for the initial-margin computation under uncleared-margin regulations.
- Basel Committee on Banking Supervision, *Sound practices for backtesting counterparty credit risk models* (BCBS 185), April 2010 — the regulatory expectations for IMM backtesting. The data engineer who builds an IMM backtest pipeline needs to know what the regulator expects to see in the validation pack.
- Engelmann, B. & Rauhmeier, R. (eds.), *The Basel II Risk Parameters: Estimation, Validation, Stress Testing*, 2nd edition, Springer, 2011 — the chapters on EAD and CCF estimation complement the PD and LGD chapters used in the prior modules; the treatment of CCF calibration for revolving facilities is one of the most practitioner-friendly available.

## 8. Recap

You should now be able to:

- Define Exposure at Default across funded and unfunded exposures, distinguish the trivial cases (term loan = outstanding) from the model-output cases (revolver = drawn + CCF × undrawn; derivative = current + PFE), and articulate why the "at default" qualifier produces a figure that typically exceeds today's drawn balance for revolving facilities.
- Apply the CCF formula to compute EAD for a revolver portfolio, recognise the segmentation requirements (corporate vs. retail, rated vs. unrated, PIT vs. TTC vs. downturn), and design the `fact_facility_drawn_undrawn` snapshot pipeline that feeds the calibration team.
- Distinguish current exposure from Potential Future Exposure for derivatives, articulate the shape of the PFE profile across a swap's life (rises with diffusion, peaks around quarter-to-mid life, falls to zero at maturity), and recognise that PFE is a profile rather than a single number.
- Identify wrong-way risk and its two flavours (general macro-correlation vs. specific structural-correlation), recognise the trade categories that typically attract WWR flags, and design the dimensional shape (`wwr_classification`, `wwr_severity`, bitemporal classification history) that supports the credit-policy team's escalation framework.
- Design `fact_ead_calculation` at a grain that supports BOOK / SA-CCR / IMM / INTERNAL EAD types on a single grain, with `ead_aggregation_level` distinguishing trade / facility / netting-set rows, and the methodology metadata (`applied_ccf`, `model_version`, `discount_rate_used`) that makes any historical EAD figure reproducible.
- Connect this module forward to [Expected Loss](#) (the PD × LGD × EAD product) and to the Phase 4 [Collateral & Netting](#) module that treats the collateral mechanics this module only introduces, and backward to [Credit Instruments](04-credit-instruments.md) (which classifies the funded vs. unfunded distinction this module operationalises) and to [Probability of Default](07-probability-of-default.md) and [Loss Given Default](08-loss-given-default.md) (the parallel measures whose data shapes informed this one).
- Trace the operational lineage of an EAD figure from the loan-accounting system (drawn balance), from the derivative position store (current MTM), from the collateral system (haircut-adjusted collateral value), and from the model team's CCF / SA-CCR / IMM engines (the methodology outputs) into a single row on `fact_ead_calculation` with the methodology version, the aggregation level, and the bitemporal as-of timestamp that make the figure reproducible and auditable.
- Recognise the operational discipline EAD requires that PD and LGD do not — a daily refresh cadence, intraday-monitoring SLAs for the highest-priority counterparties, a reconciliation against the source-of-truth loan-accounting system every business day, and a bitemporal restatement pattern that handles the routine methodology updates and the occasional regulator-driven historical correction without rewriting the past.
