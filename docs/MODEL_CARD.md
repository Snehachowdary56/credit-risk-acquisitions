# Model card: application scorecard (credit risk acquisitions)

**Purpose.** Rank new consumer credit applications by risk of default, so an adjudication strategy (score cutoff) can approve or decline them. It is a decision-support tool: the cutoff, policy rules and exceptions stay with credit risk management.

**Data.** German Credit data: 1,000 historical consumer credit applications, 30% bad outcomes (Hofmann, UCI Machine Learning Repository, CC BY 4.0; CSV mirror in `data/`). Category labels are used as they appear in the source file.

**Method.** Weight of Evidence (WoE) binning, characteristics with Information Value of 0.02 or more, then logistic regression. Scores are scaled so that 600 points = 50:1 good:bad odds and every 20 points doubles the odds (PDO 20). A points table for every attribute is published, so each decision can be explained to an applicant or an auditor.

**Excluded inputs (fair lending).** Sex / marital status, foreign-worker status and age are **not** model inputs. Age is kept only to monitor outcomes by age band.

**Performance (5-fold cross-validated, every application scored by a model that never saw it).**

| Model | AUC | Gini | KS |
|---|---|---|---|
| Scorecard (chosen) | 0.771 | 0.541 | 0.429 |
| Gradient boosting challenger | 0.763 | 0.527 | 0.411 |

The scorecard is kept because it performs as well as the more complex model and is fully explainable.

**Stability.** PSI of the score between the development sample and a later sample: 0.018 (stable; < 0.10). PSI for the top characteristics: 0.006 to 0.026 (stable).

**Fairness check (open item).** Even without age as an input, approval rates under the recommended cutoff differ by age band: 18–24: 18.8%, 25–34: 29.8%, 35–49: 38.5%, 50+: 41.6%. Younger applicants also have higher observed bad rates (41% vs 23–33%), so part of the gap is risk, but characteristics such as employment length and property can act as proxies for age. This needs review by compliance before use.

**Limitations.** Small, historical sample (1,000 applications); amounts in DM; the business case uses assumed loss given default (45%) and net margin (4% a year), with a sensitivity table in the workbook. The model must be validated on the lender's own recent applications before any use.

**Monitoring plan.** Monthly: score PSI and characteristic PSI (alert at 0.10, review at 0.25), approval rate and early delinquency by score band and segment; re-check the fairness table quarterly.
