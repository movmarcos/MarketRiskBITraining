# Glossary

A reference of terms used throughout the training, with cross-links to the
module where each concept is treated in depth.

## A

**Accumulating snapshot** — a fact-table style where one row tracks an entity
(a trade, a settlement, a workflow item) through a known sequence of
milestones, with the milestone columns updated in place as the entity
progresses. Contrast with transaction and periodic-snapshot facts (see
[Module 07](modules/07-fact-tables.md)).

**ACS** — Annual Cyclical Scenario. The Bank of England / PRA macro stress-test
regime for major UK banks; the UK analogue of CCAR (see
[Module 19](modules/19-regulatory-context.md)).

**Actual P&L** — the realised P&L of the desk including intraday trading,
fees, and new business. Distinct from hypothetical P&L; using actual P&L for
backtesting silently inflates exception counts (see
[Module 14](modules/14-pnl-attribution.md)).

**Additive measure** — a measure that can be summed across any dimension
without restating it. Examples: notional, gross exposure, stress P&L.
*See also*: semi-additive, non-additive, sub-additive.

**Aggregation** — the act of rolling a measure up a hierarchy (book → desk →
firm; tenor → curve; trade → portfolio). For risk measures, aggregation is
rarely a simple sum (see [Module 12](modules/12-aggregation-additivity.md)).
*See also*: additive, sub-additive, diversification benefit, semantic layer.

**Allocation ID** — when a block trade is split across multiple sub-accounts,
the parent ID and the N child IDs that link the allocations. Modelled as a
one-to-many cross-reference (see [Module 03](modules/03-trade-lifecycle.md)).

**AMENDED** — a trade-status value indicating economics have been modified
post-booking. Most shops treat AMENDED as a self-loop back to NEW with a
`version_number` increment, not a terminal status (see
[Module 03](modules/03-trade-lifecycle.md)).

**As-of date** — the business date a risk view represents. Distinct from
the system / transaction time when the data was inserted (see
[Module 13](modules/13-time-bitemporality.md)).

**As-of join** — a temporal join that picks the dimension row whose
`valid_from`/`valid_to` interval contains the fact's business date. The
correct way to join SCD2 dimensions; joining on `is_current = TRUE`
back-applies today's attributes to history and is a common bug (see
[Module 05](modules/05-dimensional-modeling.md)).

**Audit trail** — the queryable record of who produced what number, from
which inputs, with which code version, and when. Built from bitemporal
stamps and lineage (see [Module 16](modules/16-lineage-auditability.md)).

## B

**Backtesting** — comparing predicted VaR to realised P&L outcomes over a
window (typically 250 days) to validate the model. Regulatory requirement
under Basel 2.5 and FRTB IMA (see
[Module 09](modules/09-value-at-risk.md)).

**Basel** — the framework of global banking regulations from the Basel
Committee on Banking Supervision (BCBS), implemented locally by national
supervisors.

**BCBS 239** — *Principles for Effective Risk Data Aggregation and Risk
Reporting*. Sets supervisory expectations on data architecture, accuracy,
completeness, timeliness, and adaptability for systemically-important
banks (see [Module 19](modules/19-regulatory-context.md)).

**Bitemporality** — modelling two independent time axes: business time
(when something was true in the world) and system / transaction time (when
the warehouse recorded it). Required for regulatory reproducibility (see
[Module 13](modules/13-time-bitemporality.md)).
*See also*: as-of date, valid time, transaction time, SCD2.

**Block trade** — a single large order subsequently allocated across many
sub-accounts; produces a parent and child trade IDs (see
[Module 03](modules/03-trade-lifecycle.md)).

**Book** — a logical container of trades and positions, used for management,
risk, and P&L purposes. The conformed `dim_book` is the universal organisational
spine (see [Module 06](modules/06-core-dimensions.md)).

**Bronze layer** — the source-system-faithful raw landing zone in a
medallion architecture; carries bitemporal stamps and no business logic
(see [Module 18](modules/18-architecture-patterns.md)).

**Bucketed sensitivity** — a vector of sensitivities along a tenor or
strike axis (e.g. DV01 per curve point). Required for FRTB SA (see
[Module 08](modules/08-sensitivities.md)).

