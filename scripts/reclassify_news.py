"""
기존 raw/news/articles.csv 의 press_lean 을 보강된 news_outlets 기준으로 재적용  [2026-06-16]
(재크롤 불필요). + news_quarterly_by_lean.csv 재생성.

실행: python scripts/reclassify_news.py
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from news_outlets import classify_lean

ROOT = Path(__file__).parents[1]
OUT = ROOT / "raw" / "news"
Y_MIN, Y_MAX = 2016, 2024


def run():
    a = pd.read_csv(OUT / "articles.csv", dtype=str)
    a["press_lean"] = a["press"].map(classify_lean)
    a.to_csv(OUT / "articles.csv", index=False, encoding="utf-8-sig")

    a["quarter"] = a["date"].astype(str).str[:4] + "Q" + \
        ((a["date"].astype(str).str[4:6].astype(int) - 1) // 3 + 1).astype(str)
    qs = [f"{y}Q{q}" for y in range(Y_MIN, Y_MAX + 1) for q in range(1, 5)]
    (a.groupby(["quarter", "press_lean"]).size().unstack(fill_value=0)
       .reindex(qs, fill_value=0)).to_csv(OUT / "news_quarterly_by_lean.csv", encoding="utf-8-sig")

    print("재분류 완료. 성향 분포:")
    print(a["press_lean"].value_counts().to_string())


if __name__ == "__main__":
    run()
