-- Three-band strategy for Operations: auto-approve 540+, refer 520-539 to manual review, auto-decline below 520.
SELECT
  CASE WHEN score >= 540 THEN '1 Auto-approve'
       WHEN score >= 520 THEN '2 Refer to manual review'
       ELSE '3 Auto-decline' END                  AS band,
  COUNT(*)                                        AS applications,
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER (), 3)      AS share,
  ROUND(AVG(bad), 3)                              AS bad_rate,
  ROUND(AVG(amount))                              AS avg_amount
FROM `credit.scored_applications`
GROUP BY band
ORDER BY band;
