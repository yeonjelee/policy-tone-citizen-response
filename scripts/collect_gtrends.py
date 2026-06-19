"""
Google Trends — 웹 + 유튜브 검색 트렌드 (플랫폼 교차검증)  [2026-06-16]
네이버 외 구글·유튜브로도 같은 관심이 재현되나? (외적 타당성)
- gprop="" : 구글 웹 검색,  gprop="youtube" : 유튜브 검색 트렌드
- 2016–2024 (장기라 주별 반환 → 월별 resample), geo=KR
출력: raw/gtrends/<var>_google_monthly.csv, <var>_youtube_monthly.csv

의존성: pip install pytrends
주의: 비공식 API라 과도 호출 시 429. term 사이 sleep. 막히면 잠시 후 재실행.
"""
import time
from pathlib import Path
import pandas as pd

OUT = Path(__file__).parents[1] / "raw" / "gtrends"
OUT.mkdir(parents=True, exist_ok=True)
# 네이버와 맞춘 대표 검색어(플랫폼 비교용 단일어)
KW = {"deposit": "예금 금리", "loan": "대출 금리", "realestate": "부동산",
      "inflation": "물가", "currency": "환율", "invest": "재테크"}


def pull(py, term, gprop):
    py.build_payload([term], timeframe="2016-01-01 2024-12-31", geo="KR", gprop=gprop)
    df = py.interest_over_time()
    if df is None or term not in df:
        return None
    m = df[term].resample("MS").mean()
    out = m.reset_index()
    out.columns = ["period", "value"]
    out["period"] = pd.to_datetime(out["period"]).dt.strftime("%Y-%m")
    return out


if __name__ == "__main__":
    from pytrends.request import TrendReq
    py = TrendReq(hl="ko-KR", tz=540)
    for var, term in KW.items():
        for gprop, tag in [("", "google"), ("youtube", "youtube")]:
            try:
                out = pull(py, term, gprop)
                if out is not None:
                    (OUT / f"{var}_{tag}_monthly.csv").unlink(missing_ok=True)
                    out.rename(columns={"value": var}).to_csv(
                        OUT / f"{var}_{tag}_monthly.csv", index=False, encoding="utf-8-sig")
                    print(f"  ✓ {var} [{tag}]: {len(out)}개월")
                time.sleep(3)
            except Exception as e:
                print(f"  ✗ {var} [{tag}]: {e} (429면 잠시 후 재실행)")
                time.sleep(10)
    print(f"\n→ {OUT}/")