**Bus matrix** — Kimball's grid of facts × conformed dimensions, used to
declare which dimensions any given fact must join to with shared semantics
(see [Module 05](modules/05-dimensional-modeling.md)).

**Business date** — the trading date a row pertains to (the date of the
position, the date the P&L was earned). Distinct from the system date the
row was loaded (see [Module 13](modules/13-time-bitemporality.md)).

## C

**CCAR** — Comprehensive Capital Analysis and Review. The US Federal
Reserve's annual quantitative stress-test programme for large bank holding
companies, with a 9-quarter projection horizon (see
[Module 19](modules/19-regulatory-context.md)).

**CCP** — Central Counterparty. A clearing entity (LCH, CME, ICE) that
interposes itself between counterparties; once a trade clears, the CCP ID
becomes the legal identifier (see [Module 03](modules/03-trade-lifecycle.md)).

**Christoffersen test** — a backtesting test that extends Kupiec by also
testing the independence of exceptions over time, catching clustering of
breaches (see [Module 09](modules/09-value-at-risk.md)).

**Coherent risk measure** — a risk measure that satisfies monotonicity,
sub-additivity, positive homogeneity, and translation invariance. Expected
Shortfall is coherent; VaR is not (see
[Module 12](modules/12-aggregation-additivity.md)).

**Column-level lineage** — lineage tracked at the granularity of individual
columns (this column derives from those columns), not just table-to-table.
Required for serious BCBS 239 attestations (see
[Module 16](modules/16-lineage-auditability.md)).

**Completeness** — DQ dimension: every required field, row, and partition is
present. The cheapest class to detect, the most consequential when missed
(see [Module 15](modules/15-data-quality.md)).

**Component VaR** — the contribution of a position (or sub-portfolio) to
total VaR. The components are summable to the total, unlike VaR itself (see
[Module 12](modules/12-aggregation-additivity.md)).

**Conformed dimension** — a dimension shared with the same surrogate key and
the same attribute semantics across multiple fact tables. Conformance is
what makes cross-fact slicing meaningful (see
[Module 05](modules/05-dimensional-modeling.md)).

**Consistency** — DQ dimension: the same fact appears the same way across
systems and across time, with no contradictions (see
[Module 15](modules/15-data-quality.md)).

**CRO** — Chief Risk Officer. Head of the firm-wide risk function.

**CS01** — sensitivity of a position's value to a 1bp change in credit
spread (see [Module 08](modules/08-sensitivities.md)).

**CSA** — Credit Support Annex. The ISDA document that defines collateral
terms between bilateral counterparties.

**CSR** — Credit Spread Risk. An FRTB SA risk class, split into
non-securitisation (CSR-NS), securitisation (CSR-S), and the correlation
trading portfolio (CTP) (see
[Module 19](modules/19-regulatory-context.md)).

**Curvature** — under FRTB SA, a higher-order risk measure that captures
the convexity of the price function with respect to a market factor;
computed as the difference between a full revaluation under a large shock
and the linear (delta) approximation (see
[Module 19](modules/19-regulatory-context.md)).

**CVA** — Credit Valuation Adjustment. The market value of counterparty
default risk on derivatives, charged as an XVA component.
*See also*: XVA, DVA, FVA, MVA, KVA.

## D

**Degenerate dimension** — a dimension attribute (typically an identifier
like a trade ID) stored directly on the fact row rather than in a separate
dimension table (see [Module 05](modules/05-dimensional-modeling.md)).

**Delta (Δ)** — sensitivity of an option's value to changes in the
underlying price. Also used informally as the differential operator; the
market-risk meaning is the option Greek (see
[Module 08](modules/08-sensitivities.md)).

**DFAST** — Dodd-Frank Act Stress Test. The Federal Reserve's parallel
stress-test programme alongside CCAR (see
[Module 19](modules/19-regulatory-context.md)).

**Diversification benefit** — the extent to which the risk of a portfolio
is less than the sum of the risks of its components, due to imperfect
correlation. The reason VaR is sub-additive in practice (see
[Module 12](modules/12-aggregation-additivity.md)).

