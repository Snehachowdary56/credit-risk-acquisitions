"""Adjudication strategy: score cutoffs, approval rate vs bad rate vs expected loss, the business case,
and a champion (current policy rules) vs challenger (scorecard) comparison with swap-set analysis."""
from __future__ import annotations

import numpy as np
import pandas as pd

# Business-case assumptions (stated, not taken from the data):
LGD = 0.45            # loss given default on unsecured consumer credit (share of the amount lost)
NET_MARGIN = 0.04     # annual net interest margin earned on a good loan


def economics(df: pd.DataFrame, approved: pd.Series, lgd: float = LGD, margin: float = NET_MARGIN) -> dict:
    a = df[approved]
    goods, bads = a[a["bad"] == 0], a[a["bad"] == 1]
    loss = float((bads["amount"] * lgd).sum())
    revenue = float((goods["amount"] * margin * goods["duration"] / 12).sum())
    return {
        "approved": int(approved.sum()),
        "approval_rate": round(approved.mean(), 3),
        "bad_rate": round(a["bad"].mean(), 3) if len(a) else 0.0,
        "approved_amount": int(a["amount"].sum()),
        "expected_loss": round(loss),
        "loss_rate": round(loss / a["amount"].sum(), 4) if len(a) else 0.0,
        "net_revenue": round(revenue),
        "profit": round(revenue - loss),
    }


def cutoff_table(df: pd.DataFrame, scores: pd.Series, step: int = 10, **econ) -> pd.DataFrame:
    rows = []
    for cut in range(int(scores.min()) // step * step, int(scores.max()) + step, step):
        rows.append({"cutoff": cut, **economics(df, scores >= cut, **econ)})
    return pd.DataFrame(rows)


def sensitivity(df: pd.DataFrame, scores: pd.Series, margins=(0.04, 0.06, 0.08), lgds=(0.35, 0.45, 0.60)) -> pd.DataFrame:
    """Business case sensitivity: how the profit-maximizing cutoff moves with margin and loss-given-default."""
    rows = []
    for m in margins:
        for l in lgds:
            best = best_cutoff(cutoff_table(df, scores, margin=m, lgd=l))
            rows.append({"net_margin": m, "lgd": l, "best_cutoff": int(best["cutoff"]),
                         "approval_rate": best["approval_rate"], "bad_rate": best["bad_rate"], "profit": int(best["profit"])})
    return pd.DataFrame(rows)


def best_cutoff(table: pd.DataFrame) -> pd.Series:
    return table.loc[table["profit"].idxmax()]


def champion_policy(df: pd.DataFrame) -> pd.Series:
    """Stand-in for a typical rules-only policy before a scorecard: approve unless a knock-out rule fires."""
    decline = (
        (df["credit_history"] == "delay in paying off in the past")
        | ((df["status"] == "... < 100 DM") & (df["savings"] == "... < 100 DM") & (df["amount"] > 5000))
        | (df["duration"] > 48)
    )
    return ~decline


def matched_cutoff(scores: pd.Series, approval_rate: float) -> int:
    """Lowest cutoff whose approval rate does not exceed the target, so champion and challenger approve as many."""
    return int(np.quantile(scores, 1 - approval_rate, method="higher"))


def swap_set(df: pd.DataFrame, champion: pd.Series, challenger: pd.Series) -> pd.DataFrame:
    groups = {
        "Both approve": champion & challenger,
        "Swap-in (challenger approves, champion declined)": challenger & ~champion,
        "Swap-out (challenger declines, champion approved)": ~challenger & champion,
        "Both decline": ~champion & ~challenger,
    }
    return pd.DataFrame([{"group": k, "applications": int(m.sum()),
                          "bad_rate": round(df.loc[m, "bad"].mean(), 3) if m.any() else None}
                         for k, m in groups.items()])
