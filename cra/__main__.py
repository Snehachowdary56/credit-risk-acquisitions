"""python -m cra  ->  writes output/credit_strategy.xlsx, output/credit_strategy_briefing.pptx, charts and summary.md"""
import argparse
from pathlib import Path

from cra import pipeline, report


def main() -> None:
    p = argparse.ArgumentParser(description="Credit risk acquisitions: scorecard and adjudication strategy")
    p.add_argument("--out", type=Path, default=Path("output"))
    a = p.parse_args()
    r = pipeline.run()
    imgs = report.charts(r, a.out)
    report.excel(r, a.out / "credit_strategy.xlsx")
    report.powerpoint(r, imgs, a.out / "credit_strategy_briefing.pptx")
    scored = r.df.assign(score=r.oof["score"], pd=r.oof["pd"].round(4))
    scored[["application_id", "purpose", "duration", "amount", "age", "status", "credit_history", "bad", "score", "pd"]].to_csv(
        a.out / "scored_applications.csv", index=False)
    md = report.markdown(r)
    (a.out / "summary.md").write_text(md)
    print(md)
    print(f"\nWrote {a.out}/credit_strategy.xlsx, {a.out}/credit_strategy_briefing.pptx")


if __name__ == "__main__":
    main()