**DRC** — Default Risk Charge. Under FRTB, the capital charge for issuer
default risk on positions exposed to single-name credit. Computed
separately from sensitivities-based capital under both SA and IMA (see
[Module 19](modules/19-regulatory-context.md)).

**DV01** — Dollar Value of a 01 (basis point). Sensitivity of a fixed-income
position to a 1bp change in yield. Also called PV01 (see
[Module 08](modules/08-sensitivities.md)).

**DVA** — Debit Valuation Adjustment. The mirror of CVA: the value of the
firm's own default risk to its counterparties.

**DQ scorecard** — a composite quality indicator combining checks across
the six DQ dimensions to produce a per-feed health score (see
[Module 15](modules/15-data-quality.md)).

## E

**EAD** — Exposure at Default. Counterparty credit risk measure: expected
exposure at the time of a hypothetical default.

**EBA** — European Banking Authority. The EU body that designs the
biennial EU-wide stress test (see
[Module 19](modules/19-regulatory-context.md)).

**ELT** — Extract, Load, Transform. The modern pattern of landing raw
data first and transforming inside the warehouse (see
[Module 18](modules/18-architecture-patterns.md)).

**EOD** — End of Day. The cutoff at which official daily figures are
struck; the dominant cadence for regulatory reporting.

**ES (Expected Shortfall)** — also called CVaR or Conditional VaR. The
average loss in the worst (1−α)% of cases. FRTB IMA's replacement for
VaR; coherent (see [Module 09](modules/09-value-at-risk.md)).

**ETL** — Extract, Transform, Load. The legacy pattern of transforming
data outside the warehouse before loading (see
[Module 18](modules/18-architecture-patterns.md)).

## F

**F2B / Front-to-Back** — the full lifecycle of a trade from origination
through settlement (see [Module 03](modules/03-trade-lifecycle.md)).

**Fact table** — the central table in a star schema, holding measures at a
declared grain with foreign keys to dimensions. Three styles: transaction,
periodic snapshot, accumulating snapshot (see
[Module 07](modules/07-fact-tables.md)).

**FO** — Front Office. The revenue-generating side of the firm; traders
and salespeople.

**FRTB** — Fundamental Review of the Trading Book. The Basel III/IV market
risk capital framework, replacing Basel 2.5 (see
[Module 19](modules/19-regulatory-context.md)).
*See also*: SA, IMA, ES, NMRF, PLA, DRC, RRAO.

**FRTB IMA** — FRTB Internal Models Approach. Bank's-own-model approach
to capital, conditional on supervisory approval, ongoing backtesting, and
PLA tests (see [Module 19](modules/19-regulatory-context.md)).

**FRTB SA** — FRTB Standardised Approach. Bucket-based sensitivities
approach with prescribed risk weights and correlations; mandatory for all
banks (see [Module 19](modules/19-regulatory-context.md)).

**FVA** — Funding Valuation Adjustment. The XVA charge for the cost of
funding uncollateralised derivative exposures.

## G

**Gamma (Γ)** — second derivative of an option's value with respect to the
underlying price; the rate of change of delta (see
[Module 08](modules/08-sensitivities.md)).

**Give-up** — in prime brokerage, an executing broker books a trade and
"gives it up" to the prime broker, who books a mirror; both have FO IDs
linked by the give-up agreement (see
[Module 03](modules/03-trade-lifecycle.md)).

**GIRR** — General Interest Rate Risk. An FRTB SA risk class covering
interest-rate sensitivities by currency and tenor band (see
[Module 19](modules/19-regulatory-context.md)).

**Gold layer** — the business-ready facts and dimensions in a medallion
architecture; what BI tools read (see
[Module 18](modules/18-architecture-patterns.md)).

**Grain** — the level of detail represented by one row in a fact table.
The single most important sentence in any fact-table design; "one row per
(book, business_date, instrument, risk_factor)" (see
[Module 07](modules/07-fact-tables.md)).

**Greeks** — the family of partial derivatives of an option's value:
delta, gamma, vega, theta, rho. Collectively, the price-sensitivity
profile of an option (see [Module 08](modules/08-sensitivities.md)).

## H

**Historical VaR** — VaR computed by replaying past market-factor moves
(typically 250 days) against today's portfolio (see
[Module 09](modules/09-value-at-risk.md)).

