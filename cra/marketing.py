"""Marketing: which applicant segments to target in acquisition campaigns, given approval rate, bad rate and
profit per application under the adjudication strategy."""
from __future__ import annotations

import pandas as pd

from cra.strategy import LGD, NET_MARGIN

MIN_SEGMENT = 25  # smaller segments are too noisy to act on


def term_band(d: pd.Series) -> pd.Series:
    return pd.cut(d, [0, 12, 24, 1000], labels=["<=12 months", "13-24 months", "25+ months"]).astype(str)


def targeting(df: pd.DataFrame, approved: pd.Series) -> pd.DataFrame:
    d = df.assign(approved=approved, term=term_band(df["duration"]))
    d["profit"] = 0.0
    a = d["approved"]
    d.loc[a & (d["bad"] == 0), "profit"] = d["amount"] * NET_MARGIN * d["duration"] / 12
    d.loc[a & (d["bad"] == 1), "profit"] = -d["amount"] * LGD
    g = (d.groupby(["purpose", "term"])
           .agg(applications=("bad", "size"), approval_rate=("approved", "mean"), bad_rate=("bad", "mean"),
                profit_per_application=("profit", "mean"))
           .reset_index())
    g = g[g["applications"] >= MIN_SEGMENT].copy()
    overall_bad = df["bad"].mean()
    overall_approval = approved.mean()

    def recommend(r):
        if r.approval_rate >= overall_approval and r.bad_rate <= overall_bad and r.profit_per_application > 0:
            return "Target", "approved often, low risk, profitable"
        if r.profit_per_application < 0:
            return "Avoid", "loses money under the strategy"
        if r.approval_rate < overall_approval / 2:
            return "Avoid", "most applicants would be declined"
        return "Neutral", "mixed: keep in general campaigns"

    g[["recommendation", "reason"]] = g.apply(lambda r: pd.Series(recommend(r)), axis=1)
    for c in ["approval_rate", "bad_rate"]:
        g[c] = g[c].round(3)
    g["profit_per_application"] = g["profit_per_application"].round(1)
    return g.sort_values("profit_per_application", ascending=False).reset_index(drop=True)
