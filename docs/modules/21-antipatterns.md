# Module 21 — Anti-patterns & War Stories

!!! abstract "Module Goal"
    Every anti-pattern in this module produced a real production incident at a real bank. None of them are exotic; all of them are the kind of pragmatic shortcut that looks reasonable on the day it ships and looks indefensible on the day the regulator asks about it. Module 21 is the synthesis chapter — it pulls the engineering material from M05 through M18 into a working catalogue of failure modes, gives each one a single-page block (symptom → why it happens → why it hurts → fix → before/after SQL), and trains the reader to recognise the patterns in their own warehouse before someone else does. The patterns are easy to see in retrospect. The whole point of the module is to make them easy to see in prospect.

---

## 1. Learning objectives

By the end of this module, you should be able to:

- **Recognise** the pre-aggregation trap — a `fact_var_*` table that pre-sums a non-additive measure — by inspection of a schema, and articulate the recompute-from-components fix in the language of M12.
- **Audit** a candidate fact table for additivity violations, missing bitemporality, mixed grains, hard-coded calendar assumptions, and bypassed conformance, and produce a triaged list of remediation work.
- **Identify** hard-coded calendar, FX, and scenario-set assumptions in transformation code, and replace them with dimension joins (M06, M10, M11) that absorb the change without a code edit.
- **Apply** the *store components, not aggregates* rule consistently — for VaR, ES, capital, and any other non-additive measure — and defend the storage decision against an architect who wants the dashboard to "just be fast."
- **Sequence** an anti-pattern remediation with the parallel-run, backfill, and consumer-retirement steps that turn a schema fix into a credible one rather than a fresh source of incidents.
- **Distinguish** the schema-level anti-patterns (additivity, bitemporality, grain, conformance) from the operational anti-patterns (silent DQ failures, helpful-DBA hotfixes, untracked spreadsheet outputs) and route each to the right remediation team.

## 2. Why this matters

Every anti-pattern in this catalogue was harvested from a real incident. Names and amounts are abstracted, but the shapes are real: a regional VaR table that did not match the recomputed firmwide number, a fact table that could only show *yesterday's report as we know it now* when the regulator asked for *yesterday's report as we knew it then*, a month-end batch that broke every time month-end fell on a Sunday, an "official" feed that turned out to be a vendor mid quote that the desk had repudiated. None of these required a sophisticated attacker, a novel technology, or a black swan. Each of them required only a moment of pragmatic shortcutting on the day the table was built, and several years of nobody asking the awkward question.

The cost asymmetry is the reason this module exists. Each of these anti-patterns costs an hour to avoid in design and weeks-to-months to remediate in production. Some of them cost a regulatory enforcement action when they finally surface — BCBS 239 §36 is unambiguous about restating-the-past as a *defect*, not a feature, and the supervisor who finds it during an on-site review will not accept *we'll fix it next quarter* as a remediation plan. Once the anti-pattern is in the warehouse, every report built on top of it inherits the defect; ripping it out requires a parallel-run period, a back-population, and a careful retirement of the downstream consumers, which together take months and burn political capital the team would rather spend elsewhere.

The practitioner framing for this module is therefore *prospective*. The goal is not to tour the museum of past failures, although that is half the fun. The goal is to install a set of recognition reflexes — the engineer who can spot AP1 in a schema review during the design phase saves the firm a year of remediation later. Each anti-pattern in section 3 is presented in a uniform single-page block (symptom, why-it-happens, why-it-hurts, the-fix, before/after SQL) so the reader can scan the catalogue, recognise the shape in a current piece of work, and walk back to the architect with a defensible counter-proposal before the table is materialised. The before/after SQL pairs are deliberately short — the lesson is in the diff, not in the depth of either side.

A reading note for the rest of the module. Sections 3.1 to 3.6 are the must-read core — every BI engineer in market risk encounters at least three of these in their first year on a real warehouse, and most encounter all six within two years. Sections 3.7 and 3.8 are common but slightly more specialised; the worked examples in section 4 will revisit them. Each block is deliberately short (single-page) and uniformly structured: the *symptom* paragraph is what the consumer or the regulator sees, the *why-it-happens* paragraph is the technical or organisational origin, the *why-it-hurts* paragraph quantifies the cost in audit-failure / capital-impact / P&L-mis-attribution / operational-toil terms, the *fix* paragraph names the architectural counter-pattern, and the *before/after SQL* makes the diff concrete. A reader who is short on time can read the symptom paragraphs alone and treat the catalogue as a checklist; a reader who is in the middle of a remediation will want the full block.

## 3. Core concepts

A reading note. Section 3 is the catalogue. Each sub-section is a self-contained one-page block, and the blocks can be read in any order; the numbering reflects the rough order of frequency-times-severity in the field, not a logical dependency. APs 1 through 6 are the must-knows; APs 7 and 8 are common enough to include and will recur in the worked examples. The before/after SQL in each block is intentionally minimalist — the diff is the lesson, not the surrounding architecture.

### 3.1 AP1 — Pre-aggregating a non-additive measure

**Symptom.** A `fact_var_region` table sits in the warehouse and powers a regional-VaR dashboard tile. Reports sliced by region show one number; the firmwide number computed by the methodology team's engine shows a different number. The gap is not noise — it is consistent, and it is in the friendly direction (the dashboard total is too high, because summing per-region quantiles ignores cross-region diversification). Risk managers learn to "use the engine number" for the firmwide line and "use the dashboard number" for regional lines; they have stopped trusting the dashboard for any rollup.

**Why it happens.** Someone optimised the dashboard. The original design routed every regional-tile request to the engine, the engine took thirty seconds, the dashboard felt slow, and a well-meaning engineer materialised an overnight `fact_var_region` table that pre-summed VaR by region. The performance problem went away; the additivity problem appeared silently. The pre-aggregation never had a sponsor in methodology — it was a one-line architectural decision in a Tuesday standup that the methodology team never reviewed.

**Why it hurts.** Every report sliced by region is wrong by the regional diversification benefit, which on a typical IB book is 20–35%. Aggregating regions to firmwide compounds the error. BCBS 239 §3 requires that risk-aggregation be accurate; an internal-audit reviewer who notices the gap will write a finding. The methodology team will be asked to explain the discrepancy to the supervisor. The fix is invasive — the pre-aggregated table cannot simply be dropped because dozens of dashboards now depend on it — and the firm spends six months unwinding what took an engineer one afternoon to introduce. Module 12 §3.5 is the canonical reference; this anti-pattern is the embodied version of that section.

A second-order cost: once the wrong number is in the firmwide tile, the *correct* number from the methodology engine looks like a discrepancy that the risk team has to explain. The conversation flips — instead of *the dashboard is wrong, fix it*, the conversation becomes *why does the engine disagree with the dashboard?* The methodology team then spends days reconciling, the data team spends days defending, and the actual fix gets deferred again. This dynamic — *the wrong number defends itself once it is in production* — is the political reason these tables linger in warehouses for years.

**The fix.** *Store the components, recompute the aggregate.* The fact tables that matter are the position-level fact, the market-data snapshots, and the per-scenario P&L vectors. Regional VaR is computed *from* those components, never *summed from* a coarser layer. If consumer performance demands a materialised regional number, materialise it as an *independently computed* quantity (the methodology engine runs at the regional grain and writes the result), not as a sum of per-desk numbers. Every non-additive column is flagged in the data dictionary with a `safe_aggregation = none` attribute; the BI semantic layer disables `SUM` for those columns by default and routes the user through a defined safe-aggregation measure.

**Before / after SQL.** The before is the friendly-looking pre-aggregation; the after stores the components and exposes a recompute pattern.

```sql
-- BEFORE: a tempting pre-aggregation that bakes in the wrong rollup
CREATE TABLE fact_var_region AS
SELECT
    region_id,
    business_date,
    SUM(var_99_1d) AS region_var_99_1d   -- NON-ADDITIVE: this number is wrong
FROM fact_var_desk
GROUP BY region_id, business_date;

-- Any downstream report that does
--   SELECT SUM(region_var_99_1d) FROM fact_var_region
-- compounds the error to firmwide level.

-- AFTER: store the components and recompute on demand (or independently)
-- 1. Position-level fact (atomic, additive in notional/MTM)
SELECT position_id, book_id, region_id, business_date, mtm_usd
FROM fact_position
WHERE business_date = DATE '2026-05-07';

-- 2. Per-scenario P&L vectors, joined to positions and aggregated to the
--    requested grain BEFORE taking the quantile.
SELECT
    region_id,
    PERCENTILE_DISC(0.01) WITHIN GROUP (ORDER BY scenario_pnl_usd) AS region_var_99_1d
FROM (
    SELECT
        p.region_id,
        s.scenario_id,
        SUM(s.pnl_usd) AS scenario_pnl_usd      -- additive INSIDE the scenario
    FROM fact_position p
    JOIN fact_scenario_pnl s USING (position_id, business_date)
    WHERE p.business_date = DATE '2026-05-07'
    GROUP BY p.region_id, s.scenario_id
) per_region_per_scenario
GROUP BY region_id;
```

