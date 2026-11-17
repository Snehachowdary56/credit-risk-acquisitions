"""Application scorecard: logistic regression on WoE features, scaled to points (600 points = 50:1 odds, 20 PDO)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from cra.data import NUMERIC, PROTECTED
from cra.woe import Binning, fit_binning

BASE_SCORE, BASE_ODDS, PDO = 600, 50, 20
FACTOR = PDO / np.log(2)
OFFSET = BASE_SCORE - FACTOR * np.log(BASE_ODDS)


@dataclass
class Scorecard:
    binnings: dict[str, Binning]
    model: LogisticRegression
    features: list[str]

    def woe_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({f: self.binnings[f].transform(df[f]) for f in self.features}, index=df.index)

    def pd_(self, df: pd.DataFrame) -> np.ndarray:
        """Probability of default (bad) for each application."""
        return self.model.predict_proba(self.woe_frame(df))[:, 1]

    def score(self, df: pd.DataFrame) -> np.ndarray:
        """Points: higher = safer. ln(good:bad odds) = -logit(PD)."""
        p = np.clip(self.pd_(df), 1e-6, 1 - 1e-6)
        return np.round(OFFSET + FACTOR * np.log((1 - p) / p)).astype(int)

    def points_table(self) -> pd.DataFrame:
        """Points per attribute, so an adjudicator can see why an application scored as it did."""
        n = len(self.features)
        rows = []
        for f, coef in zip(self.features, self.model.coef_[0]):
            for bin_label, woe in self.binnings[f].woe.items():
                pts = -(coef * woe + self.model.intercept_[0] / n) * FACTOR + OFFSET / n
                rows.append({"characteristic": f, "attribute": bin_label, "woe": round(woe, 3), "points": round(pts)})
        return pd.DataFrame(rows)


def candidate_features(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in ("application_id", "bad", *PROTECTED)]


def fit(train: pd.DataFrame, min_iv: float = 0.02, C: float = 0.5) -> tuple[Scorecard, pd.DataFrame]:
    binnings = {f: fit_binning(train[f], train["bad"], f in NUMERIC) for f in candidate_features(train)}
    iv = pd.DataFrame({"feature": list(binnings), "iv": [b.iv for b in binnings.values()]}).sort_values("iv", ascending=False)
    features = iv.loc[iv["iv"] >= min_iv, "feature"].tolist()
    X = pd.DataFrame({f: binnings[f].transform(train[f]) for f in features}, index=train.index)
    model = LogisticRegression(C=C, max_iter=1000).fit(X, train["bad"])
    return Scorecard(binnings, model, features), iv
