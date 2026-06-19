"""
실업률(%) 수집  [수정본 2026-06-16]
출력: raw/kosis/unemployment_monthly.csv, unemployment_quarterly.csv
분석 구간: 2016Q1~2024Q4
API 키: .env 의 ECOS_API_KEY (1순위), KOSIS_API_KEY (폴백)

[v3 수정 내역 — 버그2]
이전 데이터는 값이 8,243~9,060 으로 '실업률(%)'이 아니라 '취업자 수(천명)'였고,
2017Q4→2018Q1, 2022Q4→2023Q1 에서 시계열이 인공적으로 단절됐다.
원인: KOSIS objL1="ALL" 로 모든 분류값(연령·성별 등)을 받아 단순 평균 → 표 구성이
바뀌는 시점마다 평균 대상 집합이 달라져 값이 튐. 또 실업률이 아닌 항목(itmId)이 선택됨.

수정:
- 1순위를 ECOS 실업률(%) 단일 항목으로 변경 (가장 안정적).
- '실업률' 항목 1개만 선택(다중 분류 평균 금지).
- 0~30% 범위 검증 후에만 저장. 실패 시 KOSIS 폴백.
"""

import os
import sys
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[1] / ".env")

ECOS_KEY  = os.getenv("ECOS_API_KEY")
KOSIS_KEY = os.getenv("KOSIS_API_KEY")
OUT_DIR   = Path(__file__).parents[1] / "raw" / "kosis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DEBUG    = "--debug" in sys.argv
START_YM = "201601"
END_YM   = "202412"


def is_valid_rate(series: pd.Series) -> bool:
    """실업률(%)이면 0~30 범위. 취업자수(수천)면 탈락."""
    v = pd.to_numeric(series, errors="coerce").dropna()
    return len(v) > 0 and v.max() < 30 and v.min() >= 0


# ── 1순위: ECOS 실업률(%) ─────────────────
def try_ecos() -> pd.DataFrame:
    if not ECOS_KEY:
        return pd.DataFrame()
    base = "https://ecos.bok.or.kr/api/StatisticSearch"
    # 901Y027: 고용/실업 관련 통계표 (실업률 항목 포함)
    for stat in ["901Y027", "901Y003", "901Y034"]:
        try:
            url = f"{base}/{ECOS_KEY}/json/kr/1/100000/{stat}/M/{START_YM}/{END_YM}"
            data = requests.get(url, timeout=30).json()
            if "StatisticSearch" not in data:
                continue
            df = pd.DataFrame(data["StatisticSearch"]["row"])
            if df.empty or "ITEM_NAME1" not in df.columns:
                continue

            # '실업률' 정확히 포함하는 항목만 (고용률/참가율 제외)
            unemp = df[df["ITEM_NAME1"].str.contains("실업률", na=False)]
            unemp = unemp[~unemp["ITEM_NAME1"].str.contains("청년|연령|장기", na=False)]
            if unemp.empty:
                if DEBUG:
                    print(f"  [디버그] {stat} 항목명: {df['ITEM_NAME1'].unique()[:8]}")
                continue

            # 단일 계열만 선택 (계절조정 우선, 없으면 첫 코드)
            seas = unemp[unemp["ITEM_NAME1"].str.contains("계절조정", na=False)]
            pick = seas if not seas.empty else unemp
            pick = pick[pick["ITEM_CODE1"] == pick["ITEM_CODE1"].iloc[0]]

            out = pick[["TIME", "DATA_VALUE"]].copy()
            out.columns = ["period", "unemployment"]
            out["unemployment"] = pd.to_numeric(out["unemployment"], errors="coerce")
            out = out.dropna()
            if is_valid_rate(out["unemployment"]):
                nm = pick["ITEM_NAME1"].iloc[0]
                print(f"  ✅ ECOS {stat} '{nm}' "
                      f"({out['unemployment'].min():.1f}~{out['unemployment'].max():.1f}%)")
                return out
        except Exception as e:
            if DEBUG:
                print(f"  ECOS {stat} 오류: {e}")
    return pd.DataFrame()


