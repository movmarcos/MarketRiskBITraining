# Module 20 — Working with the Business

!!! abstract "Module Goal"
    Technical excellence is necessary but insufficient. The most expensive market-risk-data mistakes are not bugs in pipelines — they are perfectly correct deliveries of the wrong thing, built from briefs nobody pushed back on. Module 20 is the soft-skills module written for engineers: it covers the daily reality of translating vague business asks into precise data specs, pushing back on technically wrong requests without breaking the relationship, communicating non-additivity to a non-quant, and surfacing data-quality uncertainty in language that informs without eroding trust. Phase 6 of the curriculum has framed the warehouse against its regulators (M19); this module frames it against its consumers, the people who actually pick up the phone when a number looks off.

---

## 1. Learning objectives

By the end of this module, you should be able to:

- **Map** a stakeholder ask to a precise data spec — naming the grain, the measures, the dimensions, and the freshness — before writing a line of SQL.
- **Push back** on technically wrong requests (most often `SUM(VaR)`) without damaging the working relationship, by demonstrating the wrong number alongside the right one rather than by lecturing.
- **Communicate** non-additivity to a non-quant in business terms — diversification benefit, not sub-additivity — and pre-commit a stance the dashboard can defend.
- **Surface** data-quality uncertainty in the always-paired form *number + caveat + does-the-caveat-change-the-conclusion*, calibrated to the audience (regulator, trader, manager).
- **Distinguish** the situations to absorb, the situations to negotiate, and the situations to escalate, so that scarce stakeholder political capital is spent on the conversations that matter.
- **Operate** on the daily / weekly / monthly / quarterly / annual cadence of a market-risk data team, recognising the rituals each cadence creates and the credibility each ritual earns or burns.

## 2. Why this matters

The first nineteen modules of this curriculum taught the *engineering* of the market-risk warehouse — the trade lifecycle, the dimensional model, the risk measures, the bitemporal layer, the lineage scaffolding, the regulatory frame. Module 20 teaches the *interface* between that warehouse and the people who consume its outputs. The warehouse is not a closed system that answers its own questions; every fact table exists to serve a stakeholder request, and every stakeholder request arrives in natural language that has to be decoded before any code is written. The decoding is where most of the value — and most of the failure — lives.

The empirical pattern across the industry is that the *most expensive* market-risk-data mistakes are rarely engineering bugs. They are the briefs nobody clarified, the requests nobody pushed back on, the dashboards built exactly to spec where the spec was wrong. A team that builds a beautiful firmwide-VaR tile by writing `SUM(var)` over the desk-level fact has shipped, on time, a number that lies in the friendly direction by 30–40% — and the consumers will use it, trust it, and only discover the problem when a regulator or an internal-audit reviewer asks why the firmwide VaR on the dashboard does not match the firmwide VaR in the FRTB submission. The fix at that point is years of credibility erosion, not a code change. The discipline that prevents it is conversational, not technical: a five-minute conversation at brief time would have caught it; no amount of engineering rigour after the fact will undo the trust loss.

The practitioner consequence — and the framing for the rest of this module — is that the BI engineer in market risk is *not* a SQL-writing service desk. The job is to translate, push back, and educate. The team that absorbs this framing operates as a trusted advisor to the front office, the methodology team, finance, and the regulators; the team that does not operates as a ticket queue and is treated accordingly. The arc from one to the other is years of small daily choices — clarify before you build, demo the wrong number alongside the right one, never ship a caveat-free number that has a caveat, never use the word *just* without checking what hides underneath it. This module is the catalogue of those choices.

## 3. Core concepts

A reading note. Section 3 walks the stakeholder-facing craft in eight sub-sections: the deeper stakeholder map (3.1), the four-question framework for translating asks into specs (3.2), how to push back on a "just sum it" request (3.3), how to communicate non-additivity (3.4), how to surface DQ uncertainty without losing trust (3.5), the cadence and rhythm of the team's interactions (3.6), the trusted-advisor arc over a multi-year horizon (3.7), and the absorb-vs-negotiate-vs-escalate triage (3.8). The load-bearing material for a first read is 3.1, 3.2, and 3.3 — the day-to-day mechanics; the longer-arc material in 3.7 is for the quiet re-read at the end of the first year on the team.

### 3.1 The stakeholder map for the risk-data team

Module 02 introduced the org chart of a securities firm at altitude — three lines of defence, FO / MO / BO, the position of risk and finance in the structure. Module 20 narrows the lens to the stakeholders who *actually call the data team* on a given week, with enough specificity to brief a new joiner on what each one cares about, asks for, actually needs, and how they want the answer delivered. The map below is the working version most teams converge on; the labels vary by firm, the dynamic does not.

**Traders.** A trader cares about their book's P&L, their book's risk relative to limits, and the cost of any hedge they are about to put on.

They ask for ad-hoc one-liners — "show me my DV01 by tenor right now," "what's my vega ladder against yesterday's close" — and they want the answer in seconds, not hours.

What they actually need is usually narrower than the ask: when a trader says "show me my VaR" they typically mean "tell me whether I am close to my limit so I can decide whether to put on the next clip." The right delivery is a desk-level dashboard tile or a chat-bot answer, not a multi-page report.

The relationship dynamic is *tactical and impatient* — a trader who pings you at 09:32 wants an answer by 09:34; if you cannot answer, say so immediately and follow up later, do not go silent. Escalation is informal and bilateral; the trader will tell their desk head if the data team is consistently slow, and the desk head's complaint reaches the data team's management within hours.

**Risk managers.** A risk manager cares about the desk's exposure to the risk factors the firm has decided to monitor — IR delta by tenor, credit spread by issuer bucket, equity vega by index, FX delta by currency pair — plus the limit utilisations and any breaches.

They ask for the daily Greek pack and the daily limit pack at fixed times, plus ad-hoc deep-dives when something moves.

What they actually need is the *anomaly story* alongside the numbers — "VaR is up 18% day-on-day, driven by the EUR 10y point" reads better than the bare number. The right delivery is a structured daily PDF or interactive dashboard with consistent layout day after day; risk managers are pattern-matchers and inconsistent layout actively undermines them.

The relationship is *recurring and structured* — the same conversations on the same cadence with the same people. Escalation runs through the head of risk to the CRO; it is rare and consequential when it happens.

**Desk heads.** A desk head cares about their *aggregate* P&L and risk across the books in their patch, plus the high-grade summary of any individual book that is in trouble.

They ask for the EOD risk pack, the monthly performance review, and ad-hoc questions that arrive in person or by phone — short, urgent, often political.

What they actually need is the *one-line answer* at the top, with the supporting detail accessible if they choose to drill in but not blocking the headline. The right delivery is the management-summary page of a dashboard, with the second page available on click.

The relationship is *senior and time-poor* — desk heads do not read long emails and do not appreciate technical hedging; if the answer is "VaR is up because of the EUR 10y", say that, then offer the detail. Escalation runs upward to the head of trading and, in formal moments, the CEO.

**Market-risk methodology.** The methodology team owns the models — the VaR engine, the ES engine, the stress framework, the FRTB IMA approval.

They care about model performance against the supervisory tests (backtesting exceptions, PLA test outcomes, NMRF stability) and the integrity of the inputs the models consume.

They ask for diagnostic data — clean P&L vs hypothetical P&L for PLA, the per-risk-factor inventory for NMRF, the model-version timeline.

What they actually need is *data they can defend to the supervisor*, with full lineage and reproducibility. The right delivery is a structured analytical workspace with raw access to the warehouse plus reproducible notebooks; methodology is the most data-fluent stakeholder and they will write their own SQL given the right access.

The relationship is *technical, collaborative, and high-trust* — methodology is the data team's natural ally inside the second line, and a working partnership with them pays years of dividends.

**Finance / Product Control.** Finance owns the official P&L and the regulatory capital number; Product Control owns the daily P&L reconciliation between FO systems and the official ledger.

They care about reconciliation accuracy, the audit trail, and the alignment of risk measures with the accounting basis.

They ask for daily reconciliation reports, monthly capital roll-forwards, and ad-hoc questions when a reconciliation breaks.

What they actually need is *the same number on both sides plus an explanation of any gap*, with a defensible audit trail behind every adjustment. The right delivery is a reconciliation report with a structured exception list.

The relationship is *formal and process-oriented* — finance lives by month-end close and is unforgiving of late or wrong inputs at that moment. Escalation runs through the head of product control to the CFO; the trigger is usually a reconciliation break that affects the official P&L.

**Treasury.** Treasury owns the firm's funding, liquidity, and FX positions.

They care about the firm's aggregate exposure to liquidity stress, the FX position arising from operations across currencies, and the contribution of trading-book activity to firm-wide liquidity needs.

They ask for liquidity-stress contributions, FX-position rollups, and the trading-book's funding-cost attribution.

What they actually need is the *firm-level view* of items the trading-book data team naturally sees at desk level. The right delivery is a periodic report with a clearly marked grain and aggregation method.

