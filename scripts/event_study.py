"""
일별 이벤트 스터디 — 정책일(0일) 기준 시민 검색 반응 + 정책→기사→검색 순서  [2026-06-16]

질문: 정책 결정 '직후' 시민 검색이 얼마나 빨리 튀나? 그리고 시민은
      정책 발표에 직접 반응하나, 기사 보도를 거쳐 반응하나?

방법:
  (A) 이벤트 스터디: 각 통화정책 결정일 e 를 0일로, [-10, +30]일 일별 검색을
      직전 10일 평균=100 으로 지수화 → 이벤트 평균 → 반응 곡선·피크일.
  (B) 정책→기사→검색 순서: 일별 기사량 vs 일별 검색의 시차상관(news leads search?).

입력: processed/events/policy_events.csv, raw/naver_trends/search_*_daily.csv,
      raw/news/articles.csv
출력: processed/analysis/event_study_search.csv, event_leadlag.csv
의존성: pandas, scipy
"""
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).parents[1]
NAVER = ROOT / "raw/naver_trends"
OUTD = ROOT / "processed/analysis"
KS = ["deposit", "loan", "realestate", "inflation", "currency", "invest"]
PRE, POST = 10, 30


def load_daily_search():
    out = None
    for k in KS:
        f = NAVER / f"search_{k}_daily.csv"
        if not f.exists():
            continue
        d = pd.read_csv(f)
        d["date"] = pd.to_datetime(d["period"])
        d = d.rename(columns={d.columns[1]: k})[["date", k]]
        out = d if out is None else out.merge(d, on="date", how="outer")
    return out.sort_values("date").reset_index(drop=True) if out is not None else None


def run():
    OUTD.mkdir(parents=True, exist_ok=True)
    ev = pd.read_csv(ROOT / "processed/events/policy_events.csv")
    ev["date"] = pd.to_datetime(ev["date"])
    mpb = ev[ev["source"] == "mpb"]["date"].tolist()

    S = load_daily_search()
    if S is None:
        print("일별 검색 없음 → 먼저: python scripts/collect_naver_daily.py")
        return
    S = S.set_index("date")

    # (A) 이벤트 스터디
    rel = range(-PRE, POST + 1)
    acc = {k: {t: [] for t in rel} for k in KS}
    for e in mpb:
        for k in KS:
            if k not in S:
                continue
            base = [S[k].get(pd.Timestamp(e) + pd.Timedelta(days=o)) for o in range(-PRE, 0)]
            base = np.nanmean([b for b in base if pd.notna(b)]) if any(pd.notna(base)) else np.nan
            if not base or np.isnan(base) or base == 0:
                continue
            for t in rel:
                v = S[k].get(pd.Timestamp(e) + pd.Timedelta(days=t))
                if pd.notna(v):
                    acc[k][t].append(v / base * 100)
    rows = []
    for t in rel:
        r = {"rel_day": t}
        for k in KS:
            vals = acc[k][t]
            r[k] = round(np.mean(vals), 1) if vals else None
        rows.append(r)
    es = pd.DataFrame(rows)
    (OUTD / "event_study_search.csv").unlink(missing_ok=True)
    es.to_csv(OUTD / "event_study_search.csv", index=False, encoding="utf-8-sig")

    print("정책 결정일(0) 기준 검색 지수(직전10일=100) — 피크일:")
    for k in KS:
        if k in es and es[k].notna().any():
            post = es[es["rel_day"].between(0, POST)]
            pk = post.loc[post[k].idxmax()]
            print(f"  {k:11}: 피크 +{int(pk['rel_day'])}일  지수 {pk[k]:.0f}  (t=0 {es.loc[es.rel_day==0,k].iloc[0]:.0f})")

    # (B) 정책→기사→검색 순서: 일별 기사량 vs 검색 시차상관
    art = pd.read_csv(ROOT / "raw/news/articles.csv", dtype=str)
    art["date"] = pd.to_datetime(art["date"].str[:8], format="%Y%m%d", errors="coerce")
    topicmap = {"loan": ["loan"], "realestate": ["realestate"], "inflation": ["inflation", "monetary"],
                "deposit": ["deposit"], "currency": ["currency"], "invest": ["invest"]}
    ll = []
    for k in KS:
        if k not in S:
            continue
        news = art[art["topic"].isin(topicmap[k])].groupby("date").size().rename("news")
        m = pd.concat([S[k].rename("search"), news], axis=1).dropna()
        if len(m) < 60:
            continue
        best = None
        for lag in range(-7, 8):  # lag>0: 기사가 검색을 선행
            x = m["news"]; y = m["search"].shift(-lag)
            p = pd.concat([x, y], axis=1).dropna()
            if len(p) < 60:
                continue
            rho = spearmanr(p.iloc[:, 0], p.iloc[:, 1])[0]
            if best is None or rho > best[1]:
                best = (lag, rho)
        if best:
            ll.append({"topic": k, "best_lag(기사→검색,일)": best[0], "rho": round(best[1], 2)})
    lldf = pd.DataFrame(ll)
    (OUTD / "event_leadlag.csv").unlink(missing_ok=True)
    lldf.to_csv(OUTD / "event_leadlag.csv", index=False, encoding="utf-8-sig")
    print("\n[정책→기사→검색] 기사량이 검색을 선행하는 시차(일, +면 기사가 먼저):")
    print(lldf.to_string(index=False))
    print(f"\n→ {OUTD}/ event_study_search.csv, event_leadlag.csv")


if __name__ == "__main__":
    run()
