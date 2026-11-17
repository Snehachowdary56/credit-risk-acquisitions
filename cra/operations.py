"""Operations: a three-band strategy (auto-approve / refer to manual review / auto-decline) and how much
review work it creates for the adjudication team (operational effectiveness)."""
from __future__ import annotations

import pandas as pd

# Operating assumptions (stated, not from the data)
MINUTES_PER_REVIEW = 20          # an adjudicator's manual review of one referred application
MONTHLY_APPLICATIONS = 10_000    # application volume used to size the review queue
WORKDAYS_PER_MONTH = 21


def bands(scores: pd.Series, approve_at: int, decline_below: int) -> pd.Series:
    out = pd.Series("Refer to manual review", index=scores.index)
    out[scores >= approve_at] = "Auto-approve"
    out[scores < decline_below] = "Auto-decline"
    return out


def band_table(df: pd.DataFrame, band: pd.Series) -> pd.DataFrame:
    t = (df.assign(band=band).groupby("band")
           .agg(applications=("bad", "size"), bad_rate=("bad", "mean"), avg_amount=("amount", "mean"))
           .reindex(["Auto-approve", "Refer to manual review", "Auto-decline"]).fillna(0).reset_index())
    t["share"] = (t["applications"] / len(df)).round(3)
    t["bad_rate"] = t["bad_rate"].round(3)
    t["avg_amount"] = t["avg_amount"].round(0)
    return t[["band", "applications", "share", "bad_rate", "avg_amount"]]


def workload(table: pd.DataFrame) -> dict:
    refer_share = float(table.loc[table["band"] == "Refer to manual review", "share"].iloc[0])
    reviews_month = refer_share * MONTHLY_APPLICATIONS
    hours_month = reviews_month * MINUTES_PER_REVIEW / 60
    return {
        "auto_decision_rate": round(1 - refer_share, 3),
        "referral_rate": round(refer_share, 3),
        "reviews_per_month": round(reviews_month),
        "reviews_per_day": round(reviews_month / WORKDAYS_PER_MONTH),
        "review_hours_per_month": round(hours_month),
        "adjudicators_needed_fte": round(hours_month / (WORKDAYS_PER_MONTH * 7), 1),
    }


def refer_band_options(df: pd.DataFrame, scores: pd.Series, approve_at: int, widths=(0, 20, 40, 60)) -> pd.DataFrame:
    """Wider refer band = more cases for humans. Shows the trade-off Operations and Risk agree on."""
    rows = []
    for w in widths:
        t = band_table(df, bands(scores, approve_at, approve_at - w))
        ref = t[t["band"] == "Refer to manual review"].iloc[0]
        t["applications"] = t["applications"].astype(int)
        rows.append({"refer_band": f"{approve_at - w}-{approve_at - 1}" if w else "none",
                     **workload(t), "refer_bad_rate": None if w == 0 else ref["bad_rate"]})
    return pd.DataFrame(rows)
