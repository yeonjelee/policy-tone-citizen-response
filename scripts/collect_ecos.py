"""
ECOS (한국은행 경제통계시스템) 거시변수 수집  [수정본 v7 · 2026-06-16]
수집 항목: 기준금리, CPI 전년동월비, 원/달러 환율
분석 구간: 2016Q1~2024Q4
API 키: .env 파일의 ECOS_API_KEY

[v7 수정 내역]
- (버그3) 환율 절단 수정: USD '항목코드'를 요청 URL 경로에 직접 지정해 USD만 수신.
- 수집 구간 2016-01 기준 (CPI는 YoY 계산 위해 2015-01부터).
- (신규) save_csv(): 기존 파일을 먼저 삭제 후 새로 기록 → 동기화 폴더에서
  '기존 파일 크기로 잘리는' truncation 방지. (환율이 2019Q1에서 잘린 원인 차단)
"""

import os
import sys
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[1] / ".env")

API_KEY  = os.getenv("ECOS_API_KEY")
BASE_URL = "https://ecos.bok.or.kr/api/StatisticSearch"
OUT_DIR  = Path(__file__).parents[1] / "raw" / "ecos"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DEBUG = "--debug" in sys.argv

START_YM = "201601"
END_YM   = "202412"
CPI_START_YM = "201501"


def save_csv(df: pd.DataFrame, name: str):
    """기존 파일 삭제 후 기록 (덮어쓰기 truncation 방지)."""
    out = OUT_DIR / name
    try:
        out.unlink(missing_ok=True)
    except Exception:
        pass
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"  → {out.name} ({len(df)}분기)")


def fetch_ecos(stat_code: str, freq: str, start: str, end: str,
               item1: str | None = None, rows: int = 100000) -> pd.DataFrame:
    url = f"{BASE_URL}/{API_KEY}/json/kr/1/{rows}/{stat_code}/{freq}/{start}/{end}"
    if item1:
        url += f"/{item1}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "StatisticSearch" not in data:
        raise ValueError(f"API 오류 [{stat_code}]: {data}")
    return pd.DataFrame(data["StatisticSearch"]["row"])


def find_item_code(df: pd.DataFrame, *keywords: str) -> str | None:
    name_col = next((c for c in df.columns if "NAME" in c and "ITEM" in c), None)
    code_col = next((c for c in df.columns if "CODE" in c and "ITEM" in c), None)
    if name_col is None or code_col is None:
        return None
    for kw in keywords:
        m = df[df[name_col].str.contains(kw, na=False)]
        if not m.empty:
            return m[code_col].iloc[0]
    return None


