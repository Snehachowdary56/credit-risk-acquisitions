"""Application outcomes by segment, computed with SQL (SQLite) so the logic is easy to move to a warehouse."""
from __future__ import annotations

import sqlite3

import pandas as pd

SEGMENT_SQL = """
SELECT {segment} AS segment,
       COUNT(*)                                        AS applications,
       ROUND(AVG(approved), 3)                         AS approval_rate,
       ROUND(AVG(bad), 3)                              AS bad_rate_all,
       ROUND(SUM(bad * approved) * 1.0 / NULLIF(SUM(approved), 0), 3) AS bad_rate_approved,
       ROUND(AVG(pd), 3)                               AS avg_pd
FROM applications
GROUP BY {segment}
ORDER BY applications DESC
"""

BANDS = {
    "purpose": "purpose",
    "age_band": "CASE WHEN age < 25 THEN '18-24' WHEN age < 35 THEN '25-34' WHEN age < 50 THEN '35-49' ELSE '50+' END",
    "term_band": "CASE WHEN duration <= 12 THEN '<=12 months' WHEN duration <= 24 THEN '13-24 months' ELSE '25+ months' END",
    "amount_band": "CASE WHEN amount < 2000 THEN '<2,000' WHEN amount < 5000 THEN '2,000-4,999' ELSE '5,000+' END",
}


def by_segment(df: pd.DataFrame, approved: pd.Series, pd_: pd.Series) -> dict[str, pd.DataFrame]:
    con = sqlite3.connect(":memory:")
    frame = df.assign(approved=approved.astype(int), pd=pd_)
    frame.to_sql("applications", con, index=False)
    return {name: pd.read_sql_query(SEGMENT_SQL.format(segment=expr), con) for name, expr in BANDS.items()}
