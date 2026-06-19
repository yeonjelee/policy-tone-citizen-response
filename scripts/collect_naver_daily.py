"""
네이버 데이터랩 검색어 트렌드 — '일별' 재수집 (이벤트 스터디용)  [2026-06-16]
기존 월별과 별개로 일별(timeUnit=date) 다운로드. 연 단위로 나눠 요청(일별 안정성).
출력: raw/naver_trends/search_<var>_daily.csv (period=YYYY-MM-DD, value)
API 키: .env 의 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET
"""
import os, json, time
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[1] / ".env")
CID, CSEC = os.getenv("NAVER_CLIENT_ID"), os.getenv("NAVER_CLIENT_SECRET")
API = "https://openapi.naver.com/v1/datalab/search"
OUT = Path(__file__).parents[1] / "raw" / "naver_trends"
OUT.mkdir(parents=True, exist_ok=True)

KEYWORDS = {
    "search_deposit": ["예금 금리", "정기예금"], "search_loan": ["대출 금리", "주택담보대출"],
    "search_realestate": ["부동산", "아파트 매매"], "search_inflation": ["물가", "인플레이션"],
    "search_currency": ["환율", "달러 환율"], "search_invest": ["재테크", "투자"],
}


def fetch(var, kws, sd, ed):
    h = {"X-Naver-Client-Id": CID, "X-Naver-Client-Secret": CSEC, "Content-Type": "application/json"}
    body = {"startDate": sd, "endDate": ed, "timeUnit": "date",
            "keywordGroups": [{"groupName": var, "keywords": kws}]}
    r = requests.post(API, headers=h, data=json.dumps(body), timeout=30)
    r.raise_for_status()
    return pd.DataFrame(r.json()["results"][0]["data"])  # period, ratio


if __name__ == "__main__":
    if not CID or not CSEC:
        raise SystemExit(".env 에 NAVER_CLIENT_ID/SECRET 필요")
    for var, kws in KEYWORDS.items():
        frames = []
        for y in range(2016, 2025):
            try:
                d = fetch(var, kws, f"{y}-01-01", f"{y}-12-31")
                frames.append(d); time.sleep(0.3)
            except Exception as e:
                print(f"  [{var} {y}] 오류 {e}")
        if not frames:
            continue
        df = pd.concat(frames).drop_duplicates("period").sort_values("period")
        df.columns = ["period", var]
        (OUT / f"{var}_daily.csv").unlink(missing_ok=True)
        df.to_csv(OUT / f"{var}_daily.csv", index=False, encoding="utf-8-sig")
        print(f"  ✓ {var}: {len(df)}일")
    print(f"\n→ {OUT}/ (search_*_daily.csv)")
