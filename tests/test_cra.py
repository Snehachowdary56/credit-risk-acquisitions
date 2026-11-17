import numpy as np
import pandas as pd
import pytest

from cra import data, monitoring, pipeline, scorecard, strategy, validate
from cra.woe import fit_binning, iv_strength


@pytest.fixture(scope="module")
def df():
    return data.load()


@pytest.fixture(scope="module")
def results(df):
    return pipeline.run(df)


def test_data_has_1000_applications_and_30pct_bad(df):
    assert len(df) == 1000
    assert df["bad"].sum() == 300


def test_woe_is_higher_for_safer_bins():
    x = pd.Series(["safe"] * 100 + ["risky"] * 100, name="seg")
    bad = pd.Series([0] * 95 + [1] * 5 + [0] * 60 + [1] * 40)
    b = fit_binning(x, bad, numeric=False)
    assert b.woe["safe"] > 0 > b.woe["risky"]
    assert b.iv > 0.3 and iv_strength(b.iv) == "strong"


def test_numeric_binning_covers_all_values():
    x = pd.Series(np.arange(100), name="n")
    b = fit_binning(x, pd.Series([0, 1] * 50), numeric=True, n_bins=5)
    assert b.bin(pd.Series([-1000, 1000])).notna().all()


def test_protected_attributes_are_not_model_inputs(df):
    sc, _ = scorecard.fit(df)
    assert not set(data.PROTECTED) & set(sc.features)


def test_score_scaling_600_points_at_50_to_1_odds():
    p_bad = 1 / 51
    score = scorecard.OFFSET + scorecard.FACTOR * np.log((1 - p_bad) / p_bad)
    assert round(score) == 600
    p2 = 1 / 101   # odds 100:1 = doubled odds -> +20 points
    assert round(scorecard.OFFSET + scorecard.FACTOR * np.log((1 - p2) / p2)) == 620


def test_higher_score_means_lower_default_rate(results):
    oof, df = results.oof, results.df
    top = df.loc[oof["score"] >= oof["score"].quantile(0.8), "bad"].mean()
    bottom = df.loc[oof["score"] <= oof["score"].quantile(0.2), "bad"].mean()
    assert top < 0.15 < 0.45 < bottom


def test_cross_validated_scorecard_discriminates(results):
    assert results.model_metrics.loc[0, "gini"] > 0.45


def test_cutoff_table_is_monotonic(results):
    t = results.cutoffs
    assert (t["approval_rate"].diff().dropna() <= 0).all()


def test_challenger_beats_champion_at_same_approval_rate(results):
    cc = results.champ_vs_chal
    champ, chal = cc.iloc[0], cc.iloc[1]
    assert abs(champ["approval_rate"] - chal["approval_rate"]) < 0.02
    assert chal["bad_rate"] < champ["bad_rate"]
    assert chal["expected_loss"] < champ["expected_loss"]


def test_swap_outs_are_riskier_than_swap_ins(results):
    s = results.swap.set_index("group")["bad_rate"]
    assert s.iloc[2] > s.iloc[1]


def test_economics_counts_loss_only_on_bads():
    d = pd.DataFrame({"amount": [1000, 1000], "duration": [12, 12], "bad": [0, 1]})
    e = strategy.economics(d, pd.Series([True, True]), lgd=0.5, margin=0.1)
    assert e["expected_loss"] == 500 and e["net_revenue"] == 100 and e["profit"] == -400


def test_psi_detects_shift():
    a = pd.Series(np.random.default_rng(0).normal(0, 1, 5000))
    assert monitoring.psi(a, a.sample(frac=0.5, random_state=1)) < 0.1
    assert monitoring.psi(a, a + 1.0) > 0.25


def test_segments_are_computed_with_sql(results):
    seg = results.segments["age_band"]
    assert seg["applications"].sum() == 1000
    assert set(seg["segment"]) == {"18-24", "25-34", "35-49", "50+"}


def test_reports_are_written(results, tmp_path):
    from cra import report
    imgs = report.charts(results, tmp_path)
    xlsx = report.excel(results, tmp_path / "s.xlsx")
    pptx = report.powerpoint(results, imgs, tmp_path / "s.pptx")
    from openpyxl import load_workbook
    assert "Champion_Challenger" in load_workbook(xlsx).sheetnames
    from pptx import Presentation
    assert len(Presentation(pptx).slides) == 8


def test_three_bands_cover_every_application(results):
    t = results.ops_bands
    assert t["applications"].sum() == 1000
    rates = t.set_index("band")["bad_rate"]
    assert rates["Auto-approve"] < rates["Refer to manual review"] < rates["Auto-decline"]


def test_wider_refer_band_means_more_reviews(results):
    o = results.ops_options
    assert o["reviews_per_month"].is_monotonic_increasing
    assert o.loc[0, "auto_decision_rate"] == 1.0


def test_marketing_targets_are_low_risk_and_profitable(results):
    t = results.targeting
    target = t[t.recommendation == "Target"]
    assert len(target) > 0
    assert (target["bad_rate"] <= results.df["bad"].mean()).all()
    assert (target["profit_per_application"] > 0).all()
