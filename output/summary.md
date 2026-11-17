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
