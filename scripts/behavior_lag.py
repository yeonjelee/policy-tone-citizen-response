"""
행동 lag 검증 — 긴축이 실제 행동에 '시차'를 두고 미치는 효과  [2026-06-16]
동시점에선 안 보이던 '긴축→집값/대출 둔화'가 시차(ℓ개월 후)에 나타나는지.

  ρ(ℓ) = Spearman( 긴축톤_t ,  행동증가율_{t+ℓ} ),  ℓ = 0,3,6,9,12 (월)
  이론: 긴축 → 일정 시차 후 집값상승률·대출증가율 ↓ (음으로 전환 기대)

입력: tone_monthly, raw/behavior/*_monthly
출력: processed/analysis/behavior_lag.csv + 콘솔
"""
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).parents[1]
TONE = ROOT / "processed/tone/tone_monthly.csv"
BEH = ROOT / "raw/behavior"
OUTD = ROOT / "processed/analysis"
BEHS = ["house_price", "household_loan", "bank_deposit", "invest_deposit"]
LAGS = [0, 3, 6, 9, 12]


def run():
    OUTD.mkdir(parents=True, exist_ok=True)
    t = pd.read_csv(TONE); t["period"] = t["period"].astype(str).str[:7]
    t["tight"] = t[["tone_inflation", "tone_growth", "tone_finstab"]].mean(axis=1)
    df = t[["period", "tight"]].copy()
    for b in BEHS:
        p = BEH / f"{b}_monthly.csv"
        if not p.exists():
            continue
        d = pd.read_csv(p); d["period"] = d["period"].astype(str).str[:4] + "-" + d["period"].astype(str).str[4:6]
        d = d.sort_values("period")
        d[b] = pd.to_numeric(d[d.columns[1]], errors="coerce").pct_change(12) * 100
        df = df.merge(d[["period", b]], on="period", how="left")
    df = df.sort_values("period").reset_index(drop=True)

    rows = []
    for b in BEHS:
        if b not in df:
            continue
        rec = {"behavior(YoY%)": b}
        for L in LAGS:
            pair = pd.concat([df["tight"], df[b].shift(-L)], axis=1).dropna()
            rec[f"lag{L}"] = round(spearmanr(pair.iloc[:, 0], pair.iloc[:, 1])[0], 2) if len(pair) >= 12 else None
        rows.append(rec)
    res = pd.DataFrame(rows)
    (OUTD / "behavior_lag.csv").unlink(missing_ok=True)
    res.to_csv(OUTD / "behavior_lag.csv", index=False, encoding="utf-8-sig")
    print("긴축톤 → 행동증가율, 시차별 상관 (음수 = 긴축 후 둔화/하락 = 이론대로):")
    print(res.to_string(index=False))
    print("\n해석: house_price·household_loan 이 lag6~12에서 음(−)으로 가면")
    print("  → 긴축이 시차를 두고 실제 집값·대출을 눌렀다 = 검색(즉각 관심)과 분리됨.")
    print(f"→ {OUTD/'behavior_lag.csv'}")


if __name__ == "__main__":
    run()
