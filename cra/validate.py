"""Model validation: discrimination (AUC, Gini, KS) with 5-fold cross-validation, and a gradient-boosting challenger model."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OrdinalEncoder

from cra import scorecard
from cra.data import NUMERIC


def ks(y: np.ndarray, p: np.ndarray) -> float:
    fpr, tpr, _ = roc_curve(y, p)
    return float(np.max(tpr - fpr))


def metrics(y, p) -> dict:
    auc = roc_auc_score(y, p)
    return {"auc": round(auc, 3), "gini": round(2 * auc - 1, 3), "ks": round(ks(y, p), 3)}


def out_of_fold(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Each application is scored by a scorecard that never saw it (5-fold cross-validation)."""
    out = pd.DataFrame(index=df.index, columns=["pd", "score", "pd_gbm"], dtype=float)
    folds = StratifiedKFold(5, shuffle=True, random_state=seed)
    cats = [c for c in scorecard.candidate_features(df) if c not in NUMERIC]
    nums = [c for c in scorecard.candidate_features(df) if c in NUMERIC]
    for tr, te in folds.split(df, df["bad"]):
        train, test = df.iloc[tr], df.iloc[te]
        sc, _ = scorecard.fit(train)
        out.iloc[te, 0] = sc.pd_(test)
        out.iloc[te, 1] = sc.score(test)
        gbm = make_pipeline(
            ColumnTransformer([("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cats)],
                              remainder="passthrough"),
            HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200, random_state=seed))
        gbm.fit(train[cats + nums], train["bad"])
        out.iloc[te, 2] = gbm.predict_proba(test[cats + nums])[:, 1]
    out["score"] = out["score"].astype(int)
    return out
