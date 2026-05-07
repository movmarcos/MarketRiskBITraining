# Market Risk BI Training

A structured, beginner-to-pro training program on **Market Risk** for BI and data professionals — focused on table structures, fact/dimension modeling, and the business context that makes a data professional truly valuable to a securities firm.

## 🎯 What This Training Covers

- The business of market risk: VaR, stress testing, sensitivities, P&L attribution
- How a securities firm is organized and where data flows
- Dimensional modeling applied to risk data: facts, dimensions, grain, hierarchies
- The statistics you need (taught in context, not as a standalone module)
- Engineering excellence: data quality, lineage, performance, bitemporality
- Working effectively with the business

## 📚 Live Site

The training is published as a static site via GitHub Pages:

**👉 https://movmarcos.github.io/MarketRiskBITraining/**

## 🗂️ Curriculum

22 modules organized into 7 phases:

1. **Foundations** — Market risk basics, firm organization, trade lifecycle, instruments
2. **Data Modeling Core** — Dimensional modeling, core dimensions, fact tables
3. **Risk Measures** — Sensitivities, VaR, stress testing
4. **Cross-Cutting Concepts** — Market data, aggregation, bitemporality, P&L
5. **Engineering Excellence** — Quality, lineage, performance, architecture
6. **Business-Aligned Pro** — Regulatory context, business engagement, anti-patterns
7. **Capstone** — End-to-end risk data mart design

See [the full curriculum](docs/curriculum.md) for details.

## 🛠️ Local Development

To preview the site locally:

```bash
pip install mkdocs-material pymdown-extensions
mkdocs serve
```

Then open http://127.0.0.1:8000 in your browser.

To build the static site:

```bash
mkdocs build
```

## 🚀 Deployment

The site auto-deploys to GitHub Pages via GitHub Actions on every push to `main`.

To enable GitHub Pages on this repo:

1. Go to **Settings → Pages**
2. Under **Source**, select **GitHub Actions**
3. Push to `main` — the workflow will deploy automatically

## 📝 Contributing / Editing

Each module lives in `docs/modules/` as a Markdown file. To edit a module:

1. Open the relevant `.md` file
2. Edit the content
3. Commit and push — the site rebuilds automatically

## 📄 License

Educational content. Use freely for learning and training purposes.