**Hypothetical P&L** — the P&L the prior day's portfolio would have made
if held unchanged for one day. The clean comparator for VaR backtesting
(see [Module 14](modules/14-pnl-attribution.md)).

## I

**IMA** — Internal Models Approach. FRTB's option for using internal
models for capital, subject to approval (see
[Module 19](modules/19-regulatory-context.md)).

**IMCC** — Internal Models Capital Charge. The aggregated capital number
under FRTB IMA, combining ES, stressed ES, and NMRF charges (see
[Module 19](modules/19-regulatory-context.md)).

**Incremental VaR** — the change in VaR from adding (or removing) a
specific position. Related to but distinct from marginal VaR (see
[Module 12](modules/12-aggregation-additivity.md)).

**IPV** — Independent Price Verification. Periodic check by a function
independent of the front office that FO marks are reasonable.

**ISDA** — International Swaps and Derivatives Association. Publishes
the master-agreement and lifecycle-event documentation that governs OTC
derivatives.

**ISIN** — International Securities Identification Number. The 12-character
global identifier for a security (see
[Module 06](modules/06-core-dimensions.md)).

## J

**Junk dimension** — a dimension that bundles low-cardinality, mostly
unrelated flag attributes (e.g. trade-type flags, settlement flags) into
one table to avoid proliferating tiny dimensions on the fact (see
[Module 05](modules/05-dimensional-modeling.md)).

## K

**Kappa architecture** — an architecture with a single streaming path;
historical reprocessing is implemented as a slow stream replay. Right for
genuinely streaming-first platforms; wrong for batch regulatory reporting
(see [Module 18](modules/18-architecture-patterns.md)).

**Kimball** — Ralph Kimball, originator of the dimensional-modelling
school: star schemas, conformed dimensions, the bus matrix, SCDs (see
[Module 05](modules/05-dimensional-modeling.md)).

**Kupiec test** — the proportion-of-failures backtesting test (Kupiec,
1995); a likelihood-ratio test of the null hypothesis that the observed
exception rate equals the nominal rate (see
[Module 09](modules/09-value-at-risk.md)).

**KVA** — Capital Valuation Adjustment. The XVA charge for the cost of
holding regulatory capital against derivative exposures.

## L

**Lakehouse** — a storage architecture combining a data lake's open file
formats with a data warehouse's transactional and SQL semantics (see
[Module 18](modules/18-architecture-patterns.md)).

**Lambda architecture** — an architecture with parallel batch and speed
paths reconciled at the serving layer. Largely superseded by medallion
plus narrow streaming side-tiers (see
[Module 18](modules/18-architecture-patterns.md)).

**Late-arriving fact** — a fact row that arrives after the business date
it pertains to. Handled either as a bitemporal restatement on the original
business date or by booking against the arrival date with a flag (see
[Module 07](modules/07-fact-tables.md)).

**LEI** — Legal Entity Identifier. A 20-character global ID for legal
entities, issued under ISO 17442. An *attribute* on `dim_counterparty`,
not its primary key (see [Module 06](modules/06-core-dimensions.md)).

**Lineage** — the traceable record of how data flows from sources through
transformations to consumers. Table-level lineage is the minimum;
column-level lineage is what regulators expect for serious attestations
(see [Module 16](modules/16-lineage-auditability.md)).

## M

**Marginal VaR** — the rate of change of total VaR with respect to a
position's size; the sensitivity of VaR to a small change in holding (see
[Module 12](modules/12-aggregation-additivity.md)).

**MDM** — Master Data Management. The discipline of maintaining
authoritative reference data (counterparties, books, instruments) across
the firm.

**Medallion architecture** — a three-layer pattern (bronze raw / silver
conformed / gold mart) connecting source feeds to BI consumption via
batch transformations. The practical default for risk warehouses (see
[Module 18](modules/18-architecture-patterns.md)).

**Monte Carlo VaR** — VaR computed by simulating market-factor paths from
a parametric distribution and revaluing the portfolio under each path
(see [Module 09](modules/09-value-at-risk.md)).

**MO** — Middle Office. The independent layer between FO and operations;
owns trade validation, confirmation, and risk reporting.