The relationship is *peripheral but high-stakes* — treasury is not in the daily loop but the deliverables they consume go to the ALCO and to the CFO. Escalation is rare and runs through the head of treasury.

**Compliance.** Compliance cares about adherence to regulations the firm is subject to — MAR, MiFID II, conduct rules, the senior-managers regime.

From the market-risk warehouse they consume trade data and position data for surveillance, plus the audit trail showing who changed what and when.

They ask for surveillance feeds, ad-hoc lookups when an alert fires, and the documentation supporting any change to the regulatory deliverables.

What they actually need is *evidence* they can show the supervisor, not just data. The right delivery is a structured feed plus a documented control framework.

The relationship is *formal, low-volume, high-consequence* — compliance is rarely in the picture but when they appear the conversation is serious. Escalation runs through the chief compliance officer.

**Internal audit.** Audit cares about the firm's controls and the evidence those controls have been operating effectively.

From the market-risk data team they want lineage (where does the number come from), controls (who reviewed it, who approved it), and evidence (the change tickets, the test results, the reconciliation outputs).

They ask for documented control descriptions, sample testing of recent submissions, and walkthroughs of the data flow.

What they actually need is *testable assertions* — the data team should be able to point at a control and demonstrate it operating, not just describe it. The right delivery is a structured audit pack with documentation, sample evidence, and links to the supporting systems.

The relationship is *periodic and adversarial-by-design* — audit's job is independent challenge, and a healthy data team welcomes the challenge rather than treating it as an attack. Escalation runs through the head of audit to the audit committee of the board.

**Regulators.** The supervisor cares about the firm's compliance with the prudential framework (Basel III as amended by FRTB, BCBS 239, the macro stress regimes covered in M19) and the integrity of the submissions on which the supervisory judgement rests.

They ask for the regular submissions on cadence (daily backtesting, monthly capital, quarterly Pillar 3, annual stress), the ad-hoc thematic data calls, and the on-site review packs when an inspection is scheduled.

What they actually need is *defensible numbers, on time, with the lineage they can audit*. The right delivery is the formal submission template plus the supporting evidence pack.

The relationship is *mediated* — the data team rarely talks to the supervisor directly; the regulatory-affairs function holds the relationship and the data team contributes operationally to it. Escalation is the relationship itself; an operational failure surfaces to the supervisor through the regulatory-affairs function.

A practitioner observation on the *what-they-ask-versus-what-they-need* gap. Across every stakeholder above, the gap is real and consequential. Traders ask for "VaR" and need "am I near the limit"; risk managers ask for the Greek pack and need the anomaly story; desk heads ask for the EOD pack and need the headline; methodology asks for raw data and needs reproducibility; finance asks for reconciliations and needs the gap explained; treasury asks for an FX rollup and needs the firm-level grain; compliance asks for a feed and needs evidence; audit asks for a walkthrough and needs testable assertions; the supervisor asks for a submission and needs defensibility. The data team that consistently delivers what was *needed* — not just what was *asked* — operates as a trusted advisor; the team that consistently delivers what was asked, exactly, operates as a service desk. The difference compounds over years.

A second practitioner observation on the *political weight* of each stakeholder relative to the data team. Traders are individually low-weight (one trader's complaint is rarely organisationally consequential) but aggregate to high-weight (a desk's worth of unhappy traders becomes a desk-head conversation that becomes a head-of-trading conversation). Risk managers are medium-weight individually and high-weight aggregated; desk heads are individually high-weight; the head of risk and the head of trading are top-of-the-house weight. Methodology is medium-weight day-to-day and very high-weight when the supervisor calls; finance is medium-weight day-to-day and very high-weight at month-end. Treasury, compliance, audit, and the regulator are low-frequency and very high-consequence. The political-weight map matters because the team's response time, depth of work, and willingness to push back should be calibrated to the weight; treating every request identically — same response time, same depth — is both unsustainable and politically tone-deaf.

A third observation on the *consumer maturity gradient*. The stakeholders above span a wide range of data fluency. Methodology will read and write SQL natively; finance will read schemas; compliance and audit will not, but they understand evidence and controls; traders will not, and do not need to; the regulator will not, but they will read the documentation. The data team's communication has to adjust to where the consumer sits on this gradient. A SQL snippet sent to the head of trading is a category error; a chart-only summary sent to methodology under-serves them. Calibrating the artefact to the audience is a craft skill that separates the teams that are pleasant to work with from the teams that are merely correct.

A reference table compressing the above for a quick reread:

| Stakeholder              | Primary KPI                          | Typical ask                                | What they actually need                       | Delivery                          | Cadence            |
| ------------------------ | ------------------------------------ | ------------------------------------------ | --------------------------------------------- | --------------------------------- | ------------------ |
| Trader                   | Book P&L, limit headroom             | Ad-hoc one-liner                           | "Am I near my limit"                          | Dashboard tile / chat-bot         | Intraday, seconds  |
| Risk Manager             | Desk Greek pack, limit utilisation   | Daily Greek pack + ad-hoc deep-dive        | Anomaly story alongside numbers               | Structured daily PDF / dashboard  | Daily, fixed time  |
| Desk Head                | Aggregate P&L and risk               | EOD pack, monthly review                   | One-line headline with detail on click        | Management-summary page           | Daily / monthly    |
| Methodology              | Model test outcomes (PLA, BT, NMRF)  | Diagnostic data, raw access                | Defensible inputs with full lineage           | Analytical workspace + notebooks  | Daily / weekly     |
| Finance / PC             | Reconciliation accuracy              | Daily recon, monthly roll-forward          | Same number on both sides plus gap story      | Reconciliation report             | Daily / month-end  |
| Treasury                 | Firm funding and FX                  | Liquidity contribution, FX rollup          | Firm-level view of desk-level data            | Periodic report                   | Weekly / monthly   |
| Compliance               | Regulatory adherence, surveillance   | Surveillance feed, alert lookup            | Evidence the supervisor can review            | Structured feed + control docs    | Continuous         |
| Internal Audit           | Control effectiveness                | Control walk-through, sample testing       | Testable assertions, not descriptions         | Audit pack + documentation        | Periodic           |
| Regulator (via Reg Affairs) | Prudential compliance              | Formal submissions, thematic calls         | Defensible numbers on time with lineage       | Submission template + evidence    | Daily to annual    |

### 3.2 Translating business asks into data specs — the four-question framework

Every stakeholder request arrives as natural language, and natural language is structurally vague about exactly the things SQL needs to be precise about. The translation is a four-question conversation the data engineer learns to run in their head — and increasingly with the requester directly — on every brief. The four questions are GRAIN, MEASURES, DIMENSIONS, FRESHNESS. A brief with all four answered is a spec; a brief missing any one of them is an invitation to build the wrong thing.

**GRAIN.** *One row per WHAT?* The grain is the unique key of the requested output.

"Yesterday's exposure" might mean one row per book, one row per book × instrument, one row per trader, one row per legal entity, or one row per risk factor — and the same input fact table can produce all of those by different group-bys.

The wrong grain is silently wrong: the dashboard looks plausible but the numbers do not roll up to the right total, or they roll up to the same total but at a level that hides the actionable breakdown.

The fix is to ask the grain question first, before any other clarification. Most stakeholders cannot answer the grain question abstractly — *they* think in terms of "I need exposure" — but they can answer it concretely if you offer them options: "do you want one row per book, or one row per book per business date?"

**MEASURES.** *Which numbers?* Almost every market-risk noun is overloaded.

"Exposure" might mean notional, gross MV, net MV, DV01, VaR, ES, PFE, EAD — and the choice changes the answer by orders of magnitude.

"P&L" might mean clean, dirty, hypothetical, actual, or risk-theoretical — and PLA test discipline (M14) depends on never confusing them.

"Risk" is even worse; the word means whatever the speaker assumes you assume.

The discipline is to convert every noun to a column on a fact table before you accept the brief — and to read the result back to the requester in those terms so they can correct you before you build.

**DIMENSIONS.** *Sliced by WHAT?* Once the grain and measures are fixed, the dimensions are the breakdowns the consumer wants to see — by desk, by region, by currency, by tenor bucket, by counterparty hierarchy.

Two pitfalls recur. The first is *missing a dimension* the consumer wanted but did not name; the dashboard ships and the first feedback is "great, but can you also break it out by counterparty?" — a rebuild that a five-minute clarifying conversation would have prevented.

The second is *as-of confusion in a hierarchical dimension*: "by desk" might mean the desk hierarchy as it stands today (so a position booked under last year's desk-name is rolled up under this year's desk) or as-of the historical date (so the position rolls up under the desk-name in force at the time).

The bitemporal discipline of M13 makes both queryable; the brief has to specify which the consumer wants.

**FRESHNESS.** *How old can the data be?* The freshness question maps to the SLO the dashboard or report has to meet.

Intraday for a trader (seconds to minutes), end-of-prior-day for a risk manager (the official EOD), end-of-prior-month for finance (close cycle), the regulatory submission cadence for the supervisor.

