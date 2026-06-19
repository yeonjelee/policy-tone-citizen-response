"""
KOSPI 수익률 수집 (yfinance 사용 - API 키 불필요)
수집 항목: KOSPI 분기 수익률 (2010Q1 ~ 2024Q4)

설치: pip install yfinance

[수정 이력]
- pykrx → yfinance 교체 (pykrx가 로그인 필요 버전으로 변경되어 실패)
- ^KS11 티커로 KOSPI 월봉 다운로드 후 분기 수익률 계산
"""

import pandas as pd
import yfinance as yf
from pathlib import Path

OUT_DIR = Path(__file__).parents[1] / "raw" / "krx"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def collect_kospi_quarterly():
    print("KOSPI 분기 수익률 수집 중 (yfinance ^KS11)...")

    # 월봉 다운로드 (2009-12 포함해야 2010Q1 수익률 계산 가능)
    df = yf.download("^KS11", start="2009-12-01", end="2024-12-31",
                     interval="1mo", auto_adjust=True, progress=False)

    if df.empty:
        raise RuntimeError("yfinance에서 데이터를 가져오지 못했습니다. 네트워크 연결을 확인하세요.")

    # Close 컬럼 추출 (MultiIndex 대응)
    close = df["Close"] if "Close" in df.columns else df.iloc[:, 0]
    close = close.squeeze()

    # 날짜 인덱스 정리
    close.index = pd.to_datetime(close.index)
    close = close.sort_index()

    records = []
    for year in range(2010, 2025):
        for q, (m_start, m_end) in enumerate([(1,3),(4,6),(7,9),(10,12)], 1):
            qkey = f"{year}Q{q}"

            # 분기 첫 거래일 종가 (= 전 분기 마지막 월 종가)
            prev_month = pd.Timestamp(year, m_start, 1) - pd.DateOffset(months=1)
            quarter_months = close[
                (close.index.year == year) &
                (close.index.month >= m_start) &
                (close.index.month <= m_end)
            ]

            prev_data = close[
                (close.index.year == prev_month.year) &
                (close.index.month == prev_month.month)
            ]

            if quarter_months.empty or prev_data.empty:
                print(f"  {qkey}: 데이터 없음")
                continue

            start_price = prev_data.iloc[-1]   # 전 분기말 종가
            end_price   = quarter_months.iloc[-1]  # 분기말 종가
            ret = (end_price - start_price) / start_price * 100

            records.append({"quarter": qkey, "kospi_return": round(float(ret), 4)})
            print(f"  {qkey}: {ret:.2f}%")

    df_result = pd.DataFrame(records)
    out = OUT_DIR / "kospi_return.csv"
    df_result.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n→ {out} ({len(df_result)}분기)")


if __name__ == "__main__":
    collect_kospi_quarterly()
    print("\nKOSPI 수집 완료.")