What changed: the after computes the regional quantile from the underlying per-scenario aggregation, which respects the math; the before sums a quantile, which does not.

**Before / after schema (visual).**

```text
BEFORE — pre-aggregated VaR (the anti-pattern)
+-----------------------+         +------------------------+
|   fact_var_desk       |  SUM →  |   fact_var_region      |
|-----------------------|         |------------------------|
| desk_id     PK        |         | region_id     PK       |
| business_date PK      |         | business_date PK       |
| var_99_1d  (NUMERIC)  |         | var_99_1d   ← SUM lies |
+-----------------------+         +------------------------+
                                            ↓
                                   firmwide_var = SUM(...)
                                   (compounded error)

AFTER — store components, recompute on demand
+--------------------+    +-------------------------+    +-----------------+
|  fact_position     |    |  fact_scenario_pnl      |    | dim_scenario    |
|--------------------|    |-------------------------|    |-----------------|
| position_id   PK   |←─→ | position_id      PK_part|←──→| scenario_uid PK |
| book_id            |    | scenario_id      PK_part|    | scd2 validity   |
| region_id          |    | business_date    PK_part|    +-----------------+
| business_date PK   |    | pnl_usd  (additive INSIDE
| mtm_usd            |    |          a single scenario) |
+--------------------+    +-------------------------+
                ↓                       ↓
        (aggregate per (region × scenario) FIRST,
         take quantile of the resulting distribution
         ─ no SUM of quantiles anywhere)
```

### 3.2 AP2 — Storing only the latest snapshot (no bitemporality)

**Symptom.** The regulator (or internal audit, or the head of risk) asks for *yesterday's report as we knew it then*. The team can produce *yesterday's report as we know it now* — the current state of the warehouse filtered to yesterday's `business_date` — but cannot produce the version of the report that was actually delivered yesterday morning, because overnight a late trade arrived, a market-data correction was applied, and a counterparty-id remap was processed. The two reports disagree by an amount the team cannot explain, and the explanation that *the underlying data has been corrected since* is a BCBS 239 §6 failure, not an answer.

**Why it happens.** The fact tables were modelled at a single time dimension — `business_date` — and every overnight ingest does an UPSERT in place. There is no `as_of_timestamp`, no record-validity interval, no system-time history. The original schema was simpler this way, and at design time nobody articulated the requirement to reproduce a prior delivery byte-for-byte. The cost of bitemporality looked like complexity; the benefit looked theoretical. Two years later the supervisor asks for a six-month replay and the cost lands all at once.

**Why it hurts.** BCBS 239 §6 (timeliness) and §7 (adaptability) are explicit that risk reports must be reproducible at the as-of moment they were delivered; the SOX framework requires the same for any number reported externally; internal audit will issue a finding and the regulator may issue an MRA (matter requiring attention). Beyond the formal failures, the trust cost is severe — every late trade, every market-data correction, every backfill of a reference table now silently changes prior reports, and there is no way to demonstrate to a stakeholder that the number they saw last Tuesday was the number that was true at last Tuesday's close. Module 13 is the canonical reference; this anti-pattern is the negative.

There is a particularly acute version of this failure mode in regulatory submissions. When the supervisor asks a follow-up question on a submission delivered six weeks ago, the team needs to reproduce the *exact* numbers the supervisor is reading on their copy of the submission, then explain any difference between those numbers and what the warehouse currently shows. Without bitemporality, the team cannot reproduce the original numbers; they can only show the current state of the data and *speculate* about what changed. The supervisor's reasonable response is to lose trust in the submission process itself. Recovering that trust takes years, not months.

**The fix.** Bitemporal fact tables — `(business_date, as_of_timestamp)` is the minimum, with an explicit record-validity interval if the warehouse expects retroactive corrections. The bitemporal pattern from M13 §3.4 is the standard: every fact carries the *business date* it describes and the *as-of moment* at which the warehouse believed it. Reports filter on both dimensions; *as we knew it then* becomes a single predicate (`as_of_timestamp <= '2026-05-07T18:00:00Z'`); the underlying append-only table preserves the full history and the storage cost is small.

**Before / after SQL.**

```sql
-- BEFORE: single-version table, in-place UPSERT
CREATE TABLE fact_position (
    position_id     VARCHAR  PRIMARY KEY,
    book_id         VARCHAR,
    business_date   DATE,
    notional_usd    NUMERIC,
    mtm_usd         NUMERIC
);
-- Overnight job does:
--   MERGE INTO fact_position USING staging ... WHEN MATCHED THEN UPDATE ...
-- After the merge, prior versions are gone. There is no way to ask for
-- "the value that was in this row yesterday at 18:00".

-- AFTER: bitemporal — append-only, point-in-time queryable
CREATE TABLE fact_position (
    position_id          VARCHAR,
    book_id              VARCHAR,
    business_date        DATE,
    as_of_timestamp      TIMESTAMP,   -- system time: when did we know this?
    valid_from_timestamp TIMESTAMP,
    valid_to_timestamp   TIMESTAMP,   -- NULL = currently valid
    notional_usd         NUMERIC,
    mtm_usd              NUMERIC,
    PRIMARY KEY (position_id, business_date, as_of_timestamp)
);

-- Reproduce yesterday's 18:00 delivery:
SELECT position_id, book_id, notional_usd, mtm_usd
FROM fact_position
WHERE business_date     = DATE '2026-05-06'
  AND valid_from_timestamp <= TIMESTAMP '2026-05-06 18:00:00'
  AND (valid_to_timestamp >  TIMESTAMP '2026-05-06 18:00:00'
       OR valid_to_timestamp IS NULL);
```

What changed: the after appends new versions instead of overwriting, and the `valid_from`/`valid_to` interval lets any historical query reproduce the prior view exactly.

**Before / after schema (visual).**

```text
BEFORE — single-version fact, in-place UPSERT
+---------------------------------+
|        fact_position            |
|---------------------------------|
| position_id     PK              |
| book_id                         |
| business_date                   |   overnight job:  MERGE … UPDATE
| notional_usd                    |       │
| mtm_usd                         |       ▼
+---------------------------------+   prior versions GONE
                                       (no replay possible)

AFTER — bitemporal, append-only, point-in-time queryable
+--------------------------------------------------------------+
|                       fact_position                          |
|--------------------------------------------------------------|
| position_id            PK_part                               |
| business_date          PK_part   (event time)                |
| as_of_timestamp        PK_part   (system time / known-when)  |
| valid_from_timestamp                                         |
| valid_to_timestamp     NULL = currently valid                |
| notional_usd                                                 |
| mtm_usd                                                      |
+--------------------------------------------------------------+
   "as we knew it then" =  filter on (business_date, as_of_timestamp)
   "as we know it now"  =  filter on (business_date, valid_to IS NULL)
```

### 3.3 AP3 — One big fact table with mixed grains

**Symptom.** A `fact_risk` table powers most of the team's reports. `SELECT SUM(notional_usd) FROM fact_risk WHERE business_date = ...` produces a number that is roughly twice what the desk heads expect. Row counts vary by an order of magnitude depending on the filter. The team has learned to add `WHERE grain = 'trade'` or `WHERE source = 'desk_summary'` to every query; new joiners are caught by the gotcha for months. Reconciliation against the upstream FO system passes most days and fails on others without obvious cause.

**Why it happens.** The original `fact_risk` table was at trade grain. Six months in, a desk-summary source arrived without trade-level detail; rather than building a separate fact, an engineer unioned the desk-level summary rows into the same table with a `grain` column to disambiguate. Three months later a position-snapshot source was added the same way. The table now contains rows at three grains, and every query must filter on grain to be correct. Module 07 §3.2 is unambiguous that a fact table has *one* grain; this anti-pattern is the *don't*.

