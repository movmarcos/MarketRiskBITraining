# Claude for Financial Services: A Practical, No-Fluff Guide

*A walkthrough for finance and data professionals who want to actually try Anthropic's new financial-services plugins — installed in the terminal, used in plain English, with the bugs and caveats called out honestly.*

---

On 5 May 2026, Anthropic released **Claude for Financial Services** — a catalogue of plugins that turn Claude into something closer to a junior analyst that lives inside your terminal or your spreadsheet.

If you have been reading the articles that followed, you may have noticed a pattern: a lot of "this changes everything" energy, very little of "here is the command, here is what it does, here is what does not work yet." This guide is the opposite of that. No course at the end. No paywall. Copy the commands, run them, see for yourself.

This guide assumes you can open a terminal. If you have never used Claude before, the first section gets you set up; if you already use Claude Code daily, skip to the install commands.

---

## What it actually is

It is **not a single product**. It is a marketplace of plugins, hosted in the public GitHub repository [`anthropics/financial-services`](https://github.com/anthropics/financial-services). Three categories live inside it:

**1. Agent plugins (10 today).** Each one wraps a focused workflow into an agent you can talk to in plain English: `earnings-reviewer`, `gl-reconciler`, `kyc-screener`, `market-researcher`, `meeting-prep-agent`, `model-builder`, `month-end-closer`, `pitch-agent`, `statement-auditor`, `valuation-reviewer`.

**2. Vertical plugins (7 today).** Bigger bundles that group several agents and skills around a domain: `equity-research`, `financial-analysis`, `fund-admin`, `investment-banking`, `operations`, `private-equity`, `wealth-management`.

**3. Partner plugins (2 today).** Connectors to vendor data: `lseg` (Refinitiv) and `spglobal`. These need their own subscriptions to actually pull data, but they install for free and you can read the schemas they expose.

Everything is open source. The plugins are Markdown and YAML files. You can read every prompt that goes to the model, fork what does not fit your firm, and propose fixes upstream when something is wrong.

---

## The three ways you can use this

You have three paths. Pick the one that matches how you already work.

**Claude Code (CLI)**
Best for: engineers and analysts comfortable with a terminal.
You need: a Claude API key or paid Claude account.

**Claude Desktop**
Best for: people who live in Excel and want Claude to read/write spreadsheets.
You need: the Claude desktop app + Excel.

**Claude.ai (web)**
Best for: quick experiments without installing anything.
You need: a free or paid Claude account.

The plugin catalogue is most fully exercised through **Claude Code in the terminal**, so that is what I cover in detail. The desktop and web routes get a brief section at the end.

---

## Path 1: Claude Code in the terminal (the full walkthrough)

### Step 1 — install Claude Code

If you already have Claude Code, skip to Step 2.

```bash
# macOS / Linux
curl -fsSL https://claude.ai/install.sh | sh

# or via npm if you prefer
npm install -g @anthropic-ai/claude-code
```

Then sign in:

```bash
claude
```

The first run opens a browser window for sign-in. After that, the `claude` command starts an interactive session. You can also pipe prompts into it non-interactively, but the interactive session is the default and the easiest place to start.

### Step 2 — add the financial-services marketplace

A marketplace is just a Git repository that publishes a list of plugins. You add it once; you install plugins from it as many times as you like.

```bash
claude plugin marketplace add https://github.com/anthropics/financial-services.git
```

A note that cost me a few minutes: some early articles list the marketplace name as `claude-for-financial-services`, which is the *display name*. The *repository* is `anthropics/financial-services`. The HTTPS URL above is what works without setting up SSH keys.

You should see:

```
✔ Successfully added marketplace: claude-for-financial-services
```

### Step 3 — see what's available

The plugins live on disk after the marketplace clone. You can browse them with:

```bash
ls ~/.claude/plugins/marketplaces/claude-for-financial-services/plugins/
```

You will see three folders matching the three categories (`agent-plugins`, `vertical-plugins`, `partner-built`). Inside each, one folder per plugin.

Open any plugin's `README.md` to see what it does:

```bash
cat ~/.claude/plugins/marketplaces/claude-for-financial-services/plugins/agent-plugins/statement-auditor/README.md
```

### Step 4 — install one or two plugins

Install syntax is `plugin-name@marketplace-name`:

```bash
claude plugin install statement-auditor@claude-for-financial-services
claude plugin install financial-analysis@claude-for-financial-services
```

Verify:

```bash
claude plugin list
```

You should see your new plugins listed alongside any others you already had, each with status `enabled`.

### A real bug you may hit (and the one-line fix)

When I installed `financial-analysis`, it failed to load with this error:

```
Status: ✘ failed to load
Error: Hook load failed: expected object, received array
```

The cause is that the plugin shipped with an empty `[]` in its `hooks/hooks.json` file, where the loader expects an empty `{}`. The fix:

```bash
echo '{}' > ~/.claude/plugins/marketplaces/claude-for-financial-services/plugins/vertical-plugins/financial-analysis/hooks/hooks.json
echo '{}' > ~/.claude/plugins/cache/claude-for-financial-services/financial-analysis/0.1.0/hooks/hooks.json
```

Then **fully exit Claude Code and start a new session**. Reinstalling within the same session will not pick up the change because the loader caches its parse result at startup.

If you want to be a good citizen, the upstream PR is one character. The bug is in the official Anthropic repo; submit a PR and you save the next person the same hour.

### Step 5 — actually use it

Plugins surface as **subagents** and **skills**. You do not need to remember the exact name. Just describe the task in plain English; the matching skill picks itself.

Three examples that work today.

**Example A — audit an Excel model**

```
Audit the formulas on the Cash Flow tab of ~/Downloads/lbo-model.xlsx.
Flag any cells where the formula references a different sheet without
a sheet name, any hardcoded numbers in formula cells, and any rows
where the row total does not match the sum of its components.
```

The `audit-xls` skill from `statement-auditor` triggers on phrases like "audit this sheet", "QA this spreadsheet", "model won't balance". You will get back a structured report grouped by issue type, not a wall of text.

**Example B — build a quick DCF**

```
Build a 5-year DCF for a software company with these assumptions:
revenue $200M growing 25% / 18% / 14% / 11% / 9%, gross margin 78%,
operating margin reaching 22% by year 5, capex 4% of revenue, working
capital neutral, terminal growth 3%, WACC 9%. Output the model as an
Excel file with separate tabs for assumptions, P&L projection, FCF
build, valuation summary.
```

The `model-builder` agent from `financial-analysis` handles this. You will get an actual `.xlsx` file you can open and edit. The model is not magic — it is a transparent build you can audit and modify, which is exactly what you want.

**Example C — review an earnings transcript**

```
Read this earnings call transcript [paste or attach]. Summarize:
guidance changes versus prior quarter, any one-time items that affect
the comparable, and the three most pointed analyst questions with
management's actual answer (not the spin).
```

The `earnings-reviewer` agent does this kind of work. The output is structured because the prompt is structured. Spend two minutes shaping the question and the result is dramatically better than a one-liner.

### Inspect before you trust

Because the plugins are Markdown, you can read the exact prompt the agent uses before you run it:

```bash
cat ~/.claude/plugins/marketplaces/claude-for-financial-services/plugins/agent-plugins/statement-auditor/agents/statement-auditor.md
```

This is the most important habit when using these plugins for actual work. The plugin is a recipe; you can read the recipe.

---

## Path 2: Claude Desktop (for spreadsheet work)

If your day is in Excel, install the **Claude desktop app** from `claude.ai/download`, sign in, then enable the financial-services skills from Settings → Skills (the UI mirrors the marketplace structure described above).

The desktop app's killer feature for finance work is that it can read and modify open spreadsheets directly. The same `audit-xls`, `model-builder`, and `nav-tieout` skills work; you point Claude at the file and it operates on it.

A practical workflow that I use:

1. Open the model in Excel.
2. In Claude Desktop, ask "audit the Working Capital tab — anything broken?"
3. Get a list of issues, fix them in Excel, ask "audit again".
4. When clean, ask "now build a sensitivity table for revenue growth ± 200 bps and operating margin ± 100 bps".

You stay in Excel for the editing; Claude does the bulk reading, validation, and the parts that would otherwise be a ten-minute manual exercise.

---

## Path 3: Claude.ai web (for trying things out)

The web app at `claude.ai` is the lowest-friction way to test what these plugins do without installing anything. You can attach a spreadsheet, paste an earnings transcript, or describe a model and Claude will produce a useful first pass.

The trade-off is that the web does not give you the full plugin marketplace control — you cannot browse the agent definitions, fork them, or compose them. For exploration that is fine; for repeated production work, Claude Code or Claude Desktop are better fits.

---

## Honest limits

A short list of things people are not telling you in the polished articles.

**It costs money.** Most workflows here are designed for Claude Opus 4.7. That is the most capable model Anthropic ships, and it is not the cheapest. A typical agent run uses anywhere from a few cents to a couple of dollars in API tokens, depending on how much data you give it. If you are on a paid Claude plan (Pro, Team, Enterprise), this is bundled. If you are on the API directly, it is metered.

**Vendor data is separate.** The `lseg` and `spglobal` partner plugins install for free, but they are connectors. To actually retrieve a market data point or a company filing through them, you need an active subscription with the vendor. The plugin gives you the wiring; you bring the data feed.

**It is brand new.** These plugins shipped on 5 May 2026. The bug I described above is one example; you will hit others. Treat the plugins as a strong starting template, not as black-box production software. Read the agent's Markdown definition before trusting its output for anything that matters.

**Human review is non-negotiable.** Every workflow stages output for you to review. None of them post anything, file anything, or send anything without you saying go. That is by design. Do not bypass it.

**Region availability.** The plugins themselves are public; using them requires a Claude account. Claude is not available in every country. Check `claude.ai` from your location before you start.

---

## Why this is worth your time even if you never use it for paid work

Even if you read this entire guide, install nothing, and never spend a cent, there is a reason to look at the plugins on disk. They are some of the best examples I have seen of how to write a focused, structured prompt for a real task. If you build any internal tooling that uses an LLM, the agent definitions in this repository are worth reading line by line. They will improve your own prompts.

I will keep saying it because it is the point: the plugins are open source. The recipe is on disk. The recipe is the value.

---

## What to try first

If you only have one hour to spend on this:

1. Install Claude Code.
2. Add the marketplace.
3. Install `statement-auditor` and `financial-analysis` (apply the bug fix above if you hit it).
4. Pick a real spreadsheet — your own work, an old practice model, anything — and ask "audit this for formula issues and broken tie-outs". Look at what it finds.
5. Open the agent's Markdown definition and read the prompt the agent used. That is the lesson.

If it works for you, share what you learned. If it does not, file an issue on the GitHub repo. The catalogue gets better the more people use it well.

---

## Resources

- Anthropic announcement: [anthropic.com/news/finance-agents](https://www.anthropic.com/news/finance-agents)
- The repository: [github.com/anthropics/financial-services](https://github.com/anthropics/financial-services)
- Claude Code documentation: [docs.claude.com](https://docs.claude.com/)
- Install help (for Cowork): [support.claude.com/en/articles/13851150](https://support.claude.com/en/articles/13851150-install-financial-services-plugins-for-cowork)

---

*This guide is free. I am not selling a course, a newsletter, or a consulting service. If it helped you, share it with someone who would have hit the same friction. That is enough.*



