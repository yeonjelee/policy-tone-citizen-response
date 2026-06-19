"""
응용 백테스트 — 정책 결정 직후 '관심 리프트'를 마케팅 타이밍 신호로 정량화  [2026-06-16]
매파(긴축) vs 비둘기(완화) 결정으로 나눠, 결정 직후 1주 검색 리프트(%)를 산출.
→ "매파 결정 +0~+7일에 X상품 광고 시 관심 +N%" = 타이밍 ROI 프록시.

입력: processed/events/policy_events.csv(tone), raw/naver_trends/search_*_daily.csv
출력: processed/analysis/backtest_timing.csv + 콘솔
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).parents[1]
NAVER = ROOT / "raw/naver_trends"
OUTD = ROOT / "processed/analysis"
KS = ["deposit", "loan", "realestate", "inflation", "currency", "invest"]


def run():
    OUTD.mkdir(parents=True, exist_ok=True)
    ev = pd.read_csv(ROOT / "processed/events/policy_events.csv")
    ev["date"] = pd.to_datetime(ev["date"])
    mpb = ev[(ev["source"] == "mpb") & ev["tone"].notna()].copy()
    S = None
    for k in KS:
        f = NAVER / f"search_{k}_daily.csv"
        if not f.exists():
            continue
        d = pd.read_csv(f); d["date"] = pd.to_datetime(d["period"])
        d = d.rename(columns={d.columns[1]: k})[["date", k]]
        S = d if S is None else S.merge(d, on="date", how="outer")
    if S is None:
        print("일별 검색 없음 → collect_naver_daily.py 먼저"); return
    S = S.sort_values("date").set_index("date")

    def lift(events, k):
        vals = []
        for e in events:
            base = [S[k].get(e + pd.Timedelta(days=o)) for o in range(-10, 0)]
            base = np.nanmean([b for b in base if pd.notna(b)])
            post = [S[k].get(e + pd.Timedelta(days=o)) for o in range(0, 7)]
            post = np.nanmean([b for b in post if pd.notna(b)])
            if base and post and not np.isnan(base) and base > 0:
                vals.append(post / base * 100 - 100)
        return round(np.mean(vals), 1) if vals else None

    hawk = mpb[mpb["tone"] > 0]["date"].tolist()
    dove = mpb[mpb["tone"] < 0]["date"].tolist()
    rows = []
    for k in KS:
        if k not in S:
            continue
        rows.append({"상품축": k, f"매파결정후1주(%)": lift(hawk, k),
                     f"비둘기결정후1주(%)": lift(dove, k),
                     "매파이벤트수": len(hawk), "비둘기이벤트수": len(dove)})
    res = pd.DataFrame(rows)
    (OUTD / "backtest_timing.csv").unlink(missing_ok=True)
    res.to_csv(OUTD / "backtest_timing.csv", index=False, encoding="utf-8-sig")
    print("정책 결정 직후 1주 검색 리프트(직전10일 대비 %) — 마케팅 타이밍 신호:")
    print(res.to_string(index=False))
    print("\n해석: 리프트가 큰 (상품×기조) 조합 = 그 결정 직후가 해당 상품 광고 적기.")
    print(f"→ {OUTD/'backtest_timing.csv'}")


if __name__ == "__main__":
    run()
