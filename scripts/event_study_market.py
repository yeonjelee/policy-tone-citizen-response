"""
시장 이벤트 스터디 — 정책일에 환율·KOSPI가 '즉시' 반응하나  [2026-06-16]
전달 위계 ① 시장(즉시). 검색(수일)·행동(수개월)과 시간축 비교.

방법: 금통위 결정일 0일, [-5,+5]일 일별 '절대 변동'(환율 |일간%변화|, KOSPI |일간수익률|)을
      이벤트 평균. 0일 부근에 변동이 몰리면 = 시장 즉각 반응(비정상변동).

입력: processed/events/policy_events.csv, raw/market/fx_daily.csv, kospi_daily.csv
출력: processed/analysis/event_study_market.csv + 콘솔
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).parents[1]
M = ROOT / "raw/market"
OUTD = ROOT / "processed/analysis"
PRE, POST = 5, 5


def run():
    OUTD.mkdir(parents=True, exist_ok=True)
    ev = pd.read_csv(ROOT / "processed/events/policy_events.csv")
    ev["date"] = pd.to_datetime(ev["date"])
    mpb = ev[ev["source"] == "mpb"]["date"].tolist()

    series = {}
    fp = M / "fx_daily.csv"
    if fp.exists():
        d = pd.read_csv(fp); d["date"] = pd.to_datetime(d["date"])
        d["fx_abs"] = d["value"].pct_change().abs() * 100
        series["환율|변화%|"] = d.set_index("date")["fx_abs"]
    kp = M / "kospi_daily.csv"
    if kp.exists():
        d = pd.read_csv(kp); d["date"] = pd.to_datetime(d["date"])
        series["KOSPI|수익률%|"] = d.set_index("date")["return"].abs()
    if not series:
        print("시장 데이터 없음 → collect_market_daily.py 먼저"); return

    rel = range(-PRE, POST + 1)
    rows = []
    for t in rel:
        r = {"rel_day": t}
        for name, s in series.items():
            vals = [s.get(pd.Timestamp(e) + pd.Timedelta(days=t)) for e in mpb]
            vals = [v for v in vals if pd.notna(v)]
            r[name] = round(np.mean(vals), 3) if vals else None
        rows.append(r)
    es = pd.DataFrame(rows)
    (OUTD / "event_study_market.csv").unlink(missing_ok=True)
    es.to_csv(OUTD / "event_study_market.csv", index=False, encoding="utf-8-sig")
    print("정책 결정일(0) 기준 시장 절대변동 — 평균:")
    print(es.to_string(index=False))
    print("\n해석: 0일(또는 ±1)에 변동이 평소(±5일)보다 크면 = 시장 즉각 반응(전달 위계 ①).")
    print(f"→ {OUTD/'event_study_market.csv'}")


if __name__ == "__main__":
    run()