# ── 폴백: KOSIS 실업률 ─────────────────────
def try_kosis() -> pd.DataFrame:
    if not KOSIS_KEY:
        return pd.DataFrame()
    url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    # DT_1DA7004S: 성별 실업률 (단일 itmId, 전체 분류만 사용)
    candidates = [
        ("101", "DT_1DA7004S", "13103792999"),   # 실업률
        ("101", "DT_1DA7002S", "T70"),
    ]
    for org, tbl, itm in candidates:
        try:
            params = {
                "method": "getList", "apiKey": KOSIS_KEY,
                "itmId": itm, "objL1": "00",  # 00=전체 (ALL 평균 금지)
                "objL2": "", "objL3": "", "objL4": "",
                "objL5": "", "objL6": "", "objL7": "", "objL8": "",
                "format": "json", "jsonVD": "Y", "prdSe": "M",
                "startPrdDe": START_YM, "endPrdDe": END_YM,
                "orgId": org, "tblId": tbl,
            }
            data = requests.get(url, params=params, timeout=30).json()
            if not isinstance(data, list):
                if DEBUG:
                    print(f"  [디버그] KOSIS {tbl}/{itm} 응답: {str(data)[:120]}")
                continue
            recs = [{"period": d.get("PRD_DE"), "unemployment": d.get("DT")}
                    for d in data if isinstance(d, dict)]
            out = pd.DataFrame(recs).dropna()
            out["unemployment"] = pd.to_numeric(out["unemployment"], errors="coerce")
            out = out.dropna()
            if is_valid_rate(out["unemployment"]):
                print(f"  ✅ KOSIS {tbl}/{itm} 실업률 확인")
                return out
            elif DEBUG:
                print(f"  [디버그] KOSIS {tbl}/{itm} 범위이상 "
                      f"max={out['unemployment'].max():.1f} → 실업률 아님")
        except Exception as e:
            if DEBUG:
                print(f"  KOSIS {tbl}/{itm} 오류: {e}")
    return pd.DataFrame()


def monthly_to_quarterly(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["year"]    = df["period"].str[:4].astype(int)
    df["month"]   = df["period"].str[4:6].astype(int)
    df["quarter"] = df["month"].apply(lambda m: (m - 1) // 3 + 1)
    df["qkey"]    = df["year"].astype(str) + "Q" + df["quarter"].astype(str)
    qs = [f"{y}Q{q}" for y in range(2016, 2025) for q in range(1, 5)]
    res = df.groupby("qkey")["unemployment"].mean().reset_index()
    res.columns = ["quarter", "unemployment"]
    res = res[res["quarter"].isin(qs)]
    res["unemployment"] = res["unemployment"].round(2)
    return res.sort_values("quarter").reset_index(drop=True)


if __name__ == "__main__":
    print("실업률(%) 수집 중...\n[1단계] ECOS")
    df = try_ecos()
    if df.empty:
        print("\n[2단계] KOSIS 폴백")
        df = try_kosis()

    if df.empty:
        print("\n⚠️  실업률 수집 실패. --debug 로 항목명/응답 확인하세요.")
        print("    참고: ECOS 실업률은 보통 901Y027 통계표에 '실업률' 항목으로 존재.")
        raise SystemExit(1)

    df.to_csv(OUT_DIR / "unemployment_monthly.csv", index=False, encoding="utf-8-sig")
    q = monthly_to_quarterly(df)
    q.to_csv(OUT_DIR / "unemployment_quarterly.csv", index=False, encoding="utf-8-sig")
    print(f"\n→ unemployment_quarterly.csv ({len(q)}분기) "
          f"범위 {q['unemployment'].min()}~{q['unemployment'].max()}%")
    print(q.head(4).to_string(index=False))
