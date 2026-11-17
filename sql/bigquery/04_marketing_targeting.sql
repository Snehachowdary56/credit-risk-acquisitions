-- Marketing: profit per application by purpose and term under the recommended cutoff (segments with 25+ applications).
WITH scored AS (
  SELECT *,
    CASE WHEN duration <= 12 THEN '<=12 months' WHEN duration <= 24 THEN '13-24 months' ELSE '25+ months' END AS term,
    CASE WHEN score < 540 THEN 0
         WHEN bad = 0 THEN amount * 0.04 * duration / 12
         ELSE -amount * 0.45 END AS profit
  FROM `credit.scored_applications`
)
SELECT purpose, term, COUNT(*) AS applications,
       ROUND(COUNTIF(score >= 540) / COUNT(*), 3) AS approval_rate,
       ROUND(AVG(bad), 3)                          AS bad_rate,
       ROUND(AVG(profit), 1)                       AS profit_per_application
FROM scored
GROUP BY purpose, term
HAVING COUNT(*) >= 25
ORDER BY profit_per_application DESC;
