# Code samples

This directory holds reusable SQL and Python snippets that are referenced from the training modules via the `pymdownx.snippets` Markdown extension. Keeping snippets out of the prose makes them runnable, testable, and easier to maintain.

## Layout

```
docs/code-samples/
├── README.md     <- this file
├── sql/          <- SQL snippets, one file per example
└── python/       <- Python snippets, one file per example
```

## Naming convention

Files are named `<module-num>-<short-name>.<ext>` where:

- `<module-num>` is the two-digit module number (`01` through `22`).
- `<short-name>` is a kebab-case slug describing what the snippet does.
- `<ext>` is `sql` or `py`.

Examples:

- `09-historical-var.py` — historical VaR demo for module 09.
- `13-bitemporal-upsert.sql` — bitemporal upsert pattern for module 13.
- `07-fact-position-ddl.sql` — fact-table DDL for module 07.

If a single module needs several snippets that belong together, add a second slug segment: `09-historical-var-bootstrap.py`, `09-historical-var-backtest.py`.

## Referencing snippets from a module

The `pymdownx.snippets` extension is configured in `mkdocs.yml`. Its `base_path` defaults to `docs/`, so paths in references are written **relative to `docs/`** (no leading `docs/`):

````markdown
```sql
;--8<-- "code-samples/sql/13-bitemporal-upsert.sql"
```
````

The build inlines the file's contents at the marker. The fenced block's language hint controls syntax highlighting, so make sure it matches the snippet's actual language.

## Runnability

**Every snippet must either run standalone, or include a header comment that documents the required setup.** A reader copy-pasting a snippet should not have to guess at missing context.

A header comment should cover, at minimum:

- The module that uses the snippet.
- Any sample-data DDL or seed inserts the snippet depends on (or a reference to a sibling snippet that creates them).
- External libraries or dialect-specific features used.
- A one-line description of what the snippet demonstrates.

## SQL conventions

- **Target ANSI SQL** wherever practical so snippets are portable.
- **Note the dialect** at the top of the file when using vendor-specific features. Use a comment like `-- Dialect: Snowflake (uses QUALIFY, MERGE)` or `-- Dialect: PostgreSQL 15+ (uses MERGE)`.
- Prefer explicit column lists over `SELECT *`.
- Use uppercase for keywords and lowercase for identifiers.
- Format with one clause per line for readability inside the rendered docs.

## Python conventions

- **Target Python 3.11+.**
- **Stdlib + `numpy` + `pandas` only**, unless a module specifically introduces another library (e.g., `scipy.stats` for module 09). Document any extra dependency in the header comment.
- Include type hints on public functions.
- Include a `if __name__ == "__main__":` demo block whenever the snippet defines reusable functions, so the file is runnable as `python <file>.py`.
- Keep snippets self-contained — no imports from sibling files unless explicitly noted.

## Testing snippets locally

SQL snippets can be smoke-tested in a local Postgres or Snowflake worksheet. Python snippets should run cleanly with:

```bash
python docs/code-samples/python/<file>.py
```

There is no automated test harness yet; if/when one is added, snippets must continue to satisfy the runnability rule above.
