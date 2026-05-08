# Module: 16 — Lineage & Auditability
# Purpose:  Toy SQL parser that extracts table-level lineage edges from a
#           collection of "INSERT INTO ... SELECT ... FROM ... [JOIN ...]"
#           statements and emits OpenLineage-style edges (source -> target).
#           The intent is pedagogical: show what a parsing-based table-level
#           lineage capture does in spirit, and where it breaks. Real
#           production lineage uses a proper SQL parser (sqlglot, sqlfluff,
#           sqllineage); this script uses only stdlib `re` so the mechanics
#           are visible end-to-end.
# Depends:  Python 3.11+ (stdlib only).
# Run:      python docs/code-samples/python/16-sql-lineage.py
#
# Limitations called out explicitly so that the reader does not mistake
# this for production-grade lineage:
#   * Does NOT handle CTEs (WITH clauses). A real parser resolves CTE names
#     against the surrounding scope; this regex collapses them into the
#     edge set, which is wrong.
#   * Does NOT handle subqueries in the FROM clause beyond the trivial case.
#     "FROM (SELECT ... FROM A) AS x" is invisible to the regex.
#   * Does NOT handle dynamic SQL, prepared statements, or anything that
#     resolves a table name at runtime.
#   * Does NOT model column-level lineage. Every column in target depends
#     on every column in source, by assumption.
#   * Does NOT canonicalise schemas (e.g., "public.x" vs "x").
#
# A production lineage capture either parses SQL with a real parser or
# captures the lineage at execution time (query log, OpenLineage events
# emitted by the engine). Both approaches sit on top of the same core idea
# this script demonstrates: an edge from each source table to each target
# table, captured against a code_version, and stored for transitive
# closure queries.

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class LineageEdge:
    """One source -> target edge for table-level lineage.

    The fields mirror the minimal OpenLineage RunEvent surface:
      - source_table: the upstream table feeding the target
      - target_table: the downstream table being written
      - transform_type: a free-form tag (insert_select, ctas, merge, ...)
      - code_version: the git SHA of the transformation that produced the edge
    """

    source_table: str
    target_table: str
    transform_type: str = "insert_select"
    code_version: str = "unknown"


@dataclass
class LineageGraph:
    """A small in-memory lineage graph keyed by (source, target)."""

    edges: list[LineageEdge] = field(default_factory=list)

    def add(self, edge: LineageEdge) -> None:
        if edge not in self.edges:
            self.edges.append(edge)

    def downstream_of(self, table: str) -> list[str]:
        """Return every table downstream of `table` (transitive closure).

        BFS over the edge list. Cycles are guarded by the `seen` set; in a
        well-formed warehouse the graph is a DAG, but defensive code costs
        nothing here and saves a stack overflow when someone introduces a
        cycle by accident.
        """

        seen: set[str] = set()
        frontier: list[str] = [table]
        out: list[str] = []
        while frontier:
            current = frontier.pop()
            for edge in self.edges:
                if edge.source_table != current:
                    continue
                if edge.target_table in seen:
                    continue
                seen.add(edge.target_table)
                out.append(edge.target_table)
                frontier.append(edge.target_table)
        return out

    def to_openlineage_like(self) -> list[dict[str, str]]:
        """Emit a JSON-serialisable list mirroring the shape of OpenLineage
        input/output dataset facets. Real OpenLineage events have job and
        run identifiers; we omit those for clarity.
        """

        return [
            {
                "inputs": edge.source_table,
                "outputs": edge.target_table,
                "transform": edge.transform_type,
                "version": edge.code_version,
            }
            for edge in self.edges
        ]


# ---------------------------------------------------------------------------
# The parser. Regex-based, stdlib-only, deliberately small.
# ---------------------------------------------------------------------------

# Match an `INSERT INTO <target> ... ;` statement as a whole. The body
# between the INSERT and the terminating semicolon is captured so that
# the JOIN and FROM extractors can scan it. Case-insensitive.
_INSERT_RE = re.compile(
    r"INSERT\s+INTO\s+(?P<target>[\w\.]+)(?P<body>[^;]*?);",
    re.IGNORECASE | re.DOTALL,
)

