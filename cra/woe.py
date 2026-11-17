"""Weight of Evidence (WoE) binning and Information Value (IV), the standard way to build credit scorecards."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

EPS = 0.5  # smoothing so an empty good or bad count does not give log(0)


@dataclass
class Binning:
    feature: str
    edges: list[float] | None = None                  # numeric features
    woe: dict = field(default_factory=dict)          # bin label -> WoE
    iv: float = 0.0
    table: pd.DataFrame | None = None

    def bin(self, s: pd.Series) -> pd.Series:
        if self.edges is not None:
            return pd.cut(s, bins=self.edges, include_lowest=True).astype(str)
        return s.astype(str)

    def transform(self, s: pd.Series) -> pd.Series:
        return self.bin(s).map(self.woe).fillna(0.0)


def fit_binning(x: pd.Series, bad: pd.Series, numeric: bool, n_bins: int = 5) -> Binning:
    b = Binning(x.name)
    if numeric:
        qs = np.unique(np.quantile(x, np.linspace(0, 1, n_bins + 1)))
        qs[0], qs[-1] = -np.inf, np.inf
        b.edges = qs.tolist()
    bins = b.bin(x)
    t = pd.DataFrame({"bin": bins, "bad": bad}).groupby("bin", observed=True)["bad"].agg(["count", "sum"])
    t.columns = ["applications", "bads"]
    t["goods"] = t["applications"] - t["bads"]
    dist_good = (t["goods"] + EPS) / (t["goods"].sum() + EPS * len(t))
    dist_bad = (t["bads"] + EPS) / (t["bads"].sum() + EPS * len(t))
    t["bad_rate"] = t["bads"] / t["applications"]
    t["woe"] = np.log(dist_good / dist_bad)
    t["iv"] = (dist_good - dist_bad) * t["woe"]
    b.woe = t["woe"].to_dict()
    b.iv = float(t["iv"].sum())
    b.table = t.reset_index()
    return b


def iv_strength(iv: float) -> str:
    return "unpredictive" if iv < 0.02 else "weak" if iv < 0.1 else "medium" if iv < 0.3 else "strong"
