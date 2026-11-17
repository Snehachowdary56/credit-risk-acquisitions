"""Population Stability Index (PSI): has the applicant population shifted since the model was built?
Rule of thumb: < 0.10 stable, 0.10-0.25 monitor, > 0.25 investigate / redevelop."""
from __future__ import annotations

import numpy as np
import pandas as pd


def psi(expected: pd.Series, actual: pd.Series, bins: int = 10) -> float:
    if expected.dtype.kind in "if":
        edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
        edges[0], edges[-1] = -np.inf, np.inf
        e = pd.cut(expected, edges).value_counts(normalize=True, sort=False)
        a = pd.cut(actual, edges).value_counts(normalize=True, sort=False)
    else:
        e = expected.value_counts(normalize=True)
        a = actual.value_counts(normalize=True).reindex(e.index, fill_value=0)
    e, a = e.clip(lower=1e-4), a.clip(lower=1e-4)
    return float(((a - e) * np.log(a / e)).sum())


def status(value: float) -> str:
    return "stable" if value < 0.10 else "monitor" if value < 0.25 else "investigate"