**MVA** — Margin Valuation Adjustment. The XVA charge for the funding
cost of posting initial margin.

## N

**Natural key** — the business identifier of a record (a counterparty's
LEI, a trade's USI). Surrogate keys are preferred as primary keys because
natural keys can change or be reused (see
[Module 05](modules/05-dimensional-modeling.md)).

**NEW** — a trade-status value indicating the live current version of a
trade (see [Module 03](modules/03-trade-lifecycle.md)).

**NMRF** — Non-Modellable Risk Factor. Under FRTB IMA, factors lacking
sufficient observable price evidence; receive punitive stand-alone capital
treatment (see [Module 19](modules/19-regulatory-context.md)).

**Non-additive measure** — a measure that cannot be summed across any
dimension; must be recalculated. Examples: VaR, ES, ratios, percentiles
(see [Module 12](modules/12-aggregation-additivity.md)).

**Notional** — the face amount of a contract used to compute payments;
not the contract's market value. Additive across positions (see
[Module 04](modules/04-financial-instruments.md)).

**Novation** — the legal transfer of a contract from one counterparty to
another, replacing the original contract with a new one. Common at
clearing (FO trade is novated to the CCP) and in bilateral assignments
(see [Module 03](modules/03-trade-lifecycle.md)).

## O

**OpenLineage** — an open standard for emitting lineage events from data
pipelines, designed to be tool-agnostic (see
[Module 16](modules/16-lineage-auditability.md)).

**OTC** — Over the Counter. Bilateral derivatives traded directly between
two parties rather than on an exchange (see
[Module 04](modules/04-financial-instruments.md)).

## P

**Parametric VaR** — VaR computed analytically from an assumed
multivariate-normal (or other parametric) distribution of returns; also
called variance-covariance VaR (see
[Module 09](modules/09-value-at-risk.md)).

**PC** — Product Control. The independent function producing official
daily P&L; reports into Finance, not the front office.

**Periodic snapshot** — a fact-table style with one row per entity per
period (book × business_date), regardless of whether anything changed
(see [Module 07](modules/07-fact-tables.md)).

**PFE** — Potential Future Exposure. Counterparty credit risk measure
giving a percentile of expected exposure over time.

**PLA** — P&L Attribution test. Under FRTB IMA, the daily test comparing
the variance and tail of the risk-model-predicted P&L distribution to the
actual hypothetical P&L. Failure forces the desk back to SA (see
[Module 19](modules/19-regulatory-context.md)).

**P&L** — Profit and Loss. The change in portfolio value over a period;
the central measurement of trading performance.
*See also*: actual P&L, hypothetical P&L, risk-theoretical P&L, clean P&L,
dirty P&L.

**P&L attribution** — the decomposition of daily P&L into components
attributable to specific risk factors or activities (delta-explain,
vega-explain, residual) (see
[Module 14](modules/14-pnl-attribution.md)).

**Position** — net holding in an instrument at a point in time, derived
from accumulated trades. Semi-additive across time (see
[Module 07](modules/07-fact-tables.md)).

**PV01** — Present Value of a 01 (basis point). Synonym for DV01 in many
shops.

## R

**Ragged hierarchy** — a hierarchy with branches of unequal depth (a book
that rolls directly to a legal entity without an intermediate desk).
Handled with an `(unallocated)` placeholder row or a bridge table (see
[Module 06](modules/06-core-dimensions.md)).

**Reconciliation** — the process of comparing two sources of the same
fact and investigating differences. The primary mechanism for catching
accuracy failures (see [Module 15](modules/15-data-quality.md)).

**Reproducibility** — the ability to regenerate any past published number
on demand from the warehouse. Requires bitemporality plus lineage (see
[Module 16](modules/16-lineage-auditability.md)).

**Restatement** — a corrected value for a previously-reported business
date, loaded with a later transaction time. Bitemporal modelling preserves
both the original and corrected values (see
[Module 13](modules/13-time-bitemporality.md)).

**Risk factor** — an underlying market input (a specific tenor on a yield
curve, a stock price, a vol-surface point) to which positions have
sensitivity (see [Module 08](modules/08-sensitivities.md)).

