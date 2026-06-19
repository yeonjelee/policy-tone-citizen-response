"""
네이버 데이터랩 — 연령·성별 인구통계 분해 (타겟 마케팅 응용)  [2026-06-16]
'누가' 반응하나? 각 검색어를 연령대(청년/중년/장년)·성별로 분해.
출력: raw/naver_trends/demo_<var>.csv  (period, group, value)
      processed/analysis/demo_profile.csv (검색어×그룹 평균지수 요약)
API: .env NAVER_CLIENT_ID/SECRET
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
OUTA = Path(__file__).parents[1] / "processed" / "analysis"
OUTA.mkdir(parents=True, exist_ok=True)

KEYWORDS = {"deposit": ["예금 금리", "정기예금"], "loan": ["대출 금리", "주택담보대출"],
            "realestate": ["부동산", "아파트 매매"], "inflation": ["물가", "인플레이션"],
            "currency": ["환율", "달러 환율"], "invest": ["재테크", "투자"]}
# 연령 밴드(네이버 코드) 그룹
AGES = {"청년(19-34)": ["3", "4", "5"], "중년(35-54)": ["6", "7", "8", "9"], "장년(55+)": ["10", "11"]}
GENDERS = {"남": "m", "여": "f"}


def fetch(var, kws, ages=None, gender=None):
    h = {"X-Naver-Client-Id": CID, "X-Naver-Client-Secret": CSEC, "Content-Type": "application/json"}
    body = {"startDate": "2016-01-01", "endDate": "2024-12-31", "timeUnit": "month",
            "keywordGroups": [{"groupName": var, "keywords": kws}]}
    if ages:
        body["ages"] = ages
    if gender:
        body["gender"] = gender
    r = requests.post(API, headers=h, data=json.dumps(body), timeout=30)
    r.raise_for_status()
    return pd.DataFrame(r.json()["results"][0]["data"])


if __name__ == "__main__":
    if not CID:
        raise SystemExit(".env 에 NAVER 키 필요")
    prof = []
    for var, kws in KEYWORDS.items():
        rows = []
        for gname, ages in AGES.items():
            try:
                d = fetch(var, kws, ages=ages); d["group"] = gname; rows.append(d); time.sleep(0.3)
            except Exception as e:
                print(f"  ✗ {var}/{gname}: {e}")
        for gname, g in GENDERS.items():
            try:
                d = fetch(var, kws, gender=g); d["group"] = "성별:" + gname; rows.append(d); time.sleep(0.3)
            except Exception as e:
                print(f"  ✗ {var}/{gname}: {e}")
        if not rows:
            continue
        df = pd.concat(rows)
        df.columns = ["period", "value", "group"]
        (OUT / f"demo_{var}.csv").unlink(missing_ok=True)
        df.to_csv(OUT / f"demo_{var}.csv", index=False, encoding="utf-8-sig")
        for gname, g in df.groupby("group"):
            prof.append({"keyword": var, "group": gname, "mean_index": round(g["value"].astype(float).mean(), 1)})
        print(f"  ✓ {var}: {df['group'].nunique()}개 그룹")
    pd.DataFrame(prof).to_csv(OUTA / "demo_profile.csv", index=False, encoding="utf-8-sig")
    print(f"\n→ raw/naver_trends/demo_*.csv, processed/analysis/demo_profile.csv")