**Why it hurts.** Every query is suspect — anyone who forgets the grain filter gets a wrong answer that does not visibly look wrong. Debugging takes hours because the failure mode is silently doubled or tripled numbers, not an error. Conformed dimensions become harder to maintain because the grain column is implicit in every join. The downstream BI tool cannot expose the table to self-service users without wrapping it in views — and once the views exist, the original table has no business existing. The fix is to split the table by grain, but every consumer that depends on the merged view has to be migrated, and the migration takes months because the consumers are everywhere.

Two failure modes are particularly insidious. First, *aggregation order matters in mixed-grain tables*: if the trade-grain rows and the desk-summary-grain rows are both present, a `SUM` over the desk dimension produces one number, a `SUM` over the trade dimension produces a different number, and a `SUM` over both produces a third. None of the three is right unless the grain filter is applied first. Second, *late-arriving sources change the grain mix*: when a new source is unioned in at a different grain, every existing query becomes silently wrong from that release forward, with no error and no visible signal. The team often discovers the change only weeks later when a reconciliation breaks; tracing back to the release is slow.

**The fix.** *One fact, one grain.* Split `fact_risk` into `fact_trade`, `fact_position`, `fact_desk_summary`, with a clear naming convention that telegraphs the grain in the table name. Each fact has a documented grain statement at the top of its data-dictionary entry. Cross-grain comparisons happen via aggregation in the model layer, never via union in the storage layer. Where a downstream consumer genuinely needs the merged view, it is a view, not a table, and the view names the grain explicitly.

**Before / after SQL.**

```sql
-- BEFORE: mixed-grain fact, every query needs a grain filter to be safe
CREATE TABLE fact_risk (
    grain          VARCHAR,   -- 'trade' | 'position' | 'desk_summary'
    trade_id       VARCHAR,   -- NULL when grain != 'trade'
    position_id    VARCHAR,   -- NULL when grain != 'position'
    desk_id        VARCHAR,
    business_date  DATE,
    notional_usd   NUMERIC,
    mtm_usd        NUMERIC
);
-- Naive query (wrong: triple-counts because each grain has its own row):
SELECT desk_id, SUM(notional_usd)
FROM fact_risk
WHERE business_date = DATE '2026-05-07'
GROUP BY desk_id;

-- AFTER: split by grain, each table single-purpose and unambiguous
CREATE TABLE fact_trade    (trade_id    PK, desk_id, business_date, notional_usd, mtm_usd);
CREATE TABLE fact_position (position_id PK, desk_id, business_date, notional_usd, mtm_usd);
CREATE TABLE fact_desk_summary (desk_id PK_part, business_date PK_part, notional_usd, mtm_usd);

SELECT desk_id, SUM(notional_usd)
FROM fact_position                          -- explicit grain choice
WHERE business_date = DATE '2026-05-07'
GROUP BY desk_id;
```

What changed: the after forces the analyst to pick the grain explicitly by choosing the table; there is no silent triple-count failure mode.

### 3.4 AP4 — Hard-coded business dates and timezone-naive EOD

**Symptom.** The month-end reports go wrong every time month-end falls on a weekend or a regional holiday. Cross-region reports show inconsistent dates — the Tokyo desk's number is for `2026-05-07`, the London desk's number is for `2026-05-06`, and the New York desk's number is from a snapshot taken halfway through London's afternoon. A production incident is logged on most US public holidays because the New York EOD batch ran against a London-EOD snapshot that did not exist. The team has accumulated dozens of `WHERE business_date = '2026-05-07'` patches.

**Why it happens.** Early reports were written with `WHERE business_date = CURRENT_DATE - 1` or, worse, with a hard-coded date string that someone "will fix tomorrow." There is no `dim_business_date` with region-aware trading-day flags (M06 §3.4 prescribes one). The notion of *which 5pm* is not encoded anywhere; the EOD batch assumes "yesterday in the server's timezone" and that assumption was true on the day it was written and false from the next holiday onward.

**Why it hurts.** Production incidents on every regional holiday and every weekend month-end. Cross-region reports that look right on Tuesday and wrong on Monday because the regions disagree about which business date is current. Hours of operations time spent applying date-string patches. The trader population learns to distrust any cross-region rollup because they have seen too many timezone-confused versions. The fix is mechanically straightforward — a date dimension with region-aware trading-day flags — but every query in the warehouse has to be migrated to use it, and the migration touches code in dozens of places.

The hidden cost is reputational with the operations team. Every holiday-driven incident is a 6 a.m. page, an hour of triage, a patch, and a post-mortem; the operations team learns that the data warehouse is *fragile around dates* and starts treating every release with extra suspicion. Some of that suspicion is healthy; most of it is overhead the team has earned through avoidable failures. A clean date-dimension migration retires not only the incidents but the suspicion.

**The fix.** A parameterised `dim_business_date` keyed by `(date, region)` with explicit `is_trading_day`, `is_eom`, `prev_trading_day`, `next_trading_day`, and `eod_timestamp_utc` columns. Every report filters by joining to the dimension and asking the question in the dimension's vocabulary, not the calendar's. The EOD batch is parameterised by region and consults the dimension for *which 5pm* — there is no naked `CURRENT_DATE - 1` anywhere in the production code base.

**Before / after SQL.**

```sql
-- BEFORE: hard-coded date logic, breaks on holidays and across regions
SELECT SUM(notional_usd) AS firmwide_notional
FROM fact_position
WHERE business_date = CURRENT_DATE - 1;     -- which timezone? what about Monday?

-- BEFORE (worse): hard-coded month-end string
SELECT SUM(notional_usd)
FROM fact_position
WHERE business_date = DATE '2026-05-31';    -- 2026-05-31 is a Sunday

-- AFTER: date-dim-driven, region-aware, holiday-aware
SELECT SUM(p.notional_usd) AS firmwide_notional
FROM fact_position p
JOIN dim_business_date d
  ON  p.business_date = d.business_date
  AND d.region_id     = 'GLOBAL'
WHERE d.is_eom_global = TRUE
  AND d.business_date = (
      SELECT MAX(business_date) FROM dim_business_date
      WHERE region_id = 'GLOBAL' AND is_eom_global = TRUE
        AND business_date <= CURRENT_DATE
  );
```

What changed: the after asks the date dimension *which date is the most recent global month-end trading day* and the dimension absorbs every holiday, weekend, and timezone question that the before encoded as bugs.

### 3.5 AP5 — Implicit conformance (fixing identifiers in the report layer)

**Symptom.** The same counterparty appears with two different identifiers in two reports — the credit-risk report knows it as `CP_104592`, the market-risk report knows it as `LEI:529900T8BM49AURSDO55`. Reconciliation across the two reports fails because the join key does not match. Each report has its own `CASE WHEN ... THEN ...` xref logic embedded in the SQL, and the two CASE statements do not agree on edge cases. New reports rebuild the wheel; DQ checks miss the inconsistency because each report passes its own internal checks.

**Why it happens.** The silver-layer `dim_counterparty` exists but is incomplete; rather than fixing it, each report-team patched their own xref into the report's SQL. This was faster on the day, and the report shipped on time, but the patch became permanent. M18 §3.3 is explicit that conformance belongs in the silver layer; this anti-pattern is the embodied violation. The reason it persists is organisational: fixing `dim_counterparty` requires cross-team agreement that the report-team would rather not negotiate, while patching their own report's SQL requires nobody's agreement at all.

**Why it hurts.** Data lineage fragments — there is no single source of truth for *which counterparty is which*. Every new report rebuilds the xref logic from first principles, with subtle differences. DQ checks miss the inconsistency because they validate within a report, not across reports. When a counterparty merges with another, every CASE statement in every report has to be found and updated, and inevitably some are missed. The eventual fix — consolidate the xref into a single `dim_xref` and migrate every report — is a multi-quarter programme.