The freshness budget determines which upstream pipelines have to run before the deliverable can be produced, and a brief that asks for "today's number" without specifying freshness can mean any of "right now," "as of this morning's official EOD," or "as of the most recent batch run, whenever that was."

Naming the freshness explicitly forces the conversation about what is *actually* available — and in many cases the consumer will accept a less-fresh number once they realise the cost of the fresher one.

A brief that has answered all four is a *spec*. The spec should be written down — in a ticket, an email, a Confluence page, whatever the team's tooling supports — and shared back to the requester for sign-off *before* implementation begins. The cost of writing the spec down is a few minutes; the value is the elimination of the three most common failure modes (build-the-wrong-thing, build-the-right-thing-the-wrong-way, requester-changes-mind-mid-build). The spec template the team uses is less important than the discipline of producing one for every non-trivial brief.

!!! info "The spec template"
    A useful minimal spec template — copy and adapt — has six fields: GRAIN (one row per …), MEASURES (which columns from which fact table, with their units), DIMENSIONS (which slicers, sourced from which dimensions, with the as-of treatment named), FRESHNESS (the SLO and the upstream dependencies), SOURCE (the fact and dim tables, with the lineage to upstream systems), and DELIVERY (dashboard / report / API / file, with the destination and the recipients). Six fields, fits on one screen, defensible to the requester and to a reviewer.

A practitioner observation on *the order of the four questions*. The order GRAIN → MEASURES → DIMENSIONS → FRESHNESS is not arbitrary; each subsequent question is constrained by the prior answers. The grain determines which fact table is relevant (and therefore which measures are even available); the measures determine which dimensions can legitimately slice them (a non-additive measure cannot be sliced by a dimension that requires aggregation across its members); the dimensions in turn constrain which freshness levels are achievable (a dimension that requires SCD2-historical lookup may be slower to refresh than one that uses current-state). Asking the questions out of order — starting with freshness, say — produces conversations that go in circles. The natural pedagogy is to teach the four-question framework as a *sequence*, not as a checklist.

A second observation on *the requester's role* in spec authorship. The four-question framework is the *engineer's* mental model; from the requester's perspective the conversation should feel collaborative rather than interrogatory. Two phrasings of the same clarifying question land very differently with a senior consumer. *"What's the grain?"* is jargon and reads as gatekeeping; *"do you want one row per book per day, or one row per book averaged over the period?"* is the same question phrased as an offered choice, and lands as service. Translating the four questions into requester-friendly language is a craft skill the team's juniors learn from their seniors; the underlying framework is the same, the surface is calibrated to the audience.

A third observation on *spec reuse*. A spec that has been written down once is reusable forever — the same brief from a different requester three months later is answered in minutes, not hours, by retrieving the spec and adjusting the parameters. Teams that maintain a structured catalogue of past specs (in the ticketing system, in a Confluence space, in a git repository) compound their throughput year-over-year; teams that re-derive every spec from scratch on every brief stay at the same throughput indefinitely. The catalogue is not glamorous engineering work but it is one of the highest-leverage investments a team can make.

### 3.3 How to push back on a "just sum it" request

