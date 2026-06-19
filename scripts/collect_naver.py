"""
네이버 데이터랩 검색어 트렌드 수집
수집 항목: 예금금리, 대출금리, 부동산, 물가, 환율, 재테크 (월별 → 분기 평균)
API 키: .env 파일의 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

발급처: https://developers.naver.com/apps/#/register
  → 애플리케이션 등록 → 데이터랩(검색어트렌드) 체크
"""

import os
import json
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[1] / ".env")

CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
API_URL = "https://openapi.naver.com/v1/datalab/search"
OUT_DIR = Path(__file__).parents[1] / "raw" / "naver_trends"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 수집 키워드 정의 (변수명: [검색어 리스트])
KEYWORDS = {
    "search_deposit":     ["예금 금리", "정기예금"],
    "search_loan":        ["대출 금리", "주택담보대출"],
    "search_realestate":  ["부동산", "아파트 매매"],
    "search_inflation":   ["물가", "인플레이션"],
    "search_currency":    ["환율", "달러 환율"],
    "search_invest":      ["재테크", "투자"],
}


def fetch_trend(var_name: str, keywords: list[str]) -> pd.DataFrame:
    """네이버 데이터랩 API 호출 (2016-01 ~ 2024-12, 월별)"""
    headers = {
        "X-Naver-Client-Id":     CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type":          "application/json",
    }
    body = {
        "startDate":    "2016-01-01",   # 네이버 데이터랩 제공 시작일
        "endDate":      "2024-12-31",
        "timeUnit":     "month",
        "keywordGroups": [{"groupName": var_name, "keywords": keywords}],
    }
    resp = requests.post(API_URL, headers=headers, data=json.dumps(body), timeout=30)
    resp.raise_for_status()
    data = resp.json()

    rows = data["results"][0]["data"]
    df = pd.DataFrame(rows)          # period, ratio
    df.columns = ["period", var_name]
    df[var_name] = pd.to_numeric(df[var_name], errors="coerce")
    return df


def monthly_to_quarterly(df: pd.DataFrame, var_name: str) -> pd.DataFrame:
    """월별 → 분기 평균"""
    df["year"]    = df["period"].str[:4].astype(int)
    df["month"]   = df["period"].str[5:7].astype(int)
    df["quarter"] = df["month"].apply(lambda m: (m - 1) // 3 + 1)
    df["qkey"]    = df["year"].astype(str) + "Q" + df["quarter"].astype(str)
    result = df.groupby("qkey")[var_name].mean().reset_index()
    result.columns = ["quarter", var_name]
    return result.sort_values("quarter").reset_index(drop=True)


if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        raise EnvironmentError(".env 파일에 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET이 없습니다.")

    all_dfs = []
    for var_name, keywords in KEYWORDS.items():
        print(f"{var_name} 수집 중... ({keywords})")
        try:
            df_monthly = fetch_trend(var_name, keywords)
            # 월별 원본 저장
            df_monthly.to_csv(OUT_DIR / f"{var_name}_monthly.csv", index=False, encoding="utf-8-sig")
            # 분기 집계
            df_q = monthly_to_quarterly(df_monthly, var_name)
            df_q.to_csv(OUT_DIR / f"{var_name}_quarterly.csv", index=False, encoding="utf-8-sig")
            all_dfs.append(df_q.set_index("quarter"))
            print(f"  → {len(df_q)}분기 저장")
        except Exception as e:
            print(f"  [오류] {var_name}: {e}")

    # 전체 병합
    if all_dfs:
        merged = pd.concat(all_dfs, axis=1).reset_index()
        merged.to_csv(OUT_DIR / "naver_trends_quarterly.csv", index=False, encoding="utf-8-sig")
        print(f"\n통합 파일 저장: naver_trends_quarterly.csv")

    print("\n네이버 트렌드 수집 완료.")
    print("⚠️  2010~2015 구간은 API 미지원. 해당 기간은 결측치(NaN) 처리 후 보간 필요.")
