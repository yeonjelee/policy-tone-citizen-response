"""
일별 금융시장 데이터 — 환율·KOSPI (정책 전달의 '즉시' 계층)  [2026-06-16]
정책 충격에 시장은 당일 즉각 반응 → 이벤트 스터디의 첫 계층.
- 환율(원/달러): ECOS 731Y001 일별 (USD 항목)
- KOSPI: yfinance ^KS11 일별 종가 → 일간수익률(%)
출력: raw/market/fx_daily.csv, kospi_daily.csv  (date, value/return)
의존성: requests, pandas, yfinance, python-dotenv (collect_ecos 재사용)
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
ROOT = Path(__file__).parents[1]
OUT = ROOT / "raw" / "market"
OUT.mkdir(parents=True, exist_ok=True)


def fx_daily():
    from collect_ecos import fetch_ecos, find_item_code, API_KEY
    if not API_KEY:
        print("  ✗ 환율: ECOS 키 없음"); return
    probe = fetch_ecos("731Y001", "D", "20240101", "20240131", rows=1000)
    code = find_item_code(probe, "원/미국달러", "미국달러", "달러")
    df = fetch_ecos("731Y001", "D", "20160101", "20241231", item1=code)
    df = df.copy()
    df["date"] = pd.to_datetime(df["TIME"], format="%Y%m%d", errors="coerce")
    df["value"] = pd.to_numeric(df["DATA_VALUE"], errors="coerce")
    out = df.dropna(subset=["date", "value"]).sort_values("date")[["date", "value"]]
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    (OUT / "fx_daily.csv").unlink(missing_ok=True)
    out.to_csv(OUT / "fx_daily.csv", index=False, encoding="utf-8-sig")
    print(f"  ✓ 환율 {len(out)}일")


def kospi_daily():
    try:
        import yfinance as yf
    except ImportError:
        print("  ✗ KOSPI: pip install yfinance"); return
    k = yf.download("^KS11", start="2016-01-01", end="2024-12-31", progress=False)
    if k is None or len(k) == 0:
        print("  ✗ KOSPI 수신 실패"); return
    close = k["Close"].squeeze()
    ret = close.pct_change() * 100
    out = pd.DataFrame({"date": ret.index.strftime("%Y-%m-%d"), "return": ret.values}).dropna()
    (OUT / "kospi_daily.csv").unlink(missing_ok=True)
    out.to_csv(OUT / "kospi_daily.csv", index=False, encoding="utf-8-sig")
    print(f"  ✓ KOSPI {len(out)}일")


if __name__ == "__main__":
    print("일별 시장 데이터 수집...")
    fx_daily()
    kospi_daily()
    print(f"\n→ {OUT}/")
