-- Application outcomes by loan purpose under the recommended cutoff (540).
SELECT
  purpose,
  COUNT(*)                                                         AS applications,
  ROUND(COUNTIF(score >= 540) / COUNT(*), 3)                       AS approval_rate,
  ROUND(AVG(bad), 3)                                               AS bad_rate_all,
  ROUND(SAFE_DIVIDE(COUNTIF(score >= 540 AND bad = 1), COUNTIF(score >= 540)), 3) AS bad_rate_approved
FROM `credit.scored_applications`
GROUP BY purpose
ORDER BY applications DESC;
