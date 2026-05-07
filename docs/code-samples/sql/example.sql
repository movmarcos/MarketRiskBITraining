-- Module: _template (generic illustrative snippet)
-- Dialect: ANSI SQL (portable; tested against PostgreSQL 15+ and Snowflake)
-- Description: Demonstrates a CTE that computes a 7-day running total of
--   daily values using a windowed SUM. Runs standalone — the `daily_values`
--   CTE provides its own seed data, so no external tables are required.

WITH daily_values (value_date, amount) AS (
    VALUES
        (DATE '2026-05-01',  100),
        (DATE '2026-05-02',  120),
        (DATE '2026-05-03',   90),
        (DATE '2026-05-04',  140),
        (DATE '2026-05-05',  110),
        (DATE '2026-05-06',  130),
        (DATE '2026-05-07',  150)
)
SELECT
    value_date,
    amount,
    SUM(amount) OVER (
        ORDER BY value_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_total
FROM daily_values
ORDER BY value_date;
