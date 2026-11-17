## Credit risk acquisitions: results

| | |
|---|---|
| Applications | 1,000 (30% bad) |
| Scorecard (WoE logistic regression), 5-fold CV | AUC 0.771, Gini 0.541, KS 0.429 |
| Challenger model (gradient boosting), 5-fold CV | AUC 0.763, Gini 0.527, KS 0.411 |
| Recommended cutoff | 540: approval 32.5%, bad rate 7.7%, loss rate 3.60%, profit 28,303 DM |
| Score stability (PSI) | 0.0184 (stable) |

### Champion vs challenger

| strategy                                              |   approved |   approval_rate |   bad_rate |   approved_amount |   expected_loss |   loss_rate |   net_revenue |   profit |
|:------------------------------------------------------|-----------:|----------------:|-----------:|------------------:|----------------:|------------:|--------------:|---------:|
| Champion: policy rules only                           |        865 |           0.865 |      0.28  |           2490539 |          367530 |      0.1476 |        125415 |  -242116 |
| Challenger: scorecard cutoff 476 (same approval rate) |        871 |           0.871 |      0.251 |           2596640 |          349123 |      0.1345 |        144550 |  -204572 |
| Recommended: scorecard cutoff 540 (max profit)        |        325 |           0.325 |      0.077 |            866886 |           31190 |      0.036  |         59494 |    28303 |

### Swap set

| group                                             |   applications |   bad_rate |
|:--------------------------------------------------|---------------:|-----------:|
| Both approve                                      |            778 |      0.242 |
| Swap-in (challenger approves, champion declined)  |             93 |      0.333 |
| Swap-out (challenger declines, champion approved) |             87 |      0.621 |
| Both decline                                      |             42 |      0.643 |

### Business case sensitivity (profit-maximizing cutoff)

|   net_margin |   lgd |   best_cutoff |   approval_rate |   bad_rate |   profit |
|-------------:|------:|--------------:|----------------:|-----------:|---------:|
|         0.04 |  0.35 |           540 |           0.325 |      0.077 |    35234 |
|         0.04 |  0.45 |           540 |           0.325 |      0.077 |    28303 |
|         0.04 |  0.6  |           540 |           0.325 |      0.077 |    17906 |
|         0.06 |  0.35 |           530 |           0.427 |      0.11  |    71554 |
|         0.06 |  0.45 |           530 |           0.427 |      0.11  |    58148 |
|         0.06 |  0.6  |           540 |           0.325 |      0.077 |    47653 |
|         0.08 |  0.35 |           520 |           0.494 |      0.121 |   115450 |
|         0.08 |  0.45 |           530 |           0.427 |      0.11  |    97640 |
|         0.08 |  0.6  |           530 |           0.427 |      0.11  |    77531 |

### Operations: three-band strategy

| band                   |   applications |   share |   bad_rate |   avg_amount |
|:-----------------------|---------------:|--------:|-----------:|-------------:|
| Auto-approve           |            325 |   0.325 |      0.077 |         2667 |
| Refer to manual review |            169 |   0.169 |      0.207 |         2851 |
| Auto-decline           |            506 |   0.506 |      0.474 |         3799 |

Workload (10,000 applications/month, 20 min per review): auto_decision_rate 0.831, referral_rate 0.169, reviews_per_month 1690, reviews_per_day 80, review_hours_per_month 563, adjudicators_needed_fte 3.8

### Refer band options

| refer_band   |   auto_decision_rate |   referral_rate |   reviews_per_month |   reviews_per_day |   review_hours_per_month |   adjudicators_needed_fte |   refer_bad_rate |
|:-------------|---------------------:|----------------:|--------------------:|------------------:|-------------------------:|--------------------------:|-----------------:|
| none         |                1     |           0     |                   0 |                 0 |                        0 |                       0   |          nan     |
| 520-539      |                0.831 |           0.169 |                1690 |                80 |                      563 |                       3.8 |            0.207 |
| 500-539      |                0.644 |           0.356 |                3560 |               170 |                     1187 |                       8.1 |            0.278 |
| 480-539      |                0.472 |           0.528 |                5280 |               251 |                     1760 |                      12   |            0.348 |

### Marketing targeting

| purpose             | term         |   applications |   approval_rate |   bad_rate |   profit_per_application | recommendation   | reason                               |
|:--------------------|:-------------|---------------:|----------------:|-----------:|-------------------------:|:-----------------|:-------------------------------------|
| car (used)          | 25+ months   |             39 |           0.359 |      0.256 |                    319.9 | Target           | approved often, low risk, profitable |
| domestic appliances | 25+ months   |             58 |           0.362 |      0.345 |                    210.8 | Neutral          | mixed: keep in general campaigns     |
| car (used)          | 13-24 months |             49 |           0.571 |      0.102 |                    165.4 | Target           | approved often, low risk, profitable |
| radio/television    | 25+ months   |             31 |           0.065 |      0.581 |                     31.4 | Avoid            | most applicants would be declined    |
| radio/television    | 13-24 months |             85 |           0.212 |      0.294 |                     24.4 | Neutral          | mixed: keep in general campaigns     |
| others              | 25+ months   |             41 |           0.024 |      0.537 |                     18.5 | Avoid            | most applicants would be declined    |
| car (new)           | 25+ months   |             35 |           0.029 |      0.543 |                     12.1 | Avoid            | most applicants would be declined    |
| domestic appliances | 13-24 months |            111 |           0.495 |      0.225 |                      7.9 | Target           | approved often, low risk, profitable |
| domestic appliances | <=12 months  |            111 |           0.541 |      0.153 |                      7.5 | Target           | approved often, low risk, profitable |
| car (new)           | <=12 months  |            108 |           0.324 |      0.25  |                      1.2 | Neutral          | mixed: keep in general campaigns     |
| others              | 13-24 months |             40 |           0.225 |      0.25  |                    -16   | Avoid            | loses money under the strategy       |
| radio/television    | <=12 months  |             65 |           0.338 |      0.231 |                    -34.5 | Avoid            | loses money under the strategy       |
| car (new)           | 13-24 months |             91 |           0.176 |      0.473 |                    -59   | Avoid            | loses money under the strategy       |

### Outcomes by purpose

| segment             |   applications |   approval_rate |   bad_rate_all |   bad_rate_approved |   avg_pd |
|:--------------------|---------------:|----------------:|---------------:|--------------------:|---------:|
| domestic appliances |            280 |           0.486 |          0.221 |               0.066 |    0.199 |
| car (new)           |            234 |           0.222 |          0.38  |               0.115 |    0.345 |
| radio/television    |            181 |           0.232 |          0.32  |               0.095 |    0.335 |
| car (used)          |            103 |           0.495 |          0.165 |               0     |    0.205 |
| others              |             97 |           0.206 |          0.351 |               0.1   |    0.398 |
| retraining          |             50 |           0.2   |          0.44  |               0.2   |    0.429 |
| education           |             22 |           0.273 |          0.364 |               0.333 |    0.362 |
| repairs             |             12 |           0.25  |          0.333 |               0     |    0.389 |
| furniture/equipment |             12 |           0     |          0.417 |             nan     |    0.664 |
| business            |              9 |           0.556 |          0.111 |               0     |    0.159 |
