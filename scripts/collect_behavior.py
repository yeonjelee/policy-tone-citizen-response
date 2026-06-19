"""
실측 '행동' 데이터 수집 (검색=관심 프록시 검증용)  [v2 · 2026-06-16, ECOS 항목 확정]
목표: 검색↑ 이 실제 행동과 일치하는가? 특히 긴축기 대출·부동산.

수집(ECOS, 월별, 2016-01~2024-12):
  - household_loan : 예금은행 총대출금(104Y016 BDCA1) — 가계+기업 합산 proxy
                     (순수 가계대출은 분기 가계신용뿐 → 월별 일관성 위해 총대출금 사용. 한계 표기)
  - bank_deposit   : 예금은행 원화예금(104Y013 BCB1)
  - house_price    : 주택매매가격지수 총지수(901Y062 P63A)
  - invest_deposit : 투자자 예탁금(901Y056 S23A)
출력: raw/behavior/<name>_monthly.csv (period, value), _quarterly.csv

실행: python scripts/collect_behavior.py
의존성: collect_ecos 재사용
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from collect_ecos import fetch_ecos, find_item_code, API_KEY

ROOT = Path(__file__).parents[1]
OUT = ROOT / "raw" / "behavior"
OUT.mkdir(parents=True, exist_ok=True)
START, END = "201601", "202412"

TARGETS = {
    "household_loan": ("104Y016", ["총대출금"]),
    "bank_deposit":   ("104Y013", ["원화예금"]),
    "house_price":    ("901Y062", ["총지수"]),
    "invest_deposit": ("901Y056", ["투자자 예탁금", "예탁금"]),
}


def collect_one(name, stat, kws):
    df = fetch_ecos(stat, "M", START, END)
    code = find_item_code(df, *kws)
    if not code:
        print(f"  ✗ {name}: 항목 미발견"); return
    sub = df[df["ITEM_CODE1"] == code].copy()
    sub["value"] = pd.to_numeric(sub["DATA_VALUE"], errors="coerce")
    sub = sub.dropna(subset=["value"]).sort_values("TIME")
    out = sub[["TIME", "value"]].rename(columns={"TIME": "period"})
    (OUT / f"{name}_monthly.csv").unlink(missing_ok=True)
    out.to_csv(OUT / f"{name}_monthly.csv", index=False, encoding="utf-8-sig")
    sub["quarter"] = sub["TIME"].str[:4] + "Q" + ((sub["TIME"].str[4:6].astype(int)-1)//3 + 1).astype(str)
    q = sub.groupby("quarter")["value"].mean().reset_index()
    (OUT / f"{name}_quarterly.csv").unlink(missing_ok=True)
    q.to_csv(OUT / f"{name}_quarterly.csv", index=False, encoding="utf-8-sig")
    nm = sub["ITEM_NAME1"].iloc[0] if "ITEM_NAME1" in sub else ""
    print(f"  ✓ {name}: {stat} '{nm}' ({len(out)}건)")


if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit(".env 에 ECOS_API_KEY 필요")
    print("실측 행동 데이터 수집(ECOS)...")
    for name, (stat, kws) in TARGETS.items():
        try:
            collect_one(name, stat, kws)
        except Exception as e:
            print(f"  ✗ {name}: {e}")
    print(f"\n→ {OUT}/")