# Inside the body, find every "FROM <table>" — single-table FROM clauses.
_FROM_RE = re.compile(r"FROM\s+(?P<tbl>[\w\.]+)", re.IGNORECASE)

# Inside the body, find every "JOIN <table>".
_JOIN_RE = re.compile(r"JOIN\s+(?P<tbl>[\w\.]+)", re.IGNORECASE)

def extract_dependencies(
    sql_text: str, code_version: str = "unknown"
) -> list[tuple[str, str]]:
    """Parse a SQL string and return (source_table, target_table) edges.

    The parser handles the common case `INSERT INTO X SELECT ... FROM A
    JOIN B JOIN C ...` and emits one edge per (source, target) pair.
    Anything more complex than that is either ignored or mis-parsed; see
    the module-level docstring for the exhaustive list of caveats.
    """

    edges: list[tuple[str, str]] = []
    for match in _INSERT_RE.finditer(sql_text):
        target = match.group("target").strip()
        body = match.group("body")
        sources: set[str] = set()
        for from_match in _FROM_RE.finditer(body):
            sources.add(from_match.group("tbl"))
        for join_match in _JOIN_RE.finditer(body):
            sources.add(join_match.group("tbl"))
        for source in sorted(sources):
            edges.append((source, target))
    return edges


def build_graph_from_sql(
    sql_text: str, code_version: str = "unknown"
) -> LineageGraph:
    """Convenience wrapper: parse SQL, build a LineageGraph."""

    graph = LineageGraph()
    for source, target in extract_dependencies(sql_text, code_version):
        graph.add(
            LineageEdge(
                source_table=source,
                target_table=target,
                transform_type="insert_select",
                code_version=code_version,
            )
        )
    return graph


# ---------------------------------------------------------------------------
# Demo: run the parser on a realistic risk-warehouse SQL fragment.
# ---------------------------------------------------------------------------

_DEMO_SQL = """
-- Stage 1: stage the raw market data feed.
INSERT INTO stg_market_data
SELECT
    business_date,
    risk_factor,
    spot_rate AS fx_rate
FROM vendor_market_data
WHERE feed_status = 'OK';

-- Stage 2: conform staged data into the market-factor dimension.
INSERT INTO dim_market_factor (factor_sk, factor_name, value, business_date)
SELECT
    md5(s.risk_factor || s.business_date) AS factor_sk,
    s.risk_factor AS factor_name,
    s.fx_rate AS value,
    s.business_date
FROM stg_market_data s
JOIN ref_risk_factor r
  ON s.risk_factor = r.risk_factor_code;

-- Stage 3: produce the sensitivity fact for FX delta.
INSERT INTO fact_sensitivity
SELECT
    p.book_sk,
    p.instrument_sk,
    p.business_date,
    f.factor_sk,
    p.notional * f.value AS fx_delta_value
FROM fact_position p
JOIN dim_market_factor f
  ON p.business_date = f.business_date
  AND f.factor_name = 'FX_USD'
WHERE p.is_current = TRUE;
"""


def _demo() -> None:
    print("=== Stage 1: parsed edges ===")
    edges = extract_dependencies(_DEMO_SQL, code_version="git:abc1234")
    for source, target in edges:
        print(f"  {source:30s} -> {target}")

    graph = build_graph_from_sql(_DEMO_SQL, code_version="git:abc1234")

    print("\n=== Downstream of 'vendor_market_data' (transitive closure) ===")
    for downstream in graph.downstream_of("vendor_market_data"):
        print(f"  -> {downstream}")

    print("\n=== Downstream of 'fact_position' ===")
    for downstream in graph.downstream_of("fact_position"):
        print(f"  -> {downstream}")

    print("\n=== OpenLineage-like JSON payload ===")
    print(json.dumps(graph.to_openlineage_like(), indent=2))


if __name__ == "__main__":
    _demo()
