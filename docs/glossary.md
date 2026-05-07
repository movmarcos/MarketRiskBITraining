# Glossary

A reference of terms used throughout the training. This grows as we cover more modules.

## A

**Additive measure** — a measure that can be summed across any dimension. Examples: notional, sensitivities (within constraints), stress P&L.

**As-of date** — the business date a risk view represents. Distinct from the system date (when the data was inserted).

## B

**Backtesting** — comparing predicted VaR to actual P&L outcomes. Regulatory requirement.

**Basel** — the framework of global banking regulations from the Basel Committee on Banking Supervision (BCBS).

**BCBS 239** — the regulator's standard for risk data aggregation and reporting principles.

**Bitemporality** — modeling two independent time axes: business time (when something was true in the world) and system time (when we knew it).

**Book** — a logical container of trades and positions, used for management, risk, and P&L purposes.

## C

**CCP** — Central Counterparty. A clearing entity (e.g., LCH, CME) that interposes itself between counterparties.

**CRO** — Chief Risk Officer. Head of the firm-wide risk function.

**CS01** — sensitivity to a 1bp change in credit spread.

**CSA** — Credit Support Annex. Defines collateral terms between counterparties.

## D

**Delta (Δ)** — sensitivity of an option's value to changes in the underlying price.

**DV01** — Dollar Value of a 01 (basis point). Sensitivity of a fixed income position to a 1bp change in yield.

## E

**EAD** — Exposure at Default. Credit risk measure.

**EOD** — End of Day.

**ES (Expected Shortfall)** — also called CVaR. The average loss in the worst (1-α)% of cases. FRTB's replacement for VaR.

## F

**F2B / Front-to-Back** — the full lifecycle of a trade from origination to settlement.

**FO** — Front Office. The revenue-generating side of the firm.

**FRTB** — Fundamental Review of the Trading Book. The current Basel market risk capital framework.

## G

**Gamma (Γ)** — second derivative of an option's value w.r.t. the underlying. Rate of change of delta.

**Grain** — the level of detail represented by one row in a fact table. The single most important concept in dimensional modeling.

## I

**IMA** — Internal Models Approach. FRTB's option for using internal models for capital, subject to approval.

**IMCC** — Internal Models Capital Charge. The aggregated capital number under FRTB IMA.

**IPV** — Independent Price Verification. Periodic check that FO marks are reasonable.

**ISDA** — International Swaps and Derivatives Association. Publishes standard derivatives documentation.

## L

**LEI** — Legal Entity Identifier. A 20-character global ID for legal entities.

## M

**MDM** — Master Data Management. The discipline of maintaining authoritative reference data.

**MO** — Middle Office. Independent layer between FO and operations.

**Monte Carlo** — simulation-based methodology for VaR and pricing.

## N

**NMRF** — Non-Modellable Risk Factor. Under FRTB, factors lacking sufficient observable data evidence get punitive capital treatment.

**Non-additive measure** — a measure that cannot be summed; it must be recalculated. Examples: VaR, ES, ratios.

## P

**PC** — Product Control. Independent producer of official daily P&L.

**PFE** — Potential Future Exposure. Counterparty credit risk measure.

**Position** — net holding in an instrument at a point in time, derived from accumulated trades.

## R

**Risk factor** — an underlying market input (a specific tenor on a yield curve, a stock price, a vol point) to which positions have sensitivity.

**Rho (ρ)** — sensitivity to interest rates.

## S

**SA** — Standardized Approach. FRTB's prescribed methodology for capital, used by all firms (and as a backstop to IMA).

**SCD** — Slowly Changing Dimension. Strategies for handling dimension changes over time (Type 1, 2, 3, 6).

**Semi-additive measure** — summable across some dimensions but not others. Positions: summable across books, not across dates.

**Sensitivity** — partial derivative of a position's value w.r.t. a market factor. The "Greeks" plus DV01, CS01, etc.

**STP** — Straight-Through Processing. Fully automated trade flow.

**Stress P&L** — P&L of a portfolio under a specific defined market scenario.

**sVaR** — Stressed VaR. Basel 2.5 measure: VaR computed using a stressed historical period.

## T

**Theta (Θ)** — time decay. Sensitivity of an option's value to the passage of time.

**Trade** — a single executed transaction.

## V

**VaR (Value at Risk)** — the loss threshold not expected to be exceeded with X% confidence over Y days.

**Vega (ν)** — sensitivity of an option's value to implied volatility.

---

*This glossary will be expanded as more modules are completed.*