**Risk-theoretical P&L** — the P&L predicted by the risk model itself for
the realised market-factor moves. Used in the FRTB PLA test against
hypothetical P&L (see [Module 14](modules/14-pnl-attribution.md)).

**Rho (ρ)** — sensitivity of an option's value to interest rates (see
[Module 08](modules/08-sensitivities.md)).

**Role-playing dimension** — a single dimension joined multiple times to
the same fact under different aliases (e.g. `dim_date` joined as
`trade_date`, `settlement_date`, `business_date`) (see
[Module 05](modules/05-dimensional-modeling.md)).

**RRAO** — Residual Risk Add-On. Under FRTB SA, a fixed-percentage charge
on the notional of positions whose risks the sensitivities framework
cannot capture (gap risk on barriers, correlation risk on bespoke
baskets) (see [Module 19](modules/19-regulatory-context.md)).

**RWA** — Risk-Weighted Assets. The denominator of capital ratios;
exposures multiplied by regulator-prescribed risk weights.

## S

**SA** — Standardised Approach. FRTB's prescribed-formula methodology
for capital, used by all firms and as a backstop to IMA (see
[Module 19](modules/19-regulatory-context.md)).

**SCD** — Slowly Changing Dimension. Strategies for handling dimension
attribute changes over time; Type 1 (overwrite), Type 2 (new row with
validity interval), Type 3 (previous-value column), Type 6 (combination)
(see [Module 05](modules/05-dimensional-modeling.md)).

**SCD Type 2** — the dominant pattern for risk reference data: every
attribute change inserts a new row with `valid_from`, `valid_to`, and
`is_current`, preserving full history (see
[Module 05](modules/05-dimensional-modeling.md)).

**Semantic layer** — a metadata layer between BI tools and the warehouse
that codifies measure definitions, hierarchies, and aggregation rules,
preventing the user from summing non-additive measures (see
[Module 12](modules/12-aggregation-additivity.md)).

**Semi-additive measure** — a measure summable across some dimensions but
not others. Positions: summable across books on a given date, not across
dates (see [Module 07](modules/07-fact-tables.md)).

**Sensitivity** — partial derivative of a position's value with respect
to a market factor. The Greeks plus DV01, CS01, etc. (see
[Module 08](modules/08-sensitivities.md)).
*See also*: bucketed sensitivity, curvature, Greeks.

**SETTLED** — a trade-status value indicating cash has moved and the
trade is operationally complete. A SETTLED trade cannot be CANCELLED;
errors are corrected by booking a reversing trade (see
[Module 03](modules/03-trade-lifecycle.md)).

**Silver layer** — the cleansed and conformed layer in a medallion
architecture; cross-source reconciliation lives here (see
[Module 18](modules/18-architecture-patterns.md)).

**Snowflake schema** — a dimensional pattern in which a dimension is
normalised across multiple linked tables. Contrast with the denormalised
star (see [Module 05](modules/05-dimensional-modeling.md)).

**Star schema** — the dominant dimensional pattern: a central fact
surrounded by denormalised dimension tables, each joined directly (see
[Module 05](modules/05-dimensional-modeling.md)).

**STP** — Straight-Through Processing. Fully automated trade flow from
booking to settlement with no manual intervention.

**Stress P&L** — the P&L of a portfolio under a specific defined market
scenario (see [Module 10](modules/10-stress-testing.md)).

**Stressed VaR (sVaR)** — VaR computed using a calibrated stressed
historical period (typically the 2008 crisis); a Basel 2.5 measure
retained as part of the FRTB IMA capital formula (see
[Module 09](modules/09-value-at-risk.md)).

**Sub-additive** — a property of a risk measure where the risk of the
combined portfolio is no greater than the sum of the components' risks.
Required for coherence; ES is sub-additive, VaR is not always (see
[Module 12](modules/12-aggregation-additivity.md)).

**Surrogate key** — a synthetic primary key (typically an integer or hash)
assigned by the warehouse, independent of any business identifier.
Non-negotiable for SCD2 dimensions because the natural key is no longer
unique once history is preserved (see
[Module 05](modules/05-dimensional-modeling.md)).

## T

