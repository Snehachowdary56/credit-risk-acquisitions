"""Management reporting: Excel workbook, PowerPoint briefing, charts and a Markdown summary."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
from pptx import Presentation
from pptx.util import Inches, Pt

from cra.pipeline import Results
from cra.strategy import LGD, NET_MARGIN

NAVY = "1F3A68"


def charts(r: Results, out: Path) -> dict[str, Path]:
    out.mkdir(parents=True, exist_ok=True)
    paths = {}
    t = r.cutoffs
    fig, ax1 = plt.subplots(figsize=(8, 4.2))
    ax1.plot(t["cutoff"], t["approval_rate"] * 100, color="#1F3A68", lw=2, label="Approval rate %")
    ax1.plot(t["cutoff"], t["bad_rate"] * 100, color="#C0392B", lw=2, label="Bad rate of approved %")
    ax1.set_xlabel("Score cutoff (approve at or above)")
    ax1.set_ylabel("%")
    ax2 = ax1.twinx()
    ax2.bar(t["cutoff"], t["profit"] / 1000, width=6, alpha=0.25, color="#2E8B57", label="Profit (000s DM)")
    ax2.set_ylabel("Profit, thousands DM")
    ax1.axvline(r.recommended["cutoff"], ls="--", color="grey")
    ax1.set_title("Cutoff strategy: approval rate vs bad rate vs profit")
    h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="lower left", fontsize=8)
    fig.tight_layout(); paths["cutoff"] = out / "cutoff_strategy.png"; fig.savefig(paths["cutoff"], dpi=150); plt.close(fig)

    s = r.segments["purpose"].sort_values("applications")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    y = range(len(s))
    ax.barh([i + 0.2 for i in y], s["approval_rate"] * 100, height=0.4, color="#1F3A68", label="Approval rate %")
    ax.barh([i - 0.2 for i in y], s["bad_rate_all"] * 100, height=0.4, color="#C0392B", label="Bad rate (all applications) %")
    ax.set_yticks(list(y)); ax.set_yticklabels(s["segment"])
    ax.set_xlabel("%"); ax.set_title("Application outcomes by loan purpose (recommended strategy)"); ax.legend(fontsize=8)
    fig.tight_layout(); paths["segments"] = out / "segments_purpose.png"; fig.savefig(paths["segments"], dpi=150); plt.close(fig)
    return paths


def _sheet(wb: Workbook, title: str, df: pd.DataFrame, note: str | None = None):
    ws = wb.create_sheet(title)
    if note:
        ws.append([note]); ws["A1"].font = Font(italic=True); ws.append([])
    start = ws.max_row + 1 if note else 1
    for i, row in enumerate(dataframe_to_rows(df, index=False, header=True)):
        ws.append(row)
        if i == 0:
            for c in ws[ws.max_row]:
                c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor=NAVY)
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = max(12, min(55, max(len(str(c.value or "")) for c in col) + 2))
    return ws, start


def excel(r: Results, path: Path) -> Path:
    wb = Workbook(); wb.remove(wb.active)
    rec = r.recommended
    summary = pd.DataFrame({
        "metric": ["Applications", "Bad rate (all)", "Scorecard Gini (5-fold CV)", "Recommended cutoff", "Approval rate",
                   "Bad rate of approved", "Expected loss (DM)", "Profit (DM)", "Assumptions"],
        "value": [len(r.df), round(r.df["bad"].mean(), 3), r.model_metrics.loc[0, "gini"], int(rec["cutoff"]),
                  rec["approval_rate"], rec["bad_rate"], int(rec["expected_loss"]), int(rec["profit"]),
                  f"LGD {LGD:.0%}, net margin {NET_MARGIN:.0%}/yr"]})
    _sheet(wb, "Summary", summary)
    ws, start = _sheet(wb, "Cutoff_Strategy", r.cutoffs, "Approve at or above the cutoff. Profit = net revenue on goods - expected loss on bads.")
    chart = LineChart(); chart.title = "Approval rate and bad rate by cutoff"; chart.y_axis.title = "rate"; chart.x_axis.title = "cutoff"
    n = len(r.cutoffs)
    for col in (3, 4):
        chart.add_data(Reference(ws, min_col=col, min_row=start, max_row=start + n), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=start + 1, max_row=start + n))
    ws.add_chart(chart, "N3")
    _sheet(wb, "Champion_Challenger", r.champ_vs_chal)
    _sheet(wb, "Business_Case_Sensitivity", r.sensitivity, "Profit-maximizing cutoff under different margin and loss-given-default assumptions")
    _sheet(wb, "Swap_Set", r.swap)
    _sheet(wb, "Operations_Bands", r.ops_bands,
           f"Auto-approve >= {r.approve_at}, refer {r.decline_below}-{r.approve_at - 1}, auto-decline < {r.decline_below}")
    _sheet(wb, "Operations_Workload", pd.DataFrame([r.ops_workload]),
           "Assumes 10,000 applications a month, 20 minutes per manual review, 21 workdays, 7 review hours a day")
    _sheet(wb, "Refer_Band_Options", r.ops_options, "Wider refer band = more manual reviews; choose with Operations")
    _sheet(wb, "Marketing_Targeting", r.targeting, "Segments with 25+ applications; profit per application under the recommended strategy")
    for name, t in r.segments.items():
        _sheet(wb, f"Seg_{name}"[:31], t)
    _sheet(wb, "Model_Performance", r.model_metrics)
    _sheet(wb, "Information_Value", r.iv)
    _sheet(wb, "Scorecard_Points", r.points)
    _sheet(wb, "Monitoring_PSI", r.psi, "PSI < 0.10 stable, 0.10-0.25 monitor, > 0.25 investigate")
    path.parent.mkdir(parents=True, exist_ok=True); wb.save(path)
    return path


def powerpoint(r: Results, imgs: dict[str, Path], path: Path) -> Path:
    prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    def slide(title: str, bullets: list[str] | None = None, image: Path | None = None):
        s = prs.slides.add_slide(blank)
        tb = s.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.3), Inches(0.9)).text_frame
        tb.text = title; tb.paragraphs[0].runs[0].font.size = Pt(30); tb.paragraphs[0].runs[0].font.bold = True
        if image:
            s.shapes.add_picture(str(image), Inches(0.4), Inches(1.5), width=Inches(7.4))
        if bullets:
            left = Inches(8.0) if image else Inches(0.6)
            body = s.shapes.add_textbox(left, Inches(1.5), Inches(4.9 if image else 12), Inches(5.5)).text_frame
            body.word_wrap = True
            for i, b in enumerate(bullets):
                p = body.paragraphs[0] if i == 0 else body.add_paragraph()
                p.text = "• " + b; p.font.size = Pt(16); p.space_after = Pt(10)

    rec, cc, m = r.recommended, r.champ_vs_chal, r.model_metrics
    slide("Credit risk acquisitions: scorecard and cutoff strategy", [
        f"{len(r.df):,} consumer credit applications, {r.df['bad'].mean():.0%} bad outcomes",
        f"Application scorecard: Gini {m.loc[0,'gini']} (5-fold cross-validated)",
        f"Recommended cutoff {int(rec['cutoff'])}: approve {rec['approval_rate']:.0%}, bad rate {rec['bad_rate']:.1%} of approved",
        "Business case and champion vs challenger results inside"])
    slide("Cutoff strategy trade-off", [
        f"Profit peaks at cutoff {int(rec['cutoff'])}",
        f"Approval rate {rec['approval_rate']:.0%}, bad rate {rec['bad_rate']:.1%}",
        f"Expected loss {int(rec['expected_loss']):,} DM; profit {int(rec['profit']):,} DM",
        f"Assumptions: LGD {LGD:.0%}, net margin {NET_MARGIN:.0%} per year"], imgs["cutoff"])
    slide("Champion vs challenger", [
        f"{row.strategy}: approval {row.approval_rate:.0%}, bad rate {row.bad_rate:.1%}, loss {int(row.expected_loss):,} DM, profit {int(row.profit):,} DM"
        for row in cc.itertuples()] + [
        f"Swap-ins bad rate {r.swap.iloc[1]['bad_rate']:.0%} vs swap-outs {r.swap.iloc[2]['bad_rate']:.0%}"])
    sens = r.sensitivity
    slide("Business case: sensitivity to assumptions", [
        f"Net margin {row.net_margin:.0%}, LGD {row.lgd:.0%}: best cutoff {row.best_cutoff}, approve {row.approval_rate:.0%}, bad rate {row.bad_rate:.1%}"
        for row in sens.iloc[[0, 4, 8]].itertuples()] + [
        "Higher margins justify approving more applicants; the cutoff should be set with Finance's real margin and LGD"])
    w, ob = r.ops_workload, r.ops_bands.set_index("band")
    slide("Operations: three-band strategy and review workload", [
        f"Auto-approve {r.approve_at}+: {ob.loc['Auto-approve','share']:.0%} of applications, bad rate {ob.loc['Auto-approve','bad_rate']:.1%}",
        f"Refer {r.decline_below}-{r.approve_at - 1} to manual review: {ob.loc['Refer to manual review','share']:.0%}, bad rate {ob.loc['Refer to manual review','bad_rate']:.1%}",
        f"Auto-decline below {r.decline_below}: {ob.loc['Auto-decline','share']:.0%}, bad rate {ob.loc['Auto-decline','bad_rate']:.1%}",
        f"Auto-decision rate {w['auto_decision_rate']:.0%}; about {w['reviews_per_day']} reviews a day, {w['adjudicators_needed_fte']} adjudicators (10,000 applications/month)",
        "A wider refer band doubles the review workload; agree the band with Operations"])
    tg = r.targeting
    slide("Marketing: which segments to target", [
        "Target: " + "; ".join(f"{x.purpose}, {x.term}" for x in tg[tg.recommendation == "Target"].itertuples()),
        "Avoid: " + "; ".join(f"{x.purpose}, {x.term}" for x in tg[tg.recommendation == "Avoid"].itertuples()),
        "Ranked by profit per application under the recommended strategy (segments with 25+ applications)"])
    slide("Application outcomes by segment", [
        "Approval and bad rates by purpose, age band, term and amount (SQL)",
        "Used to check the strategy is not concentrated in one segment"], imgs["segments"])
    slide("Risk governance", [
        "Sex/marital status, foreign-worker status and age are excluded from the model; age is used only for monitoring",
        f"Population stability (PSI) of the score: {r.psi.loc[0,'psi']} ({r.psi.loc[0,'status']})",
        "Every attribute's points are published in the workbook, so each decision can be explained",
        "Limitations: 1,000 historical applications; assumptions for LGD and margin; needs validation on current data"])
    path.parent.mkdir(parents=True, exist_ok=True); prs.save(path)
    return path


def markdown(r: Results) -> str:
    rec, m = r.recommended, r.model_metrics
    lines = ["## Credit risk acquisitions: results", "",
             "| | |", "|---|---|",
             f"| Applications | {len(r.df):,} ({r.df['bad'].mean():.0%} bad) |",
             f"| Scorecard (WoE logistic regression), 5-fold CV | AUC {m.loc[0,'auc']}, Gini {m.loc[0,'gini']}, KS {m.loc[0,'ks']} |",
             f"| Challenger model (gradient boosting), 5-fold CV | AUC {m.loc[1,'auc']}, Gini {m.loc[1,'gini']}, KS {m.loc[1,'ks']} |",
             f"| Recommended cutoff | {int(rec['cutoff'])}: approval {rec['approval_rate']:.1%}, bad rate {rec['bad_rate']:.1%}, loss rate {rec['loss_rate']:.2%}, profit {int(rec['profit']):,} DM |",
             f"| Score stability (PSI) | {r.psi.loc[0,'psi']} ({r.psi.loc[0,'status']}) |", "",
             "### Champion vs challenger", "", r.champ_vs_chal.to_markdown(index=False), "",
             "### Swap set", "", r.swap.to_markdown(index=False), "",
             "### Business case sensitivity (profit-maximizing cutoff)", "", r.sensitivity.to_markdown(index=False), "",
             "### Operations: three-band strategy", "", r.ops_bands.to_markdown(index=False), "",
             "Workload (10,000 applications/month, 20 min per review): " + ", ".join(f"{k} {v}" for k, v in r.ops_workload.items()), "",
             "### Refer band options", "", r.ops_options.to_markdown(index=False), "",
             "### Marketing targeting", "", r.targeting.to_markdown(index=False), "",
             "### Outcomes by purpose", "", r.segments["purpose"].to_markdown(index=False), ""]
    return "\n".join(lines)
