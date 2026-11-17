-- Cutoff strategy: approval rate, bad rate, expected loss and profit for every score cutoff.
-- Assumptions: loss given default 45%, net margin 4% a year.
WITH cutoffs AS (SELECT cutoff FROM UNNEST(GENERATE_ARRAY(400, 620, 10)) AS cutoff)
SELECT
  cutoff,
  COUNTIF(score >= cutoff)                                                      AS approved,
  ROUND(COUNTIF(score >= cutoff) / COUNT(*), 3)                                 AS approval_rate,
  ROUND(SAFE_DIVIDE(COUNTIF(score >= cutoff AND bad = 1), COUNTIF(score >= cutoff)), 3) AS bad_rate,
  ROUND(SUM(IF(score >= cutoff AND bad = 1, amount * 0.45, 0)))                 AS expected_loss,
  ROUND(SUM(IF(score >= cutoff AND bad = 0, amount * 0.04 * duration / 12, 0))
      - SUM(IF(score >= cutoff AND bad = 1, amount * 0.45, 0)))                 AS profit
FROM `credit.scored_applications` CROSS JOIN cutoffs
GROUP BY cutoff
ORDER BY cutoff;