The clearest external symptom is reconciliation failure between credit-risk and market-risk views of the same counterparty exposure. Both teams compute exposures correctly *within their own reporting world*; the cross-team comparison fails because the join key is silently different. When the supervisor (or the firm's own risk-aggregation function) asks for a unified counterparty view, the team has to admit that the unified view does not exist — they can produce two reports that disagree, and a manual reconciliation. This is precisely the failure mode BCBS 239 §9 (single source of truth for risk data aggregation) was written to prevent.

**The fix.** One canonical `dim_xref` (or augmented `dim_counterparty`) in the silver layer that maps every known identifier (internal IDs, LEI, vendor IDs, legacy IDs from acquired firms) to a single `counterparty_uid`. Downstream marts join to it. The `dim_xref` is SCD2 so historical reports can reproduce the mapping that was in force at the time. Per-report CASE-statement xrefs are forbidden and called out in code review.

**Before / after SQL.**

```sql
-- BEFORE: per-report CASE-statement xref, inconsistent across reports
SELECT
    CASE
        WHEN cp_code LIKE 'CP_%' THEN cp_code
        WHEN cp_code LIKE 'LEI:%' THEN SUBSTR(cp_code, 5)
        ELSE cp_code
    END AS cp_uid,
    SUM(notional_usd)
FROM fact_trade
GROUP BY 1;

-- AFTER: centralised dim_xref join, single source of truth
SELECT
    x.counterparty_uid,
    SUM(t.notional_usd)
FROM fact_trade t
JOIN dim_xref x
  ON  x.source_system  = t.source_system
  AND x.source_cp_code = t.cp_code
  AND t.business_date BETWEEN x.valid_from_date AND x.valid_to_date
GROUP BY x.counterparty_uid;
```

What changed: the after delegates the xref to a single dimension that every report shares, and the SCD2 validity interval handles historical mappings cleanly.

### 3.6 AP6 — Over-trusting source systems' "official" feed

**Symptom.** A downstream P&L report shows a price that the trading desk does not recognise. Investigation reveals that the report joined directly to a vendor's mid quote feed, while the desk's own books used the cleansed *official* mark that the methodology team blesses. The two prices differ by 18bp, the P&L impact is material, and the desk loses trust in every downstream P&L number. The report had been running for a year; nobody had asked which feed it was using.

**Why it happens.** No formal market-data hierarchy (M11 §3.2 prescribes vendor → cleansed → official with explicit lineage), or the cleansed layer existed but was bypassed because it was harder to query. The report-author chose the vendor table because it was simpler; they did not realise that "vendor" and "official" were different things. The architecture diagram showed *one market-data feed*; the reality was *seven, with no canonical choice enforced*.

**Why it hurts.** P&L attribution does not match the desk's own books, the desk loses trust, every downstream analytical report is now suspect, and the methodology team has to spend weeks reconstructing which reports used which feed. If the price discrepancy ever feeds into a regulatory submission, the supervisor will ask which mark the firm uses *officially* and will not accept *it depends on the report*. The fix is to enforce the official cut as the single blessed source and to route every other use through an audit-logged exception process.

There is a regulatory dimension as well. FRTB IMA requires that the bank can identify, for every risk factor used in capital calculation, the modellability evidence behind the price observations — and the price observations are required to come from a *real, observable, transacted* source, not an unverified vendor mid. Bypassing the cleansed layer almost always means bypassing the modellability documentation that lives alongside it; the firm then cannot defend the IMA inputs to the supervisor. The remediation cost is more than just fixing the table — it includes reconstructing the modellability evidence retroactively, which is sometimes impossible.

**The fix.** A single `fact_market_data_official` table that every downstream consumer joins to by default; the vendor and cleansed layers exist for diagnostic and reconciliation purposes but are not the default join. An explicit fallback policy is encoded — when the official cut is missing, the consumer chooses between (a) failing the report, (b) using the cleansed cut with a flag, or (c) using the vendor cut with a louder flag — and the choice is logged.

**Before / after SQL.**

```sql
-- BEFORE: direct vendor join, no official-vs-vendor discipline
SELECT t.trade_id, t.notional, v.mid_price * t.notional AS mtm
FROM fact_trade t
JOIN vendor_market_data v
  ON v.instrument_id = t.instrument_id
 AND v.snapshot_time = (
     SELECT MAX(snapshot_time) FROM vendor_market_data
     WHERE instrument_id = t.instrument_id
 );

-- AFTER: official-snapshot join with explicit fallback logged
SELECT
    t.trade_id,
    t.notional,
    o.official_price * t.notional AS mtm,
    o.source_quality_flag                          -- 'OFFICIAL' | 'CLEANSED_FALLBACK' | 'VENDOR_FALLBACK'
FROM fact_trade t
JOIN fact_market_data_official o
  ON  o.instrument_id = t.instrument_id
  AND o.business_date = t.business_date
  AND o.snapshot_id   = 'GLOBAL_EOD_OFFICIAL'      -- the blessed cut for this report
WHERE o.source_quality_flag IS NOT NULL;
```

What changed: the after joins to an explicitly-named blessed snapshot with a quality flag exposed in the row, so every consumer of the result can see which feed was actually used.

### 3.7 AP7 — Hard-coded scenario list (the "we'll fix it later" constant)

**Symptom.** Every quarter, the methodology team re-calibrates the stress-scenario set. Every quarter, the stress-P&L reports break on the day the new set is published, because the scenario identifiers are hard-coded as constants in the transformation SQL. The data team applies a patch, ships it, and the same thing happens next quarter. SCD2 history of the scenario set is lost because the constants do not version.

**Why it happens.** The original report was written when there were three scenarios; the engineer wrote `WHERE scenario IN ('SCN_2008Q4', 'SCN_2011_EUR', 'SCN_2020Q1')` because it was simpler than building a `dim_scenario` (M10 §3.5). The methodology team grew the set to seventeen scenarios and re-versions them every quarter. The engineer who wrote the constant has long since moved teams; nobody has the political appetite to refactor.

**Why it hurts.** Every methodology change is a code change in N reports. SCD2 history of the scenario definitions is unrecoverable — there is no record of which scenario set was in force on any prior date. Backtesting the scenario set against historical data requires reconstructing the constants from version-control history, which is unreliable. The audit trail for *which scenarios were used in last quarter's submission* lives in the git log of the transformation repository, not in the warehouse — and the git history is rarely admissible as a regulatory artefact. The methodology team owns the scenario set conceptually but does not own it operationally; ownership lives in the transformation repository, which they cannot edit. Every quarterly recalibration becomes a hand-off ceremony between methodology and the data team, with the inevitable misunderstandings and timing pressure.

**The fix.** A proper `dim_scenario` SCD2 dimension in the silver layer; transformations join to it filtered by `business_date BETWEEN valid_from AND valid_to`; the constants disappear from the SQL. New scenarios appear by inserting a row into the dimension, not by editing transformation code.

```sql
-- BEFORE: hard-coded scenario constants
SELECT scenario, SUM(scenario_pnl)
FROM fact_scenario_pnl
WHERE business_date = DATE '2026-05-07'
  AND scenario IN ('SCN_2008Q4', 'SCN_2011_EUR', 'SCN_2020Q1')
GROUP BY scenario;

-- AFTER: dim_scenario SCD2 join, no constants
SELECT s.scenario_uid, SUM(p.scenario_pnl)
FROM fact_scenario_pnl p
JOIN dim_scenario s
  ON  p.scenario_id    = s.source_scenario_id
  AND p.business_date  BETWEEN s.valid_from_date AND s.valid_to_date
WHERE p.business_date  = DATE '2026-05-07'
  AND s.is_active_in_official_set = TRUE
GROUP BY s.scenario_uid;
```

What changed: the after delegates the *which scenarios are official today* question to the dimension; the methodology team owns the dimension; the data team owns the join.

### 3.8 AP8 — The DQ check that ran but on yesterday's data

**Symptom.** The DQ dashboard is uniformly green. The downstream report is wrong. The investigation reveals that the DQ check runs on a snapshot taken *before* the corrected file arrived, so it validated the wrong data; or that the tolerance on a balance-check was set so wide (±5%) that a 4% error never tripped it. The team had been treating the green dashboard as evidence of correctness; it was evidence of nothing.

**Why it happens.** Two failure modes in one anti-pattern. (a) *Stale execution*: the DQ check is scheduled at a fixed time that predates the late-arriving correction file; nobody alerts on the staleness of the check itself. (b) *Tolerance theatre*: the tolerance was set during a noisy onboarding period and never tightened; or it was negotiated with the upstream team to *make the dashboard go green* rather than to reflect the business-acceptable error.

**Why it hurts.** False confidence is worse than no confidence. The team and its stakeholders treat the green status as a guarantee; the silent-failure mode (M15 §3.6) is precisely the failure mode that erodes trust catastrophically when it surfaces. Audit will write a finding because the control is not operating effectively. The fix is to timestamp every check, alert on stale checks, and recalibrate every tolerance against a documented business-risk threshold rather than an empirical false-positive rate.

The audit conversation is particularly painful for this anti-pattern. A reviewer who finds that a DQ check has a 5% tolerance against a measure where 1% movement is materially significant will conclude that the *control framework* is broken, not just the individual check. The remediation then becomes a control-framework re-baseline, not a tolerance tweak — every tolerance in the suite has to be re-justified against a documented business-risk threshold, with sign-off from the relevant business owner. This is the right outcome but it is expensive; doing it pre-emptively, before audit asks, is dramatically cheaper.

**The fix.** Every DQ check writes a row to a `fact_dq_check` table with `(check_id, run_timestamp, data_as_of_timestamp, result, tolerance, observed_value)`. A meta-check alerts when `run_timestamp - data_as_of_timestamp` exceeds a per-check threshold or when no row has appeared since the expected schedule. Tolerances are reviewed quarterly against the business-risk threshold, not the false-positive rate.

```sql
-- BEFORE: silent staleness — green dashboard, no idea when it last ran
SELECT check_name, last_status FROM dq_check_status;

-- AFTER: timestamps and meta-checks
SELECT
    c.check_name,
    c.last_status,
    c.last_run_timestamp,
    c.last_data_as_of_timestamp,
    EXTRACT(EPOCH FROM (NOW() - c.last_run_timestamp)) / 60 AS minutes_since_last_run,
    CASE
        WHEN c.last_run_timestamp < NOW() - INTERVAL '90 minutes'
            THEN 'STALE_CHECK_ALERT'
        WHEN c.last_data_as_of_timestamp < c.last_run_timestamp - INTERVAL '60 minutes'
            THEN 'CHECK_RAN_ON_OLD_SNAPSHOT'
        ELSE 'OK'
    END AS meta_status
FROM fact_dq_check c
WHERE c.business_date = CURRENT_DATE;
```

What changed: the after exposes both *did the check run* and *what data did it see*, so the silent-failure mode becomes visible at the dashboard layer rather than at incident-response time.

### 3.9 The operational anti-patterns — short notes

The eight blocks above are the *schema-level* anti-patterns; they live in the warehouse design and they are the responsibility of the data team's architects. There is a parallel family of *operational* anti-patterns that live in the daily process around the warehouse, and they deserve a short paragraph each because the symptoms often look identical to a downstream consumer.

**The "helpful" DBA hotfix.** A production incident at 3 a.m.; the on-call DBA logs in, manually fixes a row, the report goes out on time, no ticket is opened. Three weeks later the same fix is applied again — the underlying cause was never addressed and the manual fix was never recorded. The discovery path is usually a reconciliation that finally fails despite the fix being in place. The remediation is procedural: every production data change is a logged ticket with a reviewer, no exceptions, even at 3 a.m.; the playbook for a 3 a.m. incident is *log first, fix second, post-mortem third*, not *fix first and forget*.

**Untracked spreadsheet outputs.** A monthly report is exported to Excel, a finance analyst tweaks two cells to reflect a manual adjustment, the spreadsheet is forwarded to the CFO. Three months later the same tweak is needed again and nobody remembers what it was. The discovery path is usually a SOX walkthrough where audit asks for the lineage of the CFO's number and discovers that the warehouse number and the CFO's number do not match. The remediation is to bring every off-warehouse adjustment back into a documented `fact_manual_adjustment` table with reviewer, justification, and effective dates.

**Hierarchy drift without SCD2.** A book moves from the equity desk to the macro desk. The `dim_book` is a SCD1 dimension that overwrites — the new desk attribution is applied retroactively, silently, to every prior position the book ever held. Last quarter's equity-desk P&L now shows zero for that book; last quarter's macro-desk P&L shows the entire book's history. Risk managers watching the trend lines see numbers move that they cannot explain. The fix is SCD2 on every dimension that participates in historical aggregation (M06 §3.5 prescribes the catalogue).

**Currency-aware thresholding.** A DQ check carries a *$1M* tolerance applied uniformly to every position regardless of reporting currency. The JPY desk, where notionals are routinely 100M+ in JPY (well under $1M), trips the alert constantly; the team learns to ignore the alert; a real $5M JPY error sails through. The fix is to make every threshold currency-aware (and ideally book-aware) by joining to a `dim_threshold_calibration` keyed by `(check_id, currency, book_id)` rather than hard-coding the threshold in the check definition. Reviewing the calibration table is then a quarterly exercise, not a per-check refactor.

**FX double conversion.** A trade in EUR is converted to USD using the trade-date FX, then the USD figure is converted to GBP for a London-desk report using the report-date FX. The two conversions use different rates and the result is inconsistent with both the EUR original and a single direct EUR-to-GBP conversion. The fix is to convert from the *trade currency* to the *reporting currency* in a single hop, never via an intermediate. The FX dimension is consulted once per row, not chained.

**Snapshot vs live confusion.** A report queries a `position_live` table that the trading systems update continuously, when it should query the `position_snapshot` table that captures the official EOD state. The intraday number drifts away from the EOD number; reconciliation against finance fails by an amount that varies with how late in the day the report ran. The fix is naming discipline (`position_live_intraday` vs `position_snapshot_eod`) plus a hard rule that any report that participates in finance reconciliation joins only to the snapshot, never the live table.

These six operational anti-patterns share the property that the warehouse schema is *correct* but the process around it is broken. Recognising the difference matters for remediation: schema fixes go to the data architects; process fixes go to operations and risk-control. Both are necessary; neither is sufficient on its own. The audit script in section 4 example 2 catches the schema-level patterns; the operational patterns require process discipline (logged tickets for production changes, banned spreadsheet workflows, mandatory SCD2 for hierarchy dimensions, calibrated tolerances, FX one-hop discipline, and naming conventions that telegraph snapshot-vs-live).

### 3.10 What ties the catalogue together

The eight anti-patterns above look heterogeneous on the surface — additivity, bitemporality, grain, calendar, conformance, market-data lineage, scenario sets, DQ scheduling. They are unified by a single deeper failure: each one *bakes a default into the storage layer that the consumer is then unable to question*. The pre-aggregated VaR table bakes in the wrong rollup before the analyst writes their first query. The single-version fact bakes in *as we know it now* and removes the option to ask *as we knew it then*. The mixed-grain table bakes in a triple-count for any naive `SUM`. The hard-coded date filter bakes in a calendar assumption that the production schedule cannot accommodate. The per-report xref bakes in a divergence between two reports that nobody is positioned to detect. The vendor-feed default bakes in a price the desk has repudiated. The constant-list of scenarios bakes in a methodology version. The unstamped DQ check bakes in a confidence level that is not earned.

The architectural counter-pattern, in every case, is *push the default down to the dimension or component layer where it can be parameterised, and force the consumer to make the parameterisation explicit*. The position fact carries `business_date` and `as_of_timestamp`, not a single point-in-time view. The xref dimension carries every legacy alias, not a CASE statement that drops them. The market-data fact carries the `source_quality_flag`, not an unmarked vendor-vs-official choice. The scenario dimension carries SCD2 validity, not a hard-coded list. The DQ check writes its `data_as_of_timestamp`, not just a green/red status. In every case the cost is one additional column or one additional dimension; the benefit is that the consumer's question can be answered in the language the consumer brought, not in the language the original engineer happened to use. This is the single sentence the reader should keep when the catalogue fades: *bake nothing into storage that a consumer might want to parameterise later.*

A second unifying observation. Each of these anti-patterns is *introduced* by a small, well-meaning local optimisation — a faster dashboard, a simpler ETL, a fewer-lines-of-SQL report, a less-effort xref patch, an easier vendor-feed query. The local optimisation is *correct on its own merits*; the failure is that the local optimisation's externalities — the wrong rollup, the lost history, the silent triple-count, the brittle calendar, the fragmented lineage, the unblessed mark, the unversioned scenario, the unstamped check — are absorbed by every other report and consumer in the warehouse, and those externalities are never priced into the original decision. The architectural review process exists precisely to surface those externalities at design time, when the cost of changing course is a one-hour conversation, rather than at remediation time, when the cost is six months of parallel-running and consumer migration. The catalogue in this module is, viewed one way, an inventory of *what to ask about in an architectural review*. Use it that way.

A third observation, and this is the one that closes the loop with M20. Most of these anti-patterns are introduced under stakeholder pressure — *the dashboard is too slow*, *the report needs to ship by Friday*, *just give me the number for now and we'll fix it later*. The data team that absorbs every such pressure ships the anti-patterns. The data team that pushes back — *we can ship by Friday, but the right way costs an extra day; the shortcut costs us a year of remediation* — ships the long-term-correct architecture. Section 3.3 of M20 is the playbook for that conversation; this module's catalogue is the evidence base that justifies the pushback. The two modules are designed to be read together.

## 4. Worked examples

### Example 1 — Three before/after SQL pairs in a single comparative view

The catalogue in section 3 spreads the before/after pairs across the anti-patterns; this consolidated view places three of the most impactful pairs side-by-side so the diff pattern becomes visible. AP1 (pre-aggregation), AP2 (bitemporal upgrade), and AP4 (date-dim parameterisation) are the highest-leverage refactors in most warehouses.

**AP1 — pre-aggregation fix (compressed).**

```sql
-- BEFORE
SELECT region_id, business_date, SUM(var_99_1d)
FROM fact_var_desk
GROUP BY region_id, business_date;

-- AFTER
SELECT region_id,
       PERCENTILE_DISC(0.01) WITHIN GROUP (ORDER BY scenario_pnl_usd) AS region_var_99_1d
FROM (
    SELECT p.region_id, s.scenario_id, SUM(s.pnl_usd) AS scenario_pnl_usd
    FROM fact_position p
    JOIN fact_scenario_pnl s USING (position_id, business_date)
    WHERE p.business_date = DATE '2026-05-07'
    GROUP BY p.region_id, s.scenario_id
) GROUP BY region_id;
```

*What changed.* The before sums a quantile (mathematically wrong); the after aggregates the per-scenario components first and takes the quantile of the resulting per-region distribution (mathematically correct).

**AP2 — bitemporal upgrade (compressed).**

```sql
-- BEFORE: in-place UPSERT, prior versions overwritten
MERGE INTO fact_position USING staging
  ON fact_position.position_id = staging.position_id
WHEN MATCHED THEN UPDATE SET notional_usd = staging.notional_usd, mtm_usd = staging.mtm_usd;

-- AFTER: append-only, point-in-time queryable
INSERT INTO fact_position
    (position_id, business_date, as_of_timestamp, valid_from_timestamp, valid_to_timestamp, notional_usd, mtm_usd)
SELECT position_id, business_date, NOW(), NOW(), NULL, notional_usd, mtm_usd
FROM staging;

UPDATE fact_position
SET valid_to_timestamp = NOW()
WHERE position_id IN (SELECT position_id FROM staging)
  AND valid_to_timestamp IS NULL
  AND as_of_timestamp < NOW();
```

*What changed.* The before destroys history; the after appends and closes the prior interval, preserving every prior version for point-in-time replay.

**AP4 — date-dim parameterisation (compressed).**

```sql
-- BEFORE
SELECT SUM(notional_usd) FROM fact_position
WHERE business_date = CURRENT_DATE - 1;

-- AFTER
SELECT SUM(p.notional_usd)
FROM fact_position p
JOIN dim_business_date d
  ON p.business_date = d.business_date AND d.region_id = 'GLOBAL'
WHERE d.business_date = (
    SELECT MAX(business_date) FROM dim_business_date
    WHERE region_id = 'GLOBAL' AND is_trading_day = TRUE
      AND business_date < CURRENT_DATE
);
```

*What changed.* The before assumes *yesterday* is always a valid trading day in the server's timezone; the after asks the date dimension for the most recent global trading day, and the dimension absorbs holidays, weekends, and timezone differences cleanly.

### Example 2 — A warehouse health-check audit script

The script below is a stylised diagnostic that scans a warehouse for the symptoms of the anti-patterns in section 3. It is written for a generic SQL warehouse with `information_schema` (Snowflake / Postgres / BigQuery dialect notes inline). Treat it as a starting template — every shop will tune the heuristics to its own naming conventions.

```sql
-- =====================================================================
-- WAREHOUSE ANTI-PATTERN HEALTH CHECK
-- Dialect: Snowflake-ish (uses INFORMATION_SCHEMA; works with minor tweaks
-- on Postgres / BigQuery). Mark and adapt the heuristics for your warehouse.
-- =====================================================================

-- AP2 SYMPTOM: fact tables that lack any system-time column
-- (likely missing bitemporality)
SELECT table_schema, table_name
FROM information_schema.tables t
WHERE table_name LIKE 'FACT_%'
  AND NOT EXISTS (
      SELECT 1 FROM information_schema.columns c
      WHERE c.table_schema = t.table_schema
        AND c.table_name   = t.table_name
        AND c.column_name IN ('AS_OF_TIMESTAMP', 'VALID_FROM_TIMESTAMP',
                              'SYSTEM_TIMESTAMP', 'SYS_FROM')
  );

-- AP3 SYMPTOM: fact tables with a 'GRAIN' column (mixed-grain table)
SELECT table_schema, table_name
FROM information_schema.columns
WHERE column_name = 'GRAIN'
  AND table_name LIKE 'FACT_%';

-- AP1 SYMPTOM: fact tables that contain 'VAR', 'ES', 'CAPITAL' in the
-- table name AND in the column name AND show evidence of pre-summation
-- (one row per region/desk rather than per position/scenario).
-- Heuristic: row count is small relative to the position fact, suggesting
-- an aggregate rather than an atomic fact.
WITH agg_candidates AS (
    SELECT table_schema, table_name, row_count
    FROM information_schema.tables
    WHERE (table_name ILIKE '%VAR%' OR table_name ILIKE '%ES_%'
           OR table_name ILIKE '%CAPITAL%')
      AND table_name LIKE 'FACT_%'
)
SELECT a.*, p.row_count AS position_row_count,
       a.row_count::FLOAT / NULLIF(p.row_count, 0) AS pct_of_position
FROM agg_candidates a
CROSS JOIN (SELECT row_count FROM information_schema.tables
            WHERE table_name = 'FACT_POSITION' LIMIT 1) p
WHERE a.row_count < p.row_count * 0.05;   -- < 5% suggests pre-aggregation

-- AP4 SYMPTOM: views or stored procedures with hard-coded date strings.
-- Text-scan the view definitions for date literals or CURRENT_DATE arithmetic.
SELECT table_schema, table_name, view_definition
FROM information_schema.views
WHERE REGEXP_LIKE(view_definition, 'DATE\s*''20[0-9]{2}-[0-9]{2}-[0-9]{2}''')
   OR view_definition ILIKE '%CURRENT_DATE - %';

-- AP5 SYMPTOM: views with inline CASE-statement xref logic on counterparty
SELECT table_schema, table_name
FROM information_schema.views
WHERE view_definition ILIKE '%CASE%LEI:%'
   OR view_definition ILIKE '%CASE%CP\\_%';

-- AP7 SYMPTOM: views with hard-coded scenario IN-lists
SELECT table_schema, table_name
FROM information_schema.views
WHERE REGEXP_LIKE(view_definition,
    'scenario\s+IN\s*\([^)]*''SCN_[^)]+\)', 'i');

-- AP8 SYMPTOM: dq_check rows older than expected (stale checks)
SELECT check_name,
       MAX(run_timestamp) AS last_run,
       EXTRACT(EPOCH FROM (NOW() - MAX(run_timestamp))) / 60 AS minutes_stale
FROM fact_dq_check
GROUP BY check_name
HAVING EXTRACT(EPOCH FROM (NOW() - MAX(run_timestamp))) / 60 > 90;

-- META: row counts that violate SUM(measure) ≈ COUNT × AVG, suggesting
-- the table mixes grains within a single column.
-- Per-grain sanity for a candidate fact:
SELECT
    desk_id,
    COUNT(*)                       AS rows,
    SUM(notional_usd)              AS total_notional,
    AVG(notional_usd)              AS avg_notional,
    COUNT(*) * AVG(notional_usd)   AS expected_total,
    ABS(SUM(notional_usd) - COUNT(*) * AVG(notional_usd)) AS anomaly_residual
FROM fact_risk
GROUP BY desk_id
HAVING ABS(SUM(notional_usd) - COUNT(*) * AVG(notional_usd)) > 0.001;
-- (residual will be ~0 by definition; the diagnostic value is in
--  per-grain row-count differences across desks: a desk whose row count
--  is 100x another's is the smoking gun for AP3.)
```

The script is deliberately stylised — every shop will tune the regex patterns, the table-name conventions, and the row-count thresholds. The point is the *shape* of the audit: a fixed catalogue of anti-pattern signatures that can be re-run quarterly and produces a triaged remediation list. Several of the largest banks publish similar scripts internally as part of their data-governance tooling; if your firm does not have one, this is the skeleton.

A few practitioner notes on operationalising the script.

- *Run it on a schedule and store the output as a fact table.* The diagnostic value compounds when the team can see the trend — number of mixed-grain tables over time, number of views with hard-coded date strings over time. A flat-or-rising trend is a sign that the team's design discipline is not keeping up with the warehouse's growth.
- *Triage every finding into one of three buckets — fix-this-quarter, fix-when-touching, accept-and-document.* The trap is treating every finding as urgent; some are. A well-isolated legacy view used by one decommissioning report is not the same as a foundational fact table that powers fifty downstream consumers, and the triage protects scarce remediation capacity for the cases that matter.
- *Share the output with the methodology and audit teams.* The methodology team will recognise some of the findings as their own pet peeves and will help prioritise; internal audit will appreciate that the data team is finding its own issues before audit has to. Both relationships compound.
- *Re-run after every major release.* A new release that introduces (or worse, re-introduces) an anti-pattern should fail a CI check on the audit script — the team commits to keeping the count flat or shrinking, and the CI gate makes the commitment operational rather than aspirational.

## 5. Common pitfalls

!!! warning "Watch out — pitfalls when *fixing* the anti-patterns"
    1. **Ripping out the pre-aggregated table without a parallel-run period.** AP1 fixes are tempting to ship in a single weekend release. Don't. The dashboards that depend on `fact_var_region` need to be migrated one at a time; the old and new tables should run in parallel for at least one month-end cycle so any consumer hitting the old surface visibly sees the discrepancy and can be migrated in turn. The reconciliation between the two during the parallel-run period IS the validation.
    2. **Bitemporal upgrade that doesn't backfill history.** AP2 fixes that introduce `as_of_timestamp` from the cut-over date forward, with no historical backfill, leave the *prior* history non-reproducible. The first time the regulator asks for a six-month replay, the new bitemporal columns are NULL for the historical rows and the answer to "as we knew it then" is still unavailable. Plan the backfill — even a coarse one (one row per business_date, as_of_timestamp set to the original close-of-day) — at the same time as the schema change.
    3. **Date-dim migration that misses holidays for one region.** Building `dim_business_date` for the global calendar but populating regional flags only for the regions the team currently reports on. The first time a new region onboards, every report breaks the same way it did before. Populate every region the firm operates in, even the dormant ones, and unit-test the holiday list against an external authoritative source (the relevant central bank's published calendar) annually.
    4. **xref consolidation that loses prior IDs without an alias mapping.** AP5 fixes that consolidate multiple legacy IDs into one canonical UID, but drop the legacy IDs from the dimension entirely. The first time someone reruns a historical report that hard-codes a legacy ID, the join fails silently and returns zero rows. The xref dimension MUST keep every legacy ID as a queryable alias indefinitely; storage is cheap, lineage is not.
    5. **Declaring victory after the schema fix without retiring the downstream consumers.** The most common mode of half-finished anti-pattern remediation: the schema is fixed, the migration plan is written, the parallel-run period passes — and the old surface is left in place because retiring it requires N consumer-team conversations that nobody owns. Six months later a new joiner builds a fresh report on the deprecated surface and the anti-pattern is re-introduced. The remediation is not done until the old surface is dropped; until then, leave a `RAISE NOTICE 'DEPRECATED — use fact_position_v2'` in the surface so every query logs the warning.
    6. **Fixing one anti-pattern in isolation while leaving an interaction.** AP1 (pre-aggregated VaR) is sometimes fixed in parallel with AP2 (bitemporality) being left in place. The new `fact_var_v2` is recomputed-from-components but is still single-version — and the new fact then has the AP2 problem instead of the AP1 problem. Fix the related anti-patterns together where the schemas overlap, or sequence them so the second remediation does not have to redo the first.
    7. **Underestimating the methodology team's review time.** Schema fixes that touch the methodology engine's outputs (every fix to AP1, AP6, AP7) require methodology sign-off on the new numbers. Methodology teams typically have 6–8 weeks of review backlog; build that into the schedule from day one or the migration stalls in week 5 waiting for a review that nobody scheduled.

## 6. Exercises

1. **Audit this schema.** A team gives you the following four-table sketch. Identify which anti-patterns are present and rate the severity of each.

    ```text
    fact_var_book        (book_id PK_part, business_date PK_part, var_99_1d, var_99_10d)
    fact_position        (position_id PK, book_id, trade_id, notional_usd, mtm_usd)
                         -- no business_date column; this is "current" only
    dim_book             (book_id PK, desk_id, region_code)
    vw_firmwide_var      (CREATE VIEW AS SELECT business_date,
                                                SUM(var_99_1d) AS firmwide_var
                                         FROM fact_var_book
                                         WHERE business_date >= '2024-01-01'
                                         GROUP BY business_date;)
    ```

    ??? note "Solution"
        - **AP1 (severe).** `fact_var_book` is a pre-aggregated VaR fact and `vw_firmwide_var` then *sums VaR across books*, which is the canonical non-additivity violation. The view is materially wrong.
        - **AP2 (severe).** `fact_position` has no business-date or as-of-timestamp; it is current-only. Any historical report or regulatory replay is impossible.
        - **AP4 (medium).** `vw_firmwide_var` hard-codes `'2024-01-01'` as a start date, which will silently include partial historical periods if anyone re-points the view at a different reference period.
        - **AP5 (latent).** `fact_position.book_id` and `fact_var_book.book_id` are not explicitly conformed to `dim_book` via a foreign-key constraint or contract; if the position ETL and the VaR engine source `book_id` from different upstream systems, a divergence will be invisible until reconciliation.
        - Severity ranking: AP1 and AP2 must be fixed before this schema is suitable for any regulatory submission; AP4 and AP5 are technical debt to be triaged.

2. **Migration plan.** Your warehouse has AP1 (pre-aggregated VaR in a `fact_var_region`) and AP4 (hard-coded dates throughout the reporting layer). You have six weeks. Sketch the migration sequence with milestones.

    ??? note "Solution"
        A defensible six-week sequence:
        - *Week 1.* Build `dim_business_date` populated for every region the firm operates in. Unit-test against the published trading-day calendars. Do not migrate any consumers yet — the dimension exists alongside the legacy code.
        - *Week 2.* Build `fact_var_region_v2` as an independently-computed table (the methodology engine writes the regional VaR directly) running in parallel with the legacy `fact_var_region`. Set up a daily reconciliation report that flags any divergence over a configured tolerance.
        - *Week 3.* Migrate the highest-traffic dashboards (top three by query volume) from `fact_var_region` to `fact_var_region_v2` and from hard-coded date strings to `dim_business_date` joins. Communicate the change in the daily release note. Hold a brown-bag with the consumer teams.
        - *Week 4.* Migrate the long tail of dashboards. Use the audit script from Example 2 to identify any remaining consumers of the deprecated surfaces. Add `RAISE NOTICE 'DEPRECATED'` to the legacy views.
        - *Week 5.* Parallel-run period continues; reconcile the daily output against the legacy surface; investigate every divergence. Methodology team signs off on the new regional VaR numbers.
        - *Week 6.* Drop the legacy `fact_var_region` table and the hard-coded-date views. Document the change in the architecture wiki. Schedule the audit script to run quarterly to detect recurrence.
        Critical: the deletion in week 6 is the *end* of the migration; declaring victory in week 4 — *new tables exist, dashboards work, ship it* — is the most common mode of half-finished remediation (pitfall 5).

3. **Spot the hidden anti-pattern.** The query below looks clean. Find the anti-pattern.

    ```sql
    SELECT desk_id, SUM(year_end_pnl) AS ytd_pnl
    FROM fact_pnl
    WHERE business_date BETWEEN DATE '2025-12-31' AND DATE '2026-12-31'
    GROUP BY desk_id;
    ```

    ??? note "Solution"
        Two anti-patterns hide here. First, **AP4 in disguise**: the hard-coded year-end dates `2025-12-31` and `2026-12-31` will silently roll into the wrong period when the next year begins, and `2025-12-31` is *itself* a non-trading-day in many jurisdictions (it is a Wednesday, but some venues are closed; in 2026 it falls on a Thursday with similar regional-closure risk). Second, **AP3-adjacent**: `year_end_pnl` reads like a measure that is itself an aggregate (perhaps a year-to-date stock that updates daily) being summed across days, which would double-count the year-to-date as it accrues. Both errors are the same shape — a query that looks clean because it uses obvious-looking constants and obvious-looking column names, hiding assumptions that the warehouse should make explicit.

4. **Design.** A new team wants to add a `fact_capital_legal_entity` table that pre-sums per-desk capital across desks within a legal entity. Walk through the architectural conversation you would have with them.

    ??? note "Solution"
        Open with the M12 framing: capital is non-additive across desks, so the proposed table would bake in the wrong number. Demo the wrong number alongside the right one (M20 §3.3). Offer two architectural alternatives: (a) recompute the legal-entity capital from per-desk components on demand (requires the methodology engine to be queryable at the legal-entity grain, which it usually is), or (b) the methodology engine writes the legal-entity number *independently* into the proposed table, with no SUM step in between. Either is defensible; the SUM-of-per-desk shortcut is not. Add `safe_aggregation = none` metadata to every non-additive column on the new table. Capture the agreement in an architecture decision record so the conversation does not have to be re-litigated next quarter.

5. **Operational triage.** During an audit walkthrough, the auditor finds the following in the warehouse: (a) the production DBA fixed three rows in `fact_position` last Tuesday at 2:14 a.m. with no ticket; (b) the monthly Treasury report is exported to Excel where a manual FX-translation adjustment is applied before being sent to the CFO; (c) the `dim_book` is SCD1 — when a book moved desks last quarter, prior-period reports silently re-attributed. For each, identify the operational anti-pattern from §3.9 and write the one-line remediation you would commit to in the audit response.

    ??? note "Solution"
        - (a) is the *helpful DBA hotfix*. Remediation: *every production data change is logged in the change-management system before execution, including out-of-hours; the on-call playbook is updated and circulated.*
        - (b) is the *untracked spreadsheet output*. Remediation: *introduce `fact_manual_adjustment` with reviewer, justification, and effective dates; the Treasury report is regenerated from the warehouse with the documented adjustment applied; the spreadsheet workflow is retired.*
        - (c) is *hierarchy drift without SCD2*. Remediation: *promote `dim_book` to SCD2 with a backfill of the historical attribution as it stood at each prior date; re-run the prior-quarter desk reports to confirm the SCD2 view reproduces the originally-published numbers.* All three remediations require a sign-off from a named control owner; the audit response should name the owner and the target date.

## 7. Further reading

- Kimball Group, *Dimensional Modeling Techniques and Anti-patterns*, [https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/) — the canonical source on grain rigor, conformed dimensions, and the failure modes addressed by APs 1, 3, and 5.
- Brown, W. J. et al., *AntiPatterns: Refactoring Software, Architectures, and Projects in Crisis* — the original anti-patterns book; the principles transfer directly to data engineering.
- Basel Committee on Banking Supervision, *BCBS 239: Principles for effective risk data aggregation and risk reporting*, latest version — the regulatory frame that, by negation, defines APs 1, 2, and 8 as compliance failures.
- dbt Labs, *Best Practices Guide*, [https://docs.getdbt.com/best-practices](https://docs.getdbt.com/best-practices) — the modern transformation-layer view; many of the layered-warehouse and conformance recommendations directly counter APs 3, 5, and 7.
- Fowler, M., *Refactoring: Improving the Design of Existing Code* — the code-smell vocabulary that the section-5 *common pitfalls* draws on for sequencing remediation safely.
- Industry post-mortems and supervisory enforcement actions — the OCC's enforcement archive ([https://www.occ.treas.gov/news-issuances/news-releases/](https://www.occ.treas.gov/news-issuances/news-releases/)) and the Bank of England's PRA findings publications periodically include case material on data-aggregation deficiencies; reading the public summaries is the cheapest education available on what the supervisor actually finds expensive.

## 8. Recap

You should now be able to:

- **Recognise the eight anti-patterns** by their symptoms — the regional VaR that does not match firmwide, the report that cannot be replayed, the mixed-grain SUM that doubles, the month-end batch that breaks on Sundays, the per-report xref that drifts, the vendor mark that the desk repudiates, the hard-coded scenario list, and the green-but-stale DQ dashboard.
- **Connect each anti-pattern to its earlier-module fix** — AP1 to M12 (additivity), AP2 to M13 (bitemporality), AP3 to M07 (grain rigor), AP4 to M06 (date dimension), AP5 to M18 (silver-layer conformance), AP6 to M11 (market-data hierarchy), AP7 to M10 (scenario dimension), AP8 to M15 (data quality controls).
- **Run the audit script** from Example 2 — adapted to your warehouse's dialect and naming conventions — quarterly, to detect anti-pattern recurrence before a regulator does.
- **Sequence a remediation safely** — parallel-run, backfill, consumer-by-consumer migration, deprecation warnings on the old surface, and a hard drop only after every consumer is migrated.
- **Avoid the meta-pitfalls** when fixing — never rip out a pre-aggregated table without a parallel run, never declare a bitemporal upgrade complete without a historical backfill, never consolidate xrefs without keeping the legacy aliases, and never declare victory until the old surface is gone.
- **Hold the architectural line** in design conversations — when a new team proposes pre-aggregating a non-additive measure, when a fresh report wants to inline its own xref CASE statement, when a stress-P&L pipeline wants to hard-code the current scenario set, you have the catalogue of failure modes to point at and the remediation cost to quote.
- **Treat this module as a recognition checklist, not a museum tour** — the patterns are easy to spot in retrospect; the entire purpose of this catalogue is to make them easy to spot in prospect, in your own warehouse, before someone else does.

A closing observation. The catalogue in this module is finite — eight schema-level patterns and six operational patterns — and most readers will encounter the majority of them in the first two years on a real warehouse. The catalogue is also stable; the same patterns appear in the same shapes across firms, asset classes, and warehouse technologies. A useful exercise after finishing this module is to keep a personal log of every anti-pattern you spot in the wild over the next twelve months — which one, where, who introduced it, who paid the cost, what the remediation looked like. The log becomes both a personal training artefact and, in time, the foundation for the architectural-review checklist your team will use. The patterns repeat; the lessons compound; the engineer who writes them down stops re-discovering them on each new system.

A final sequencing note for what comes next. Module 22 is the capstone — a single end-to-end exercise that integrates the engineering material (M03–M18), the regulatory frame (M19), the stakeholder craft (M20), and the anti-pattern recognition reflexes from this module into a defensible architectural choice on a realistic problem. The capstone is harder than any individual module because it requires holding all the constraints simultaneously; readers who have internalised the catalogue here will find the synthesis materially easier.

For quick reference, the catalogue collapses to the table below — the version most teams pin somewhere visible and reuse in design reviews.

| AP  | Name                              | Symptom (one line)                                       | Fix module |
| --- | --------------------------------- | -------------------------------------------------------- | ---------- |
| AP1 | Pre-aggregating non-additive      | Regional VaR ≠ recomputed firmwide VaR                   | M12        |
| AP2 | No bitemporality                  | Cannot reproduce yesterday's report as we knew it then   | M13        |
| AP3 | Mixed grains in one fact          | Naive `SUM` doubles or triples; row counts vary wildly   | M07        |
| AP4 | Hard-coded dates / TZ-naive EOD   | Month-end breaks on Sundays; cross-region disagrees      | M06        |
| AP5 | Implicit conformance              | Same counterparty, two IDs in two reports                | M18        |
| AP6 | Bypassed market-data hierarchy    | Vendor mark used where official is expected              | M11        |
| AP7 | Hard-coded scenario list          | Methodology recalibration breaks the report each quarter | M10        |
| AP8 | Stale or mis-tolerated DQ check   | Green dashboard, broken downstream report                | M15        |

The table is short on purpose. The full block in section 3 carries the *why-it-happens*, the *why-it-hurts*, and the *fix*; the table above is the recognition trigger that sends a reader back to the right block.

A practitioner habit worth forming: every architectural review opens by asking which of the eight rows the proposed design would risk introducing or perpetuating. The reviewer does not need to remember the catalogue verbatim — the table is the prompt; the discussion is the value. Teams that adopt this practice report a steady decline in remediation tickets over the following two to three quarters, and an associated increase in design-time conversations that catch the issue before it ships. Both effects compound; both are the point.

---

[← Module 20 — Working with Business](20-working-with-business.md){ .md-button } [Next: Module 22 — Capstone →](22-capstone.md){ .md-button .md-button--primary }