**Table-level lineage** — lineage tracked at the granularity of tables
(this table reads from those tables); the minimum useful lineage. Less
precise than column-level (see
[Module 16](modules/16-lineage-auditability.md)).

**TERMINATED** — a trade-status value indicating the trade ended before
its scheduled maturity (early termination, exercise, novation-out,
default) (see [Module 03](modules/03-trade-lifecycle.md)).

**Theta (Θ)** — time decay; the sensitivity of an option's value to the
passage of time (see [Module 08](modules/08-sensitivities.md)).

**Timeliness** — DQ dimension: the data arrives within the SLA window.
Often resolves on its own; dangerous because partial-feed batches can ship
silently (see [Module 15](modules/15-data-quality.md)).

**Torn trade** — a trade present in one system but missing in another
(typically present in FO capture but absent in BO settlement); detected by
a left-anti-join in the lifecycle reconciliation (see
[Module 03](modules/03-trade-lifecycle.md)).

**Trade** — a single executed transaction.

**Traffic-light test** — the Basel 2.5 backtesting categorisation: 0–4
exceptions in 250 days = green (no add-on), 5–9 = yellow (graded add-on),
10+ = red (regulatory action) (see
[Module 09](modules/09-value-at-risk.md)).

**Transaction time** — synonymous with system time in bitemporal
modelling: the time at which the warehouse recorded the value (see
[Module 13](modules/13-time-bitemporality.md)).

## U

**Uniqueness** — DQ dimension: the primary-key constraint holds; no
duplicates. Catastrophic when violated (a duplicated trade doubles the
desk's notional) (see [Module 15](modules/15-data-quality.md)).

**USI** — Unique Swap Identifier. The Dodd-Frank Title VII US-issued
identifier for swaps reported to a Swap Data Repository (see
[Module 03](modules/03-trade-lifecycle.md)).

**UTI** — Unique Trade Identifier. The global ISO/CPMI-IOSCO standard
identifier mandatory under EMIR REFIT and equivalent regimes; bilaterally
agreed via a generation waterfall (see
[Module 03](modules/03-trade-lifecycle.md)).

## V

**Valid time** — synonymous with business time in bitemporal modelling:
the time at which a value was true in the world (see
[Module 13](modules/13-time-bitemporality.md)).

**VaR (Value at Risk)** — the loss threshold not expected to be exceeded
with X% confidence over Y days. The dominant market-risk measure under
Basel 2.5; replaced by ES under FRTB IMA but still widely reported (see
[Module 09](modules/09-value-at-risk.md)).
*See also*: ES, stressed VaR, historical VaR, Monte Carlo VaR, parametric
VaR, component VaR, marginal VaR, incremental VaR, backtesting.

**Vega (ν)** — sensitivity of an option's value to implied volatility
(see [Module 08](modules/08-sensitivities.md)).

**Validity** — DQ dimension: values conform to the allowed types,
formats, ranges, and reference-data domains. The cheapest class of check
to implement (see [Module 15](modules/15-data-quality.md)).

## X

**XVA** — the family of valuation adjustments applied to derivative
prices for counterparty credit, funding, capital, and collateral effects.
Components include CVA (credit), DVA (debit), FVA (funding), MVA (initial
margin), and KVA (capital).

## Y

**Yield curve** — the schedule of interest rates by tenor for a given
currency and credit quality; the foundational risk factor for fixed
income (see [Module 11](modules/11-market-data.md)).

**Yield to maturity (YTM)** — the single discount rate that equates a
bond's discounted cashflows to its market price; the bond's internal rate
of return if held to maturity.

## Z

**Zero curve** — the curve of zero-coupon (spot) rates by tenor, derived
by bootstrapping from observed par instruments; the canonical input to
discounting (see [Module 11](modules/11-market-data.md)).

**Zero-coupon bond** — a bond that pays no periodic coupon; the holder's
return is the difference between the discounted purchase price and par
at maturity. The atomic building block of curve construction.

**Z-spread** — the constant spread that, when added to every point on a
zero curve, makes the discounted cashflows of a bond equal its market
price. A standard credit-spread measure used alongside CS01 (see
[Module 08](modules/08-sensitivities.md)).
