"""
H1 — 정책 톤 → 시민 검색 반응의 '이론 일치' 분석 (시차 순위상관)  [2026-06-16]

METHODOLOGY §3·§4. 기대부호 매트릭스(긴축=+1) 대비 실제 시차상관의 부호 일치 검증.
  - 톤·검색 z-표준화
  - 시차 ℓ=0..3 (정책 선행) Spearman: ρ(ℓ)=corr(Tone_t, Search_{t+ℓ})
  - align = E · ρ(ℓ*),  ℓ* = E·ρ 최대인 시차
  - 종합: 부호 일치율(align>0 비율), 평균 align

입력: processed/tone/tone_monthly.csv,  raw/naver_trends/search_*_monthly.csv
출력: processed/analysis/h1_concordance.csv  + 콘솔 요약
의존성: pandas, scipy
"""

from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).parents[1]
TONE = ROOT / "processed" / "tone" / "tone_monthly.csv"
NAVER = ROOT / "raw" / "naver_trends"
OUTD = ROOT / "processed" / "analysis"
SEARCHES = ["deposit", "loan", "realestate", "inflation", "currency", "invest"]
MAXLAG = 3

# 기대부호 E[tone][search]  (긴축=+1; 0=이론 모호→제외)
E = {
    "inflation": {"deposit": +1, "loan": -1, "realestate": -1, "inflation": +1, "currency": +1, "invest": -1},
    "growth":    {"deposit": +1, "loan": -1, "realestate": -1, "inflation": +1, "currency": +1, "invest": -1},
    "finstab":   {"deposit": +1, "loan": -1, "realestate": -1, "inflation":  0, "currency": +1, "invest": -1},
    "fiscal":    {"deposit": +1, "loan": -1, "realestate": -1, "inflation": -1, "currency":  0, "invest": -1},
}


def load_panel() -> pd.DataFrame:
    tone = pd.read_csv(TONE)
    tone["period"] = tone["period"].astype(str).str[:7]
    df = tone.copy()
    for k in SEARCHES:
        s = pd.read_csv(NAVER / f"search_{k}_monthly.csv")
        s["period"] = s["period"].astype(str).str[:7]
        s = s.rename(columns={f"search_{k}": f"s_{k}"})[["period", f"s_{k}"]]
        df = df.merge(s, on="period", how="left")
    return df.sort_values("period").reset_index(drop=True)


def z(x):
    return (x - x.mean()) / x.std(ddof=0)


def run():
    OUTD.mkdir(parents=True, exist_ok=True)
    df = load_panel()
    rows = []
    for a in E:
        tcol = f"tone_{a}"
        if tcol not in df:
            continue
        for k in SEARCHES:
            e = E[a][k]
            if e == 0:
                continue
            t = z(df[tcol])
            best = None
            for lag in range(0, MAXLAG + 1):
                s = z(df[f"s_{k}"]).shift(-lag)      # 정책이 lag만큼 선행
                pair = pd.concat([t, s], axis=1).dropna()
                if len(pair) < 12:
                    continue
                rho, p = spearmanr(pair.iloc[:, 0], pair.iloc[:, 1])
                align = e * rho
                if best is None or align > best["align"]:
                    best = {"tone": a, "search": k, "E": e, "lag": lag,
                            "rho": round(rho, 3), "p": round(p, 3),
                            "align": round(align, 3), "n": len(pair)}
            if best:
                rows.append(best)

    res = pd.DataFrame(rows)
    (OUTD / "h1_concordance.csv").unlink(missing_ok=True)
    res.to_csv(OUTD / "h1_concordance.csv", index=False, encoding="utf-8-sig")

    agree = (res["align"] > 0).mean()
    print(f"검증 셀 {len(res)}개 | 이론 부호 일치율 = {agree:.0%} | 평균 align = {res['align'].mean():+.3f}")
    print("\n[톤별 일치율]")
    for a, g in res.groupby("tone"):
        print(f"  {a:10}: 일치 {int((g['align']>0).sum())}/{len(g)}  평균 align {g['align'].mean():+.2f}")
    print("\n[셀별 (정책 선행 시차 lag, ρ, 일치 align)] — align<0 = 이론과 반대(괴리 후보)")
    for _, r in res.sort_values("align").iterrows():
        flag = "  ← 이론반대" if r["align"] < 0 else ""
        print(f"  {r['tone']:10}×{r['search']:11} E={r['E']:+d} lag{int(r['lag'])} ρ={r['rho']:+.2f} align={r['align']:+.2f}{flag}")
    print(f"\n→ {OUTD/'h1_concordance.csv'}")


if __name__ == "__main__":
    run()
