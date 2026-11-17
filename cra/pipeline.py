"""Runs the whole analysis and returns every table the reports need."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import train_test_split

from cra import data, monitoring, scorecard, segments, strategy, validate


@dataclass
class Results:
    df: pd.DataFrame
    oof: pd.DataFrame
    iv: pd.DataFrame
    points: pd.DataFrame
    model_metrics: pd.DataFrame
    cutoffs: pd.DataFrame
    recommended: pd.Series
    champ_vs_chal: pd.DataFrame
    swap: pd.DataFrame
    segments: dict
    psi: pd.DataFrame
    features: list
    matched_cut: int
    sensitivity: pd.DataFrame


def run(df: pd.DataFrame | None = None) -> Results:
    df = data.load() if df is None else df
    oof = validate.out_of_fold(df)
    model_metrics = pd.DataFrame([
        {"model": "Scorecard (WoE logistic regression)", **validate.metrics(df["bad"], oof["pd"])},
        {"model": "Challenger model (gradient boosting)", **validate.metrics(df["bad"], oof["pd_gbm"])},
    ])

    final, iv = scorecard.fit(df)
    iv = iv.assign(strength=iv["iv"].map(__import__("cra.woe", fromlist=["iv_strength"]).iv_strength), iv=iv["iv"].round(3))

    scores = oof["score"]
    cutoffs = strategy.cutoff_table(df, scores)
    recommended = strategy.best_cutoff(cutoffs)

    champion = strategy.champion_policy(df)
    cut = strategy.matched_cutoff(scores, champion.mean())
    challenger = scores >= cut
    champ_vs_chal = pd.DataFrame([
        {"strategy": "Champion: policy rules only", **strategy.economics(df, champion)},
        {"strategy": f"Challenger: scorecard cutoff {cut} (same approval rate)", **strategy.economics(df, challenger)},
        {"strategy": f"Recommended: scorecard cutoff {int(recommended['cutoff'])} (max profit)",
         **strategy.economics(df, scores >= recommended["cutoff"])},
    ])
    swap = strategy.swap_set(df, champion, challenger)
    segs = segments.by_segment(df, scores >= recommended["cutoff"], oof["pd"])

    # Stability: development sample vs a later "recent applications" sample (hold-out split as a stand-in)
    dev, recent = train_test_split(df, test_size=0.3, stratify=df["bad"], random_state=7)
    dev_model, _ = scorecard.fit(dev)
    rows = [{"variable": "score", "psi": round(monitoring.psi(pd.Series(dev_model.score(dev)), pd.Series(dev_model.score(recent))), 4)}]
    rows += [{"variable": f, "psi": round(monitoring.psi(dev[f], recent[f]), 4)} for f in dev_model.features[:6]]
    psi = pd.DataFrame(rows).assign(status=lambda t: t["psi"].map(monitoring.status))

    return Results(df, oof, iv, final.points_table(), model_metrics, cutoffs, recommended, champ_vs_chal, swap, segs,
                   psi, final.features, cut, strategy.sensitivity(df, scores))