The single most common technically wrong request the market-risk data team receives is some variant of "please add `SUM(var)` to the dashboard." The variants — sum the desk-level VaRs to get a firmwide VaR, sum the daily VaRs to get a monthly VaR, sum the regional ESs to get a global ES — are all the same mistake (Module 12's central theorem: VaR and ES are not additive; the sum lies in the friendly direction by the diversification benefit, which can be tens of millions of dollars at a typical bank scale). The technically correct response is "no." The *operationally* correct response is more nuanced.

The first rule of pushing back is *do not say "you're wrong."*

The requester has a real business need (they want a firmwide VaR view; they want a monthly summary; they want a global rollup); the request is a *proposed solution* to that need, and the proposal happens to be technically wrong.

Treating the proposal as the need will turn the conversation into a debate about who is right; treating the underlying need as the need turns the conversation into a collaborative search for a better solution.

The framing is "I want to make sure we get this right — can I show you what happens if we sum?" rather than "you can't sum VaR."

The second rule is *demo the wrong number alongside the right number.*

A side-by-side calculation — the `SUM(var)` answer and the recomputed-firmwide-VaR answer — beats any verbal explanation.

A trader or desk head looking at \$185M (sum-of-desk-VaRs) next to \$120M (recomputed firmwide VaR) immediately understands that the gap is real and material; they do not need the formal definition of sub-additivity to see that the dashboard answer would have over-stated the firm's position by 35%.

The conversation pivots from "is the data engineer being pedantic" to "wait, which number is right" — which is exactly where you want it.

The third rule is *explain in business terms, not in math.*

Module 12's vocabulary translates as follows: *sub-additivity* becomes *diversification benefit*; *coherent risk measure* becomes *the right kind of risk number*; *convex combination* does not get said at all.

The right framing is "the firm holds positions that partly offset each other — when the EM rates desk loses on a bond rally, the EM credit desk often gains on the same move. The firmwide VaR captures that offset; the sum of desk VaRs does not. The gap is real money — about \$65M on a typical day — and reporting the sum overstates the firm's risk by that amount."

A desk head does not need anything more than that; a methodology partner does not need anything less.

The fourth rule is *offer the alternative path.*

Pushback that ends in "and so we can't give you what you asked for" is unhelpful; pushback that ends in "and so the right way to give you the firmwide VaR view is X — which takes Y longer / costs Z more / is available on cadence W" is collaborative.

Three alternatives recur:

(a) compute the firmwide VaR correctly — a recomputation with a full historical-VaR run on the firm-level position (correct, slower, the right answer for the official report);

(b) compute the sum-of-desk-VaRs and the recomputed firmwide VaR side-by-side, with the gap labelled as the diversification benefit (correct, fast, more informative than either number alone, the right answer for a management dashboard);

(c) sum a measure that *is* additive and answers the underlying question — sum the per-scenario stress P&Ls to get a firmwide scenario impact (correct, fast, a different question, the right answer when the underlying need was actually about scenarios rather than VaR).

Picking the alternative is a conversation; the data team should arrive with all three on the table.

The fifth rule is *document the decision.* Once the conversation has converged on one of the alternatives, write the decision down — in the spec, in a ticket comment, in a follow-up email — and circulate it to the requester and any other stakeholders the decision affects. The reason is not bureaucracy; it is that the same conversation will recur in three months with a different desk head who has not been part of the original decision, and being able to point to "we decided this in March because of [the diversification benefit issue]; here is the rationale" is much faster than re-running the conversation from scratch every time. It also creates the *pre-commit* the next sub-section discusses.

A practitioner observation on the *timing of the push-back*. The push-back must happen *before* the build starts, not in the middle of it and not after delivery. A push-back delivered after the requester has been told to expect the wrong number on Friday lands as flip-flopping; a push-back delivered after the wrong number is already on the dashboard lands as embarrassment-management. The discipline is to surface the technical objection at the brief stage, in writing, with the alternatives ready. The five rules above only work if the conversation happens at the right moment in the lifecycle; the same content delivered at the wrong moment fails.

A second observation on the *political risk* of pushing back to a senior leader. The "just sum the VaR" example in §4 has the request coming from the head of trading; pushing back is more delicate when the requester is senior than when they are a peer. The mitigations are straightforward but worth stating. First, copy the head of risk on the response so the conversation has a senior 2nd-line presence — the methodology and risk-measurement question is theirs, not the data team's, and including them appropriately distributes the technical authority. Second, frame the push-back in the requester's interest — "I want to make sure the board sees a defensible number" rather than "you can't have what you asked for." Third, deliver the alternatives and the rationale in the same message as the objection — never push back without simultaneously offering the path forward. Fourth, accept the requester's final decision: if after the full conversation the requester still wants `SUM(var)`, escalate through the data team's management chain rather than refuse unilaterally. The push-back is a service, not a veto.

A third observation on *the cumulative effect of consistent push-backs*. A team that pushes back consistently and well becomes the team consumers turn to for advice; a team that ships whatever is asked becomes the team consumers stop trusting on technical questions. The first decade of a team's existence is the period in which this reputation gets set; the choices made in years one and two compound for years three through ten. The push-back is not a one-off skill; it is a long-game posture, and the daily practice of running the five rules in §3.3 is what builds the reputation over time.

### 3.3a Dialogue patterns — five lines that work

Beyond the five rules of §3.3, a small number of stock phrasings recur often enough to be worth memorising. They are not scripts; they are *patterns* that the engineer adapts to the moment. The patterns work because they consistently move the conversation in the right direction without burning the relationship.

**"Let me make sure I'm building the right thing."** Used at brief time, before any clarification questions. Frames the upcoming questions as service to the requester rather than as gatekeeping. Almost universally well-received.

**"Quick context before I build."** Used at the moment of pushing back on a technically wrong request. Signals that the engineer is going to deliver, but with caveats the requester should hear first. Distinguishes the message from "I refuse," which is the failure mode.

**"Two paths forward."** Used to offer alternatives after surfacing the issue. The phrase commits the engineer to actually offering paths, not just objections. Consumers find it dramatically more collaborative than the alternative phrasings ("the only way to do this is X").

**"My recommendation is X — happy to discuss."** Used to close the alternative-offering message. Asserts a position (the team has expertise and is using it) while explicitly inviting the requester to overrule. Almost always lands well; flat assertions ("we will do X") land less well.

**"Confirming the spec before I build."** Used to close the brief-clarification phase and start the build. Creates the written record of the spec, gives the requester one last chance to amend, and protects both sides if the requirements change mid-build.

These five patterns cover perhaps 80% of the day-to-day stakeholder interactions a market-risk data engineer has. The remainder benefit from the same posture — collaborative, service-framed, position-asserting, written-trace-leaving — even when the exact phrasing varies. New joiners pick these up by exposure; senior engineers who have not consciously catalogued them often find that the patterns are already in their vocabulary, which is why they work.

### 3.4 Communicating non-additivity to a non-quant

The pushback mechanics in 3.3 work in the moment; the longer game is to build a shared understanding across the consuming community so the conversation does not have to be re-run with every new requester. The communicating-non-additivity craft is the slow work of teaching the firm's vocabulary, one stakeholder at a time, until "VaR doesn't sum" is common knowledge and the dashboards' design can rely on it.

**Use real examples, not abstract math.**

A non-quant audience will not absorb sub-additivity from the formal statement; they will absorb it from a concrete numerical example with familiar names.

The example that lands consistently is something like: "the EM rates desk's VaR is \$30M; the EM credit desk's VaR is \$25M; the recomputed VaR for the two desks combined is \$42M. The sum is \$55M; the recomputed number is \$42M; the difference is \$13M of diversification benefit."

The follow-up: "The diversification benefit is real — it is the empirical correlation between the two desks' P&Ls in the historical-VaR window — but it depends on that correlation staying stable. In 2008 the correlation went to one and the benefit collapsed; the firmwide VaR jumped to the sum-of-desk number overnight. That is the risk the dashboard is meant to surface, and that is why we recompute rather than sum."

The example takes thirty seconds; the formal axioms would take five minutes and not stick.

**Use diversification-benefit language, not sub-additivity language.**

*Diversification benefit* is a phrase that traders, desk heads, methodology, finance, and regulators all use natively; *sub-additivity* is a phrase only methodology uses.

Phrasing the same fact in business vocabulary lets the conversation continue; phrasing it in technical vocabulary stops it.

The same applies to *coherent risk measure* (use *the right kind of risk number*), *convex combination* (do not use), *spectral measure* (do not use).

The vocabulary discipline is not anti-intellectual; it is audience-aware. Talking down to methodology is patronising; talking up to a desk head is alienating. Match the vocabulary to the listener.

**Frame the trade-off as a choice, not a constraint.**

"VaR doesn't sum" sounds like a constraint the data team is imposing; "we have a choice between two firmwide VaR numbers — the sum of desk VaRs (fast, lies by ~30%) and the recomputed VaR (correct, slower) — and we recommend the recomputed one for [these reasons]" sounds like a choice the team is offering.

The reframing is small but consequential; consumers respond very differently to "you can't have what you asked for" than to "here are the options, here is what we recommend."

The team that consistently frames its work as choices is the team that gets brought into the design conversation; the team that frames it as constraints is the team that gets briefed and ignored.

**Pre-commit a stance.** The most powerful version of this craft is to pre-commit, at design time and in writing, the stance the team will take on every recurring non-additivity question. "The firmwide VaR tile on the management dashboard is *always* the recomputed number, not the sum of desk-level numbers — see decision-record 2026-03 for the rationale" lets every future "can you just sum?" conversation be deflected to the decision record rather than re-litigated. The pre-commit does two things: it removes the team's daily decision burden, and it makes the team's stance defensible to a sceptical audience because the stance was decided once, with full review, rather than ad-hoc per request. The decision records become an institutional asset over years; the team that has fifty of them at the end of year three operates with much less friction than the team that re-decides every question every time.

A practitioner observation on *the visualization of non-additivity in dashboards*. Beyond the verbal communication, the dashboard's visual design itself can teach non-additivity. A firmwide-VaR tile that shows the recomputed number as the primary value and the sum-of-desk-VaRs in a smaller subscript with the diversification benefit labelled inline (e.g., "\$120M (\$185M sum, \$65M benefit)") gives the consumer the comparison every time they look at the tile, without requiring them to remember the methodology lecture. Over months, the visual repetition does the teaching that no single conversation could; consumers begin to read the gap between the two numbers as a feature of the dashboard rather than as a footnote. Dashboard designers who internalise this pattern build interfaces that *educate* their consumers; designers who do not build interfaces that have to be explained.

A second observation on *the methodology team as ally*. The most powerful pre-commit comes when methodology is a co-signatory of the decision record. A stance signed by the data team alone reads as a technical preference; the same stance co-signed by the methodology team reads as the firm's official position on the question. Methodology partners are typically delighted to co-sign — the alternative is being asked the same question themselves repeatedly — and the joint signature short-circuits future debates because the requester would have to overrule both teams to push back. The discipline is to bring methodology into the decision-record drafting process from the start, not to draft alone and ask for sign-off after the fact.

### 3.5 Surfacing DQ uncertainty without losing trust

Every market-risk data team produces some bad numbers some of the time. The market-data feed for an exotic curve hiccups; a counterparty's reference data is missing; a position fails to enrich because the instrument was set up on the wrong calendar. M15 covered the data-quality framework that detects these conditions; this sub-section covers what to *say* about them when they affect a deliverable in front of a consumer. The discipline is precise enough to be worth stating as a rule: *every data-quality caveat must be paired with the number it qualifies and with a statement of whether the caveat changes the conclusion.*

The wrong way to communicate a DQ issue is the unstructured apology — "the data might be wrong, sorry" — that says everything except what the consumer needs to know. The consumer is left with no number, no idea of how wrong, no idea of whether the headline conclusion has changed. The implicit message is *we don't know what we're doing*, and the consumer's response is to either over-react (ignore the deliverable entirely) or under-react (use it anyway, because no concrete alternative was offered). Either response erodes trust; both are entirely the data team's fault.

The right way is the *number + caveat + impact* triple. "The desk-level VaR for the EM rates book is \$32M as of 2026-05-08. The DQ flag for the EUR 10y point is yellow because [reason]; the impact on the headline VaR is bounded by ±\$2M based on a re-run with a fallback curve, so the headline conclusion (VaR is within limit) is unchanged." This format gives the consumer a concrete number, full transparency about the issue, and the actionable answer (does this change what I should do?) up front. The consumer can act with confidence; the data team has demonstrated competence rather than panic; the trust is preserved or even strengthened.

The severity language must match the audience. To a regulator, the framing is formal and conservative — "a yellow data-quality flag was raised on the EUR 10y curve point on 2026-05-08; the bounded impact on the FRTB IMA capital number was estimated at ±\$0.4M against a headline of \$240M; the impact does not move the headline outside the supervisor-relevant materiality threshold and the underlying issue has been remediated; full reconciliation evidence is attached." To a trader, the framing is brief and operational — "EUR 10y is a bit dodgy this morning, your VaR could be off by \$2M either way, you're still well under limit, will fix by EOD." To a desk head, the framing is in between — "VaR pack came out as normal; one curve point had a DQ yellow but the impact was within \$2M and didn't change anyone's limit position. We've remediated."

A second discipline worth stating: *never let silence read as confidence*. When a DQ issue exists and the data team does not surface it, the consumers reasonably assume the numbers are clean — and the eventual discovery (often by a third party — finance, methodology, audit) is much worse than a proactive surfacing would have been. The rule is to surface every DQ event that crosses a defined materiality threshold, in the same channel and format every time, regardless of whether anyone has asked. The consumers learn the channel and trust the data team's voice on it; an issue surfaced through the team's own channel is a sign of competence; an issue discovered elsewhere is a sign of opacity.

A third discipline: *the caveat is part of the deliverable, not a separate apology*. The dashboard tile that shows the VaR should have a small DQ indicator next to it; the report that quotes the VaR should carry the caveat in the same paragraph as the number. Splitting the number from its caveat — "here is the number, and oh by the way there is a caveat in a separate email" — makes the consumer choose between them, and the consumer will choose the number. The pairing has to be physical, not just rhetorical.

A fourth discipline: *materiality thresholds, not on/off flags*. A binary "DQ green / DQ red" flag forces a false dichotomy and trains consumers to either ignore amber states or panic at any red. The richer pattern is a three-or-four-level scale (green / yellow / amber / red) with documented materiality thresholds for each — green is "no known issue," yellow is "issue identified, bounded impact below the limit-relevant threshold," amber is "issue identified, impact between thresholds, requires consumer judgement," red is "issue identified, impact above the limit-relevant threshold or unbounded." The thresholds should be co-owned with the consumers; methodology and risk management should agree the limit-relevant levels rather than have the data team choose them unilaterally. Consumers calibrated to the scale react proportionately; the trust in the data team's voice on DQ is precisely the consumer's confidence in the scale's calibration.

A fifth discipline: *track the DQ communications themselves*. Every DQ communication that goes out should be logged — what number, what caveat, what audience, what the consumer's response was. The log is invaluable for several reasons. It allows the team to audit its own communication patterns and improve them; it provides the evidence audit needs that the team is operating its DQ-surfacing controls; and it lets the team identify recurring patterns (a particular curve that goes yellow regularly is a structural issue worth investing in fixing rather than re-communicating about). Teams that treat DQ communication as ephemeral chat traffic miss all three benefits; teams that log structurally compound the value over years.

### 3.5a A practitioner taxonomy of "the data might be wrong" moments

A useful sub-taxonomy of DQ communication. Not all DQ moments are alike, and the language and channel should differ.

**Routine yellow.** A single curve point or reference-data attribute is flagged but the impact is bounded and immaterial. Communicate via the standard daily DQ rollup, in the standard format, without escalation. The consumer reads it as "team is on top of things"; missing it reads as opacity.

**Material amber.** An issue with bounded impact above the materiality threshold for a key consumer (limit-relevant for a risk manager, capital-relevant for finance). Communicate via the standard channel *plus* a direct ping to the affected consumer, with the bounded impact stated and the operational follow-up named. The direct ping is a courtesy that consumers consistently appreciate; the omission is a missed signal.

**Unbounded red.** An issue whose impact cannot be reliably estimated — a feed outage, a calculation engine failure, a reference-data corruption affecting an unknown set of positions. Communicate immediately to all affected consumers with the honest assessment ("we cannot bound the impact yet; here is what we are doing to bound it; estimate of timeline to clarity is X") and the promised update cadence. Silence in this state is the worst possible response; under-promised candour with frequent updates is the best.

**Discovered-by-third-party.** An issue surfaced not by the data team's monitoring but by a consumer or by a downstream review. Communicate with explicit acknowledgement that the team did not catch it first, with a brief honest assessment of why the monitoring missed it, and with a commitment to close the gap. The credibility cost of a discovered-by-third-party issue is real but bounded if handled well; the cost compounds if the team responds defensively.

**Historical revision.** An issue identified after the fact, requiring revision to a number that has already been published or used. Communicate via the formal channel for revisions (most teams have one for regulatory submissions; the same channel should be used for material management revisions), with the original number, the revised number, the reason, and the impact on any downstream decisions that used the original. Bitemporal discipline (M13) makes the revision queryable and defensible; the communication discipline is what makes it acceptable.

The taxonomy is not exhaustive but it covers the main categories the team encounters. Each category has its own channel, its own format, its own audience. Conflating them — using the routine-yellow channel for an unbounded red, or escalating a routine yellow as if it were an amber — degrades the calibration of every future communication. Consistency is itself a feature; consumers learn the team's vocabulary over months and react proportionately.

### 3.6 Cadence and rhythm

A market-risk data team operates on a layered cadence — daily, weekly, monthly, quarterly, annual — and each layer creates rituals that the team has to perform reliably. The reliability is itself the credibility. A team that misses a daily DQ rollup once a quarter is worse than a team that delivers a slightly less-polished rollup every single day; the consumers measure the team by the reliability of the rituals more than by the polish of any one deliverable.

| Cadence    | Ritual                                       | Audience                          | What credibility it earns or burns                       |
| ---------- | -------------------------------------------- | --------------------------------- | -------------------------------------------------------- |
| Daily      | Morning DQ rollup (pre-market)               | Risk managers, methodology, FO    | Operational reliability — the team is on top of the data |
| Daily      | EOD risk pack (post-close)                   | Risk managers, desk heads, methodology | The team's headline deliverable; missing it is visible |
| Weekly     | Data-incident review                         | Data team + methodology + risk    | Collective learning from issues; institutional memory    |
| Weekly     | Change-board for transformations             | Data team + methodology + risk    | Disciplined evolution of the warehouse                   |
| Monthly    | Stakeholder check-in (per major consumer)    | Each stakeholder bilaterally      | Pre-empts requests; surfaces dissatisfaction early       |
| Monthly    | BI tool usage review                         | Data team + management            | Tracks which dashboards are loved vs unused              |
| Quarterly  | Roadmap review with desks                    | Desk heads + heads of risk        | Aligns the team's build with the consumers' priorities   |
| Annual     | Regulatory submission rehearsal              | Regulatory affairs + methodology  | Ensures the team can perform under pressure              |

A practitioner observation on the cadence. The daily rituals are non-negotiable; they form the operational backbone of the team and any disruption is visible to the consumers within hours. The weekly and monthly rituals are the *learning loop* — the team improves its work by reviewing incidents and dashboard usage and adjusting accordingly. The quarterly and annual rituals are the *strategic loop* — the team aligns its medium-term work with the consumers' direction and rehearses for the moments of highest stakes (the annual stress submission, the regulatory inspection, the board-level reporting cycle). A team that runs all four loops well operates with substantially less drama than a team that runs only the daily; the higher loops are where the proactive work happens.

A second observation on the rituals. Each ritual creates a *forum* in which the data team can surface things that would otherwise have to be raised through ad-hoc channels. The weekly data-incident review is the natural place to flag a pattern of upstream issues; the monthly stakeholder check-in is the natural place to surface a brewing dissatisfaction; the quarterly roadmap review is the natural place to negotiate a re-prioritisation. Without the rituals, the same conversations have to be raised through email or hallway, with much higher friction and much higher chance of being missed. The discipline of running the rituals — even when there is "nothing to discuss" — preserves the channels for the moments when there is.

A third observation on the *EOD risk pack* as the team's single most visible deliverable. For most market-risk data teams, the EOD risk pack is the deliverable consumers measure them against — it goes out at a known time every day, it is read by a known audience, and any deviation (lateness, missing components, format change) is visible within minutes. The team that delivers the EOD pack reliably day after day earns a base level of credibility regardless of what else it does; the team that misses or degrades the EOD pack suffers a base level of doubt regardless of any other achievement. The asymmetry is worth internalising: EOD reliability is *table stakes*, not differentiation. The differentiation comes from the higher-loop work; the table stakes come from operational excellence on the daily ritual.

A fourth observation on the *annual regulatory submission rehearsal* as the highest-stakes ritual. The regulatory submission cycle — annual stress submission for CCAR / EBA / ACS, the periodic FRTB capital review, the BCBS 239 self-assessment — is the moment when years of accumulated warehouse discipline is tested under genuine pressure. Teams that rehearse the submission in advance (running the submission process end-to-end against a dry-run dataset, with the actual people performing the actual handoffs) discover the broken handoffs and the missing artefacts in advance, when they can be fixed. Teams that do not rehearse discover them in the live submission, with the supervisor watching. The rehearsal is the cheapest insurance the team can buy; the cost of skipping it is bounded by the cost of a supervisory finding, which is unbounded.

### 3.7 The trusted-advisor arc

The transition from *delivery team* to *trusted advisor* is the multi-year arc most data teams aspire to. The arc is not a checkbox; it is the gradual accumulation of consumer confidence across many small interactions, and it has rough phases that recur across teams and across firms.

**Year 1 — deliver what's asked, build credibility.**

The new joiner or the new team has to earn the right to be in the strategy conversations, and the right is earned by reliable delivery of the briefs as given.

The discipline is to clarify before building, build to the spec, deliver on time, surface issues proactively, and let the work speak.

Over-reaching in year 1 — pushing back too hard, suggesting alternatives the consumer has not asked for, lecturing about non-additivity — burns capital before it has been built. The right posture is *competent and curious*, not *competent and prescriptive*.

**Year 2 — anticipate, suggest alternatives.**

Once the team has demonstrated reliability, the consumers' tolerance for "let me show you another way" goes up.

The team can start to push back on requests it knows are technically wrong, suggest alternative paths, and offer proactive analyses the consumer did not ask for.

The credibility built in year 1 lets the suggestions land as *helpful* rather than as *presumptuous*; the same suggestions in year 1 would have been received differently.

The discipline shifts from pure delivery to a mix of delivery and proposal.

**Year 3 and beyond — shape the requests before they're made.**

The mature team is in the strategy conversations early — at the design phase of new desks, new products, new regulatory regimes — and the team's input shapes what the requests will eventually look like.

The team has built so much shared vocabulary with the consumers that briefs arrive substantially better-formed; the consumers ask the four questions of 3.2 themselves before sending the brief.

The team's role is now part-builder, part-advisor, part-educator; the work is qualitatively different from year 1 even though much of the daily mechanics looks the same.

A practitioner observation on the arc. The progression is not automatic — a team can stay in year-1 mode for a decade if it never builds the credibility or never takes the risk of suggesting alternatives. The progression also depends on the consumers; some communities are harder to advance with than others, and the data team's investment has to be matched on the consumer side. The arc is also reversible — a team that loses a senior leader, or that has a high-profile delivery failure, can find itself back in year-1 posture for a while. The progression is a tendency rather than a certainty; the discipline is to keep moving in the right direction.

A second observation on the *individual-versus-team* dimension of the arc. The arc applies to teams as a whole, but it also applies to individuals within teams. A new joiner — even on a year-3 team — starts in a year-1 posture, and the team has to be patient while the new joiner builds individual credibility with the consumers. A senior member moving to a new firm starts over; the credibility built at the previous firm does not transfer except to the extent that the new firm's consumers are predisposed to trust the prior reputation. The discipline is to recognise the individual arc as well as the team arc, and to onboard new joiners through deliberate exposure to consumers — pairing them with seniors on briefs, including them in the rituals, having them write the specs and the decision records — so they can build the credibility before they need it.

A third observation on *the senior leader transition* as a moment of arc disruption. When a head of trading, a CRO, or a head of methodology changes, the consumer-side relationship resets. The new leader has not been part of the years of accumulated trust; they will need to be re-onboarded onto the team's stances, the decision records, the cadence rituals. The team that has documented its work systematically can re-onboard a new senior leader in weeks; the team that has relied on personal relationships has to rebuild from year 1 with each transition. The decision records and the spec catalogue compound their value at exactly the moments of leadership change — moments which, in the financial-services industry, recur every two-to-five years on every senior seat.

### 3.8 When to escalate, when to negotiate, when to absorb

Not every difficult conversation is worth having. The team that escalates every disagreement is exhausting; the team that absorbs every request is overworked and gradually less effective. The triage between *absorb*, *negotiate*, and *escalate* is a daily judgement that the team learns to make consistently.

**Absorb.** A small request, one-off, no precedent risk — just do it.

Absorbing is the right answer when the cost of the negotiation is higher than the cost of the work, and when the request does not set a pattern that will recur and amplify.

A trader asking for a one-off pivot of yesterday's positions by counterparty: absorb. A desk head asking for a single-use chart for an investor presentation: absorb.

The absorb decision should be conscious, not default; a team that absorbs everything ends up under water.

**Negotiate.** A medium-sized request, repeatable, sets a pattern — talk it through.

The negotiation is about the spec (the four questions of 3.2), the priority (where it fits against existing work), the cadence (one-off vs ongoing), and the maintenance burden (who owns it after build).

Negotiating is the right answer when the request is plausible but the proposed solution is suboptimal, or when the request will recur and the team needs to set the right precedent.

A risk manager asking for a new daily report: negotiate the spec and the cadence. A desk head asking for an additional dashboard tile: negotiate the maintenance ownership.

**Escalate.** A request that changes a regulatory artifact, changes the official EOD, changes the bitemporal or SCD rules, or breaks a pre-committed stance — escalate.

Escalation does not mean "complain"; it means *involve the people whose decision this actually is*, because the request is bigger than the bilateral conversation.

A request to change the firmwide VaR methodology used in the FRTB IMA submission: escalate to methodology and to the head of risk.

A request to retroactively edit a bitemporal-stamped fact row: escalate to the data governance forum.

A request to deliver a number that contradicts a pre-committed stance from a decision record: escalate to the original decision-record signatories.

The triage is a skill that develops with experience. A useful internal check: *if I do this without flagging, will I regret it later?* If yes, escalate or negotiate; if no, absorb. The check fails in both directions — over-escalating is annoying, under-escalating is risky — and the team's calibration improves over years. A second useful check: *if my manager finds out about this in a different forum, will they be surprised?* If yes, surface it now; if no, you have judged the absorb-or-negotiate boundary correctly.

A practitioner observation on *the cost of over-escalation*. Teams that escalate every disagreement become known as the team that cannot resolve its own conversations; the consequence is that genuinely important escalations get less attention because they have been pre-discounted. The skill is to escalate sparingly enough that each escalation lands with appropriate weight; this requires the team to absorb and negotiate the smaller battles even when it would be easier to push them upward. Escalation is a finite resource; spend it on the conversations that matter, save it for the conversations where it is the only path forward.

A second observation on *the negotiation-versus-absorption boundary*. The boundary moves with the team's capacity. A team operating at 80% capacity can absorb requests that a team at 110% must negotiate; the same request, asked of the same team, is in different categories at different points in the year. The discipline is to recognise the team's current capacity honestly and to adjust the boundary accordingly, rather than to maintain a fixed absorb-everything posture that the team cannot sustain. Capacity-aware triage is a leadership skill at the team-lead level; engineers individually can apply the framework to their own queue.

A third observation on *the documentation of the triage decisions themselves*. Every meaningful triage decision — particularly the negotiate-or-escalate ones — should leave a trace. The trace serves two purposes. First, it makes the decision auditable later if questions arise about why the team responded the way it did. Second, it builds a corpus of decisions the team can mine for patterns: a recurring escalation on the same topic is a signal that the underlying issue needs structural fixing, not just better triage. Teams that maintain the trace operate on data; teams that do not operate on memory, which decays.

## 4. Worked examples

### Example 1 — Translation: a vague ask becomes a precise spec

It is 11:47 on a Tuesday. A risk manager pings the data team's Slack channel:

> **From: Risk Manager (EM rates desk).** Hey — can you pull me the exposure for the EM rates desk for the last 2 weeks, broken down by counterparty? Thanks!

The brief is friendly and short and entirely under-specified. The data engineer's first move is *not* to open a SQL editor; it is to run the four-question framework in their head. Each phrase in the brief decomposes into clarifying questions:

| Phrase in the brief        | Latent ambiguity                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------- |
| "exposure"                 | DV01? Notional? MV? VaR? PFE? — different by orders of magnitude                                  |
| "EM rates desk"            | The current org definition of the desk, or the as-of historical definition? Reorg six months ago. |
| "last 2 weeks"             | 10 business days or 14 calendar days? Trailing from today or from yesterday's official EOD?       |
| "broken down by counterparty" | Counterparty hierarchy (parent group) or legal-entity-level? Long counterparty list — top N?    |
| (implicit) delivery        | One-off pivot table, recurring report, dashboard tile?                                            |
| (implicit) freshness       | Today's number including intraday, or as-of yesterday's official EOD?                             |

The engineer's reply runs in two pings, polite and concrete:

> **Engineer.** Hey — happy to. A few quick clarifying questions so I send you the right thing:
>
> 1. By "exposure" do you mean DV01, notional, market value, or VaR? (They give very different numbers.)
> 2. "EM rates desk" — do you want the desk as it stands today (so positions are rolled up under the current desk-name) or as the desk was on each historical date (so the reorg from October splits the time series)?
> 3. Last 2 weeks — 10 business days ending yesterday (the official EOD basis), or 14 calendar days?
> 4. By counterparty — do you want it at the parent group level or at legal entity? And shall I cap the list to top 20 by absolute exposure, or send all?
> 5. Is this a one-off, or do you want it as a daily recurring report?

The risk manager replies in a few minutes:

> **Risk Manager.** DV01 please. Current desk definition. 10 business days ending yesterday. Parent group, top 20. One-off for now but if it's useful I'll let you know.

The engineer now writes the spec down — in the team's ticketing system, with the requester tagged — and sends a confirmation note:

> **Engineer.** Confirming the spec before I build:
>
> - **GRAIN.** One row per (parent counterparty group × business date), top 20 groups by total absolute DV01 over the window.
> - **MEASURES.** `SUM(dv01)` from `fact_sensitivity` filtered to `risk_factor.class = 'IR'`, in USD-equivalent at the position-date FX.
> - **DIMENSIONS.** Sliced by `dim_counterparty.parent_group_sk` and `dim_date.business_date`. Desk filter is `desk_sk = current_em_rates_desk_sk` — this is the current org definition, so the historical rollup uses the present-day desk membership.
> - **FRESHNESS.** As-of yesterday's official EOD; window is the 10 business days ending yesterday.
> - **SOURCE.** `fact_sensitivity` joined to `dim_counterparty` (current, not SCD2-historical), `dim_desk` (filter only), `dim_date`.
> - **DELIVERY.** CSV file in the team's shared drop folder, plus an inline pivot in this thread.
>
> If that looks right I'll build now and have it back inside the hour. If you wanted historical desk membership instead of current, please ping back — that's a different query.

The risk manager replies *looks good, go.* The engineer builds, delivers in 35 minutes, and the spec sits in the ticket system as a record. Three weeks later, a different risk manager asks "can I get the same thing for the EM credit desk?" — the spec is reusable, the build takes ten minutes, the conversation does not have to be re-run from scratch. The investment in spec-writing has paid for itself within a month.

The lesson is that the back-and-forth at the start added perhaps fifteen minutes to the engagement and saved an unbounded amount of downstream rework. A version of this conversation has to happen on every non-trivial brief; the only question is whether it happens *before* the build (cheap) or *after* (expensive). The engineer who learns to run the four-question framework in their head — and increasingly with the requester directly — turns a chaotic input pipeline into a structured one, and the team's throughput improves measurably.

### Example 2 — Push back: the "just sum the VaR" request

It is the Wednesday before the monthly board meeting. The head of trading sends an email to the data team's distribution list, copying the head of risk:

> **From: Head of Trading.** Team — I need a daily firmwide VaR number on the management dashboard by Friday. Please add `SUM(var)` over the desk-level fact and call it firmwide. The board wants to see the trend. Thanks.

The request is technically wrong (Module 12) and politically delicate (it comes from a senior leader, with a tight deadline, in writing). The wrong responses are obvious: doing it as asked (ships a number that lies in the friendly direction by 30–40%, which is much worse than not shipping anything), or refusing flatly ("no, you can't sum VaR" — burns the relationship). The right response runs the playbook from §3.3.

**Acknowledge the underlying need first.** The data engineer's reply opens by recognising that the head of trading wants a firmwide VaR view for the board; that is a legitimate need and the engineer is going to help meet it. The opening is not "we can't do that" but "happy to get you a firmwide VaR view by Friday — quick caveat that I want to flag before I build, because the simple sum would over-state the firm's risk by quite a lot."

**Demo the wrong number alongside the right number.** The engineer does a back-of-envelope calculation overnight using yesterday's official EOD data, and assembles a small table. The numbers are illustrative but anchored in the actual portfolio:

| Date       | Sum of desk VaRs (the proposed number) | Recomputed firmwide VaR (the correct number) | Diversification benefit | Gap as % of correct |
| ---------- | -------------------------------------- | -------------------------------------------- | ----------------------- | ------------------- |
| 2026-05-04 | \$185M                                 | \$120M                                       | \$65M                   | 54% over            |
| 2026-05-05 | \$192M                                 | \$124M                                       | \$68M                   | 55% over            |
| 2026-05-06 | \$178M                                 | \$118M                                       | \$60M                   | 51% over            |
| 2026-05-07 | \$181M                                 | \$121M                                       | \$60M                   | 50% over            |

The headline is direct: the proposed number would over-state the firm's VaR by roughly half on a typical day. The engineer's reply embeds the table and the framing in business vocabulary:

> **Engineer (replying to Head of Trading and Head of Risk).** Sending Friday — quick context first. Yesterday's sum-of-desk-VaRs was \$181M; the recomputed firmwide VaR was \$121M. The \$60M gap is the diversification benefit — the firm holds positions that partially offset each other (the EM rates desk and the EM credit desk often gain on the same moves, the equity book hedges some of the credit book, etc.) and the firmwide number captures the offset where the sum does not. The gap has been around \$60M-\$70M consistently over the last week. If we put `SUM(var)` on the board dashboard, the trend the board sees would be ~50% above the firm's actual risk position.
>
> Two paths forward, both deliverable by Friday:
>
> 1. **Recomputed firmwide VaR nightly.** This is the correct number — the same engine that produces the desk-level VaRs is run on the firmwide position. The number matches the FRTB IMA submission's firmwide line. Cost: an additional ~30 minutes of overnight compute, fits in the existing window. This is the option I'd recommend for the board view.
>
> 2. **Sum the per-scenario stress P&Ls instead.** If what the board wants is "what does the firm lose under [a 200bp move / equity crash / etc.]?" then per-scenario stress P&Ls *do* sum across desks — they are additive. This is a different question from VaR but often it's the question senior management is actually trying to answer. We could add this as a complementary tile.
>
> Happy to build either or both. Could you confirm direction by tomorrow morning so we can have it on the dashboard by Friday close?

The head of trading replies within an hour: *go with option 1, plus option 2 as a second tile, makes sense, thanks for catching this.* The data team builds both for Friday. The engineer adds a decision record to the team's records, summarising the conversation and the outcome:

> **Decision record 2026-05-W2-01.** Firmwide VaR on the management dashboard is the *recomputed* firmwide VaR, not `SUM(var)` over desks. Rationale: the sum over-states the firm's VaR by the diversification benefit (~50% on the May 2026 portfolio); the recomputed number matches the FRTB IMA submission. Stress P&L tile is the per-scenario sum across desks (additive, complementary view). Stakeholders: Head of Trading, Head of Risk. Re-review: annual or on portfolio composition change.

The decision record means that the next time a desk head asks "can we just sum the VaR for [X]," the conversation does not have to be re-run — the engineer can point at the record, repeat the rationale in two sentences, and re-use the stance. Over years, the records become an institutional asset; the team that has a hundred of them at the end of year three operates with much less per-request friction than the team that re-decides every question every time.

The lesson is that the push-back, done well, is *not* an obstruction; it is a service. The head of trading got a better deliverable than they asked for, the board sees a defensible number, the FRTB submission and the management dashboard now reconcile, and the team's credibility went up rather than down. The same conversation done badly — refusing flatly, or shipping the wrong number quietly — would have produced the opposite of every one of those outcomes.

## 5. Common pitfalls

!!! warning "Watch out"
    1. **Building exactly what was asked without clarifying.** The fastest way to ship a wrong number is to take the brief at face value. Every non-trivial brief deserves the four-question framework before code is written; the time spent clarifying is always less than the time spent rebuilding.
    2. **"We'll just" responses.** Every "just" hides a complexity — "we'll just sum it," "we'll just join on counterparty," "we'll just snapshot at midnight." The word *just* is a marker of unexamined assumption; train yourself to flinch when you hear it from yourself or from a stakeholder.
    3. **Over-explaining when a manager wants a one-line answer.** A desk head who asks "is the dashboard OK" wants "yes, with one caveat on the EUR curve, no impact on limits" — not a five-paragraph technical exposition. Match the level of detail to the audience; the trader wants seconds, the methodology partner wants the long version, the desk head wants the headline.
    4. **Avoiding the conversation when DQ is bad.** Silence reads as confidence — and confidence in the wrong direction. A DQ issue surfaced through the team's own channel is a sign of competence; one discovered by a third party is a sign of opacity. Surface every material issue, every time, in the same channel and format.
    5. **Promising delivery before checking dependencies.** Every deliverable depends on M11 market-data feeds, M16 lineage, M15 DQ pipelines, and the various enrichment jobs. Promising a Tuesday delivery without checking that the dependencies will hold is how you discover, on Tuesday morning, that you cannot deliver. Five minutes of dependency check before the commitment saves the relationship.
    6. **Using technical jargon when business vocabulary will do.** "Non-additive," "sub-additive," "convex," "monotonic" are all real terms but they are not the right terms for a non-quant audience. "Doesn't sum" is enough for a desk head; "diversification benefit" is enough for a senior leader; the formal vocabulary is for the methodology partner. Audience-aware vocabulary is a craft skill, not a dilution of rigour.

## 6. Exercises

1. **Rewrite the ask.** A risk manager sends the following Slack message: *"can you show me the risk for the swap book this month?"* Write the precise data spec you would build to. Cover GRAIN, MEASURES, DIMENSIONS, and FRESHNESS at minimum.

    ??? note "Solution"
        A defensible spec would clarify each of the four questions before building. *GRAIN* — one row per (book × business_date), where book is filtered to the swap-book scope; ask the risk manager to confirm whether the scope is the IRD swap book at the desk level or all swap-classified books across desks. *MEASURES* — the term *risk* is the most ambiguous noun in market risk; clarify whether the requester wants DV01 by tenor bucket, VaR (note: not summable across days — the monthly view is a time-series of daily numbers, not a sum), ES, or stress P&L under a named scenario. Pick one; if the requester actually wants several, deliver several with the relationships labelled. *DIMENSIONS* — sliced by book and by business date; ask whether they also want a tenor-bucket breakdown (for DV01) or a scenario breakdown (for stress). *FRESHNESS* — "this month" suggests as-of yesterday's official EOD with the time series running from month-start; confirm the calendar (business days or calendar days) and the as-of cut-off. The spec should be written down and shared back to the requester before any SQL is opened.

2. **Stakeholder map.** A new dashboard is being built showing book-level VaR and stress P&L for use by the head of trading. List the four other stakeholders who must be consulted before deployment, and what each cares about.

    ??? note "Solution"
        Four stakeholders beyond the head of trading should be in the loop. **(1) Risk managers** — they own the desk-level VaR pack today and the new dashboard must reconcile against it; deploying without consulting them creates a risk-vs-management number divergence. **(2) Methodology** — the VaR engine and the stress framework are theirs, and any new presentation has to use the official measures rather than re-implementing them; methodology will also be the natural escalation if a number on the new dashboard does not match the FRTB submission. **(3) Finance / Product Control** — the stress P&L numbers feed into the firm-level capital and ICAAP narrative; PC needs to know the dashboard exists so they can reconcile against it during their close cycle. **(4) Compliance** — any senior-leadership-facing dashboard is potentially a regulatory artefact (it may be referenced in a board pack or in supervisory engagement); compliance should sign off on the controls around it. A fifth stakeholder worth consulting in some firms is internal audit, who will eventually want to walk through the lineage; better to invite them to the design than to be surprised later.

3. **Communicate the caveat.** Today's official EOD has a yellow DQ flag on the EUR swap curve. The desk head is about to walk into a board meeting. Write the 2-sentence message you'd send.

    ??? note "Solution"
        The message should follow the *number + caveat + impact* pattern from §3.5, calibrated to the desk head as the audience. A defensible version: *"EOD VaR pack came out as normal; one yellow DQ flag on the EUR swap curve point at the 10y tenor — re-ran with a fallback curve and the impact on the headline desk VaR is bounded at ±\$1.5M against \$48M, so no limit position changes. Remediation in flight, full report in tomorrow's morning rollup."* Two sentences, the headline number first, the caveat with bounded impact, the actionable answer (no limit change) up front, and the operational follow-up named. The desk head can walk into the board meeting and answer "yes, today's numbers are good" with full conviction.

4. **The escalation triage.** For each of the following requests, identify whether you would absorb, negotiate, or escalate, and give the reasoning in one line.

    a. A trader asks for a one-off pivot of yesterday's positions by counterparty.
    b. A desk head asks for a new daily dashboard tile.
    c. The methodology team asks you to retroactively edit a bitemporal-stamped row.
    d. The CFO's office asks for the firmwide VaR number expressed as a sum of desk VaRs in the next quarterly Pillar 3 disclosure.

    ??? note "Solution"
        (a) **Absorb.** Small, one-off, no precedent risk; just do it, and capture the spec briefly in case it recurs. (b) **Negotiate.** Medium-sized, repeatable, sets a maintenance pattern; talk through the spec, the priority against existing work, and the ownership of the tile after build. (c) **Escalate.** Editing bitemporal rows breaks the immutability discipline of M13 — the request needs the data governance forum (and likely audit) involved; do not absorb, even if methodology is a trusted partner. (d) **Escalate firmly.** This crosses two thresholds at once — it is a regulatory artefact (Pillar 3 disclosure) and it conflicts with the additivity rules underlying the FRTB IMA submission and the firm's pre-committed stance. Escalate to the head of risk, the head of regulatory affairs, and the methodology team; do not negotiate the technical correctness of the request bilaterally with the CFO's office. Note that the right answer is almost certainly that the published number stays as the recomputed firmwide VaR, with a footnote disclosing the diversification benefit; the wrong answer is to silently accommodate.

5. **The pre-commit.** Pick one technically wrong request your team receives recurringly (a "just sum" variant, a calendar confusion, a grain confusion, etc.). Draft a decision record — three to five sentences — that pre-commits the team's stance, gives the rationale, and names the signatories.

    ??? note "Solution"
        A worked example for the recurring "sum of desk VaRs as a firmwide proxy" request: *"Decision record 2026-05-W2-01. Firmwide VaR on any management or regulatory deliverable is computed by recomputing the historical-VaR engine on the firmwide position; it is never produced as `SUM(var)` over the desk-level fact. Rationale: the sum over-states firmwide VaR by the diversification benefit, currently ~50% on the May 2026 portfolio; the recomputed number matches the FRTB IMA submission and avoids creating a management-vs-regulatory divergence. Where a fast firmwide stress view is needed, use the per-scenario sum of stress P&Ls (additive, complementary). Signatories: Head of Risk, Head of Trading, Head of Methodology, Head of Risk-Data. Re-review: annual or on material portfolio composition change."* The record is short, names the rule, gives the reason, offers the alternative path, and assigns ownership; it can be referenced in two minutes whenever the question recurs.

## 7. RACI matrix — who's accountable for which artefact

The RACI matrix below compresses the stakeholder map (§3.1) onto the warehouse's main risk-data artefacts. R = responsible (does the work); A = accountable (signs off, single owner); C = consulted (input before publication); I = informed (notified after publication). The matrix is illustrative — every firm's exact assignment varies — but the *shape* is stable across institutions.

| Artefact \ Stakeholder | Trader | Risk Manager | Desk Head | Methodology | Finance / PC | Treasury | Compliance | Audit | Regulator |
| ---------------------- | ------ | ------------ | --------- | ----------- | ------------ | -------- | ---------- | ----- | --------- |
| Daily VaR pack         | I      | A            | I         | C           | I            | —        | —          | I     | —         |
| EOD risk pack          | I      | R            | A         | C           | C            | I        | —          | I     | —         |
| Stress submission      | —      | C            | I         | A           | C            | I        | C          | C     | I         |
| FRTB SA capital        | —      | C            | I         | R           | A            | —        | C          | C     | I         |
| FRTB IMA capital       | —      | C            | I         | A           | R            | —        | C          | C     | I         |
| DQ dashboard           | I      | C            | I         | C           | I            | —        | I          | C     | —         |
| Lineage attestation    | —      | I            | —         | C           | C            | —        | C          | A     | I         |
| Pillar 3 disclosure    | —      | C            | I         | C           | A            | C        | C          | C     | I         |
| BCBS 239 evidence pack | —      | C            | —         | C           | C            | —        | C          | A     | I         |

Two reading notes on the matrix. First, the *Accountable* column is single-owner by design — every artefact has exactly one A — and the A is the person whose job is on the line if the artefact is wrong. The data team is rarely the A; the team is almost always the R for the production work, with the A sitting in methodology, finance, risk, or audit. The distinction matters because the data team's escalation paths run through the A, not through the broader consumer base. Second, the *Consulted* column drives the cadence of pre-publication review — every artefact with multiple Cs needs a structured pre-publication forum (a change board, a sign-off email, a review meeting) so the consultation happens reliably rather than ad-hoc. Teams that skip the consulted step ship faster in the short run and slower in the long run, because every uncaught issue becomes a post-publication cleanup.

## 8. Common pitfalls

(See §5 above — the warning admonition consolidates the pitfalls for this module.)

A meta-pitfall worth naming explicitly: *treating the soft-skills material as optional*.

The pattern is so consistent across teams and firms that it deserves a flag of its own. Engineers reading this module after the dense technical content of M03–M19 are sometimes tempted to skim it as the lighter material at the end of the curriculum. The pattern across the industry is the opposite — the engineers whose careers stall in market risk are rarely the ones whose SQL was wrong; they are the ones whose stakeholder communication was wrong. Investing in this module's content is a higher-leverage career move than investing in another flavour of dimensional modelling, simply because the technical content is necessary-and-replaceable while the soft-skills content is necessary-and-rare.

## 9. Further reading

- Maister, D., Galford, R. & Green, C. *The Trusted Advisor.* The canonical text on the consultant-client relationship; the framework translates almost directly to the data-team / business-stakeholder relationship in market risk. Read the *trust equation* chapter at minimum.
- Knaflic, C. N. *Storytelling with Data.* The visualization-and-communication craft for non-quant audiences. Particularly relevant for the dashboard-design and DQ-surfacing material in §3.5.
- Minto, B. *The Pyramid Principle.* Structured executive communication — headline first, supporting points second, detail third. The Minto pattern is the one most senior consumers expect from a written brief; learning it pays dividends across every audience above the desk-manager level.
- Hull, J. *Risk Management and Financial Institutions.* The chapters on the front-to-back risk function provide the institutional context this module's stakeholder map sits inside; useful as a re-grounding text.
- Bank of England, *Senior Managers and Certification Regime* documentation. The accountability framework that sits behind the RACI matrix; understanding the SMR clarifies why the *Accountable* column is single-owner and why escalation paths matter the way they do.
- Patterson, K., Grenny, J., McMillan, R. & Switzler, A. *Crucial Conversations.* The push-back craft of §3.3 generalised — how to hold high-stakes conversations under pressure without damaging the relationship. The chapter on *making it safe* is the one most directly relevant to the "just sum the VaR" pattern.

## 10. Recap

You should now be able to:

- Map a stakeholder ask onto the four-question framework — GRAIN, MEASURES, DIMENSIONS, FRESHNESS — and write a defensible spec before any SQL is written.
- Push back on a technically wrong request (the canonical "just sum the VaR" is the running example) by acknowledging the underlying need, demoing the wrong number alongside the right one, framing in business vocabulary, offering alternative paths, and documenting the decision.
- Communicate non-additivity to a non-quant audience using diversification-benefit language rather than sub-additivity language, and pre-commit a stance the team can defend across years.
- Surface DQ uncertainty in the always-paired *number + caveat + impact* form, calibrated to the audience and never delivered as silence.
- Operate on the layered cadence — daily, weekly, monthly, quarterly, annual — and recognise the rituals each layer creates and the credibility each ritual earns or burns.
- Triage between absorb / negotiate / escalate consistently, spending the team's political capital on the conversations that matter and not on the ones that do not.
- Locate the team's work on the trusted-advisor arc — year 1 deliver, year 2 anticipate, year 3 shape — and recognise that the progression is earned over years through consistent small choices rather than declared.

---

[← Module 19 — Regulatory Context](19-regulatory-context.md){ .md-button } [Next: Module 21 — Anti-patterns →](21-antipatterns.md){ .md-button .md-button--primary }
