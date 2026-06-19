"""
이상치/괴리 타임라인 — '이론이 언제 깨지나'  [2026-06-16]  (METHODOLOGY §5)

H1의 월별 분해: 각 월의 정책-검색 관계가 기대부호(이론)와 얼마나 일치/위반했나.

  z표준화 후, 셀(a,k)의 월별 기여  c_{m,a,k} = E[a][k] · z(Tone_{m,a}) · z(Search_{m,k})
    > 0 : 그 달 이 채널은 이론대로   |   < 0 : 이론 위반(괴리)
  월별 이론정합도   A_m = mean_cells c
  월별 괴리(위반)   D_m = mean_cells max(−c, 0)
  대출·부동산 역방향 집중 지표(핵심 발견)  REV_m

출력: processed/analysis/deviation_monthly.csv + 상위 이상치 월·주도 채널
의존성: pandas
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parents[1]
TONE = ROOT / "processed" / "tone" / "tone_monthly.csv"
NAVER = ROOT / "raw" / "naver_trends"
OUTD = ROOT / "processed" / "analysis"
SEARCHES = ["deposit", "loan", "realestate", "inflation", "currency", "invest"]
E = {
    "inflation": {"deposit": +1, "loan": -1, "realestate": -1, "inflation": +1, "currency": +1, "invest": -1},
    "growth":    {"deposit": +1, "loan": -1, "realestate": -1, "inflation": +1, "currency": +1, "invest": -1},
    "finstab":   {"deposit": +1, "loan": -1, "realestate": -1, "inflation":  0, "currency": +1, "invest": -1},
    "fiscal":    {"deposit": +1, "loan": -1, "realestate": -1, "inflation": -1, "currency":  0, "invest": -1},
}
REV_CELLS = [("inflation", "loan"), ("finstab", "loan"),
             ("inflation", "realestate"), ("finstab", "realestate"), ("fiscal", "realestate")]


def z(x):
    return (x - x.mean()) / x.std(ddof=0)


def run():
    OUTD.mkdir(parents=True, exist_ok=True)
    tone = pd.read_csv(TONE); tone["period"] = tone["period"].astype(str).str[:7]
    df = tone.copy()
    for k in SEARCHES:
        s = pd.read_csv(NAVER / f"search_{k}_monthly.csv")
        s["period"] = s["period"].astype(str).str[:7]
        df = df.merge(s.rename(columns={f"search_{k}": f"s_{k}"})[["period", f"s_{k}"]],
                      on="period", how="left")
    df = df.sort_values("period").reset_index(drop=True)

    zt = {a: z(df[f"tone_{a}"]) for a in E if f"tone_{a}" in df}
    zs = {k: z(df[f"s_{k}"]) for k in SEARCHES}
    contrib = {(a, k): E[a][k] * zt[a] * zs[k]
               for a in zt for k in SEARCHES if E[a][k] != 0}
    C = pd.DataFrame(contrib)

    out = pd.DataFrame({"period": df["period"]})
    out["A_align"] = C.mean(axis=1)
    out["D_deviation"] = (-C).clip(lower=0).mean(axis=1)          # 위반량(벡터화)
    rev = C[[c for c in REV_CELLS if c in C.columns]]
    out["REV_loan_re"] = (-rev).clip(lower=0).mean(axis=1)

    (OUTD / "deviation_monthly.csv").unlink(missing_ok=True)
    out.to_csv(OUTD / "deviation_monthly.csv", index=False, encoding="utf-8-sig")
    print(f"→ deviation_monthly.csv ({len(out)}개월)")

    print("\n[이론 위반(D) 상위 10개월 — 주도 채널]")
    for _, r in out.sort_values("D_deviation", ascending=False).head(10).iterrows():
        idx = out.index[out["period"] == r["period"]][0]
        worst = C.loc[idx].sort_values().head(2)
        drv = ", ".join(f"{a}×{k}({v:+.1f})" for (a, k), v in worst.items())
        print(f"  {r['period']}  D={r['D_deviation']:.2f}  REV={r['REV_loan_re']:.2f}  ← {drv}")

    print("\n[연도별 평균: 괴리 D / 대출·부동산 역방향 REV]")
    out["y"] = out["period"].str[:4]
    print(out.groupby("y")[["D_deviation", "REV_loan_re"]].mean().round(2).to_string())


if __name__ == "__main__":
    run()
