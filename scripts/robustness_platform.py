"""
플랫폼 교차검증 — 네이버 vs 구글 vs 유튜브 (외적 타당성)  [2026-06-16]
같은 관심 신호가 플랫폼 간 일치하나? 헤드라인(긴축→검색)이 구글에서도 재현되나?
입력: raw/naver_trends/search_*_monthly.csv, raw/gtrends/*_google/youtube_monthly.csv,
      processed/tone/tone_monthly.csv
출력: processed/analysis/platform_robustness.csv + 콘솔
"""
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).parents[1]
NAVER = ROOT / "raw/naver_trends"
G = ROOT / "raw/gtrends"
KS = ["deposit", "loan", "realestate", "inflation", "currency", "invest"]


def load(path, var):
    if not path.exists():
        return None
    d = pd.read_csv(path)
    d["period"] = d["period"].astype(str).str[:7]
    return d.rename(columns={d.columns[1]: var})[["period", var]]


def run():
    tone = pd.read_csv(ROOT / "processed/tone/tone_monthly.csv")
    tone["period"] = tone["period"].astype(str).str[:7]
    tone["tight"] = tone[["tone_inflation", "tone_growth", "tone_finstab"]].mean(axis=1)
    rows = []
    for k in KS:
        nv = load(NAVER / f"search_{k}_monthly.csv", "naver")
        gg = load(G / f"{k}_google_monthly.csv", "google")
        yt = load(G / f"{k}_youtube_monthly.csv", "youtube")
        if nv is None:
            continue
        m = nv
        for x in (gg, yt):
            if x is not None:
                m = m.merge(x, on="period", how="inner")
        m = m.merge(tone[["period", "tight"]], on="period", how="inner")
        rec = {"검색축": k}
        if "google" in m:
            rec["naver~google"] = round(spearmanr(m["naver"], m["google"])[0], 2)
            rec["긴축~구글검색"] = round(spearmanr(m["tight"], m["google"])[0], 2)
        if "youtube" in m:
            rec["naver~youtube"] = round(spearmanr(m["naver"], m["youtube"])[0], 2)
        rec["긴축~네이버검색"] = round(spearmanr(m["tight"], m["naver"])[0], 2)
        rows.append(rec)
    res = pd.DataFrame(rows)
    (ROOT / "processed/analysis/platform_robustness.csv").unlink(missing_ok=True)
    res.to_csv(ROOT / "processed/analysis/platform_robustness.csv", index=False, encoding="utf-8-sig")
    print("플랫폼 일치도 + 헤드라인(긴축→검색) 재현:")
    print(res.to_string(index=False))
    print("\n해석: naver~google 높으면 관심 신호 플랫폼 일치. '긴축~구글'이 '긴축~네이버'와 같은 부호면 발견 재현.")
    print("→ processed/analysis/platform_robustness.csv")


if __name__ == "__main__":
    run()
