"""
검색(관심) vs 실측 행동 — 대출·부동산 역설 규명  [v2 · 2026-06-16]
[v2 수정] 행동을 '레벨'이 아니라 '증가율(YoY %)'로 — 잔액·가격지수는 추세로 우상향하므로
          레벨 상관은 허위(추세 교란). 흐름(증가율)으로 봐야 긴축 효과가 드러난다.

질문: 긴축기 대출·부동산 '검색'↑ 이 실제 '행동 흐름'으로 이어지나?
  비교: 톤(긴축, level) → 검색(level)   vs   톤(긴축) → 행동 증가율(YoY)
  → 행동 증가율은 이론대로(긴축→대출증가 둔화/집값 하락, 음) 인데 검색만 양이면
    = "관심·불안 ≠ 실제 수요" 입증. 역설 해소.

입력: tone_monthly, naver search_*_monthly, raw/behavior/*_monthly
출력: processed/analysis/behavior_validation.csv
"""
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).parents[1]
TONE = ROOT / "processed/tone/tone_monthly.csv"
NAVER = ROOT / "raw/naver_trends"
BEH = ROOT / "raw/behavior"
OUTD = ROOT / "processed/analysis"
PAIRS = [  # 검색, 행동, 긴축시 이론 기대부호(행동 증가율)
    ("deposit",    "bank_deposit",   +1),
    ("loan",       "household_loan",  -1),
    ("realestate", "house_price",     -1),
    ("invest",     "invest_deposit",  -1),
]


def to_period(d):
    p = d["period"].astype(str)
    return (p.str[:7] if "-" in p.iloc[0] else p.str[:4] + "-" + p.str[4:6])


def run():
    OUTD.mkdir(parents=True, exist_ok=True)
    tone = pd.read_csv(TONE); tone["period"] = tone["period"].astype(str).str[:7]
    df = tone.copy()
    df["tight"] = df[["tone_inflation", "tone_growth", "tone_finstab"]].mean(axis=1)

    for s, b, _ in PAIRS:
        sp, bp = NAVER / f"search_{s}_monthly.csv", BEH / f"{b}_monthly.csv"
        if sp.exists():
            d = pd.read_csv(sp); d["period"] = to_period(d)
            df = df.merge(d.rename(columns={d.columns[1]: f"se_{s}"})[["period", f"se_{s}"]], on="period", how="left")
        if bp.exists():
            d = pd.read_csv(bp); d["period"] = to_period(d)
            d = d.sort_values("period")
            d[f"bh_{b}"] = pd.to_numeric(d[d.columns[1]], errors="coerce").pct_change(12) * 100  # YoY %
            df = df.merge(d[["period", f"bh_{b}"]], on="period", how="left")
    df = df.sort_values("period").reset_index(drop=True)

    def sr(x, a, c):
        p = x[[a, c]].dropna()
        return round(spearmanr(p[a], p[c])[0], 2) if len(p) >= 10 else None

    tight = df[df["tight"] > 0]
    rows = []
    for s, b, E in PAIRS:
        se, bh = f"se_{s}", f"bh_{b}"
        if se not in df or bh not in df:
            continue
        rows.append({
            "search": s, "behavior(YoY%)": b, "기대부호(긴축시행동)": E,
            "톤→검색": sr(df, "tight", se),
            "톤→행동": sr(df, "tight", bh),
            "검색↔행동_전체": sr(df, se, bh),
            "검색↔행동_긴축기": sr(tight, se, bh),
            "n": df[[se, bh]].dropna().shape[0],
        })
    res = pd.DataFrame(rows)
    (OUTD / "behavior_validation.csv").unlink(missing_ok=True)
    res.to_csv(OUTD / "behavior_validation.csv", index=False, encoding="utf-8-sig")
    print(res.to_string(index=False))
    print("\n결정적 해석:")
    print(" loan·realestate 에서 '톤→행동'(증가율)이 음(−) 인데 '톤→검색'이 양(+) 이면")
    print("  → 긴축기 실제 대출증가·집값은 둔화/하락하는데 검색(관심)만 ↑ = '불안 관심 ≠ 수요' 입증.")
    print(f"→ {OUTD/'behavior_validation.csv'}")


if __name__ == "__main__":
    run()