def to_quarterly_avg(df: pd.DataFrame, value_col: str, out_col: str) -> pd.DataFrame:
    df = df.copy()
    df["year"]    = df["TIME"].str[:4].astype(int)
    df["month"]   = df["TIME"].str[4:6].astype(int)
    df["quarter"] = df["month"].apply(lambda m: (m - 1) // 3 + 1)
    df["qkey"]    = df["year"].astype(str) + "Q" + df["quarter"].astype(str)
    result = df.groupby("qkey")[value_col].mean().reset_index()
    result.columns = ["quarter", out_col]
    return result.sort_values("quarter").reset_index(drop=True)


def trim_window(df: pd.DataFrame) -> pd.DataFrame:
    qs = [f"{y}Q{q}" for y in range(2016, 2025) for q in range(1, 5)]
    return df[df["quarter"].isin(qs)].reset_index(drop=True)


def collect_base_rate():
    print("기준금리 수집 중...")
    df = fetch_ecos("722Y001", "M", START_YM, END_YM)
    code = find_item_code(df, "기준금리", "한국은행 기준금리")
    if code:
        df = df[df["ITEM_CODE1"] == code]
    df = df.copy()
    df["value"] = pd.to_numeric(df["DATA_VALUE"], errors="coerce")
    df = df[df["TIME"].str[4:6].isin(["03", "06", "09", "12"])].copy()
    df["quarter"] = df["TIME"].apply(
        lambda x: f"{x[:4]}Q{['03','06','09','12'].index(x[4:6])+1}")
    result = trim_window(df[["quarter", "value"]].rename(columns={"value": "base_rate"}))
    result["base_rate"] = result["base_rate"].round(2)
    save_csv(result, "base_rate.csv")


def collect_cpi():
    print("CPI 전년동월비 수집 중...")
    df = fetch_ecos("901Y009", "M", CPI_START_YM, END_YM)
    if "ITEM_NAME1" in df.columns:
        total = df[df["ITEM_NAME1"].str.contains("총지수", na=False)]
        if total.empty:
            total = df[df["ITEM_NAME1"].str.fullmatch("0|전체|전국", na=False)]
        if not total.empty:
            df = total.copy()
        elif "ITEM_CODE1" in df.columns:
            shortest = df["ITEM_CODE1"].str.len().idxmin()
            df = df[df["ITEM_CODE1"] == df.loc[shortest, "ITEM_CODE1"]].copy()
    df = df.sort_values("TIME").reset_index(drop=True)
    df["value"] = pd.to_numeric(df["DATA_VALUE"], errors="coerce")
    df["cpi_yoy"] = (df["value"] / df["value"].shift(12) - 1) * 100
    df = df[df["TIME"] >= START_YM].dropna(subset=["cpi_yoy"])
    result = trim_window(to_quarterly_avg(df, "cpi_yoy", "cpi_yoy"))
    result["cpi_yoy"] = result["cpi_yoy"].round(3)
    save_csv(result, "cpi_yoy.csv")


def collect_exchange_rate():
    print("원/달러 환율 수집 중...")
    probe = fetch_ecos("731Y001", "D", "20240101", "20240131", rows=1000)
    usd_code = find_item_code(probe, "원/미국달러", "미국달러", "달러")
    if DEBUG and usd_code:
        nm = probe[probe["ITEM_CODE1"] == usd_code]["ITEM_NAME1"].iloc[0]
        print(f"  [디버그] USD 항목코드={usd_code} ({nm})")

    rate_df = None
    if usd_code:
        df = fetch_ecos("731Y001", "D", f"{START_YM}01", f"{END_YM}31", item1=usd_code)
        df = df.copy()
        df["value"] = pd.to_numeric(df["DATA_VALUE"], errors="coerce")
        df["TIME"]  = df["TIME"].str[:6]
        monthly = df.groupby("TIME")["value"].mean().reset_index()
        if monthly["value"].notna().sum() >= 90:
            rate_df = monthly
            print(f"  731Y001 USD 일별→월평균 성공 ({len(monthly)}개월)")

    if rate_df is None:
        df = fetch_ecos("036Y001", "M", START_YM, END_YM)
        code = find_item_code(df, "원/미국달러", "미국달러", "달러")
        if code:
            df = df[df["ITEM_CODE1"] == code].copy()
            df["value"] = pd.to_numeric(df["DATA_VALUE"], errors="coerce")
            rate_df = df[["TIME", "value"]]
            print("  036Y001 월별 폴백 성공")

    if rate_df is None:
        print("  ⚠️ 환율 수집 실패. --debug 로 항목코드 확인 필요.")
        return

    result = trim_window(to_quarterly_avg(rate_df, "value", "exchange_rate"))
    result["exchange_rate"] = result["exchange_rate"].round(2)
    save_csv(result, "exchange_rate.csv")
    print(f"     범위 {result['exchange_rate'].min()}~{result['exchange_rate'].max()}")
    if len(result) < 36:
        print(f"  ⚠️ 36분기 미만({len(result)}). 항목코드/구간 확인 필요.")


if __name__ == "__main__":
    if not API_KEY:
        raise EnvironmentError(".env 파일에 ECOS_API_KEY가 설정되지 않았습니다.")
    if DEBUG:
        print("[디버그 모드]")
    collect_base_rate()
    collect_cpi()
    collect_exchange_rate()
    print("\nECOS 수집 완료. (목표: 각 36분기, 2016Q1~2024Q4)")
