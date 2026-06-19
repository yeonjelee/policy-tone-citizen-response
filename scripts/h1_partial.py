"""
H1 거시통제 — 편상관(partial Spearman)  [2026-06-16]  (METHODOLOGY §4-3)
단순상관은 '한은도 시민도 같은 경기에 반응'하는 공통추세로 부풀려짐.
거시(금리·CPI·환율·KOSPI·실업률)를 통제한 뒤에도 톤↔검색 관계가 남는지.

  partial ρ = corr( resid(톤|거시), resid(검색|거시) )  [순위 기반]
  거시는 분기값 → 월로 forward-fill(통제변수라 근사 허용).
  시차는 h1_concordance.csv 의 cell별 lag 사용(일관성).

입력: tone_monthly, naver search_*_monthly, h1_concordance.csv,
      raw/ecos·krx·kosis (분기 거시)
출력: processed/analysis/h1_partial.csv + 콘솔(통제 전/후 비교)
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata, pearsonr

ROOT = Path(__file__).parents[1]
TONE = ROOT / "processed/tone/tone_monthly.csv"
NAVER = ROOT / "raw/naver_trends"
H1 = ROOT / "processed/analysis/h1_concordance.csv"
OUTD = ROOT / "processed/analysis"
MACRO = {"base_rate": ROOT/"raw/ecos/base_rate.csv", "cpi_yoy": ROOT/"raw/ecos/cpi_yoy.csv",
         "exchange_rate": ROOT/"raw/ecos/exchange_rate.csv", "kospi_return": ROOT/"raw/krx/kospi_return.csv",
         "unemployment": ROOT/"raw/kosis/unemployment_quarterly.csv"}


def q_of(p):
    y, m = p.split("-"); return f"{y}Q{(int(m)-1)//3 + 1}"


def partial_spearman(x, y, Z):
    m = ~(np.isnan(x) | np.isnan(y) | np.isnan(Z).any(axis=1))
    x, y, Z = x[m], y[m], Z[m]
    if len(x) < 15:
        return None
    rx, ry = rankdata(x), rankdata(y)
    rZ = np.column_stack([np.ones(len(x))] + [rankdata(Z[:, j]) for j in range(Z.shape[1])])
    ex = rx - rZ @ np.linalg.lstsq(rZ, rx, rcond=None)[0]
    ey = ry - rZ @ np.linalg.lstsq(rZ, ry, rcond=None)[0]
    return pearsonr(ex, ey)[0]


def run():
    OUTD.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TONE); df["period"] = df["period"].astype(str).str[:7]
    for k in ["deposit", "loan", "realestate", "inflation", "currency", "invest"]:
        d = pd.read_csv(NAVER/f"search_{k}_monthly.csv"); d["period"] = d["period"].astype(str).str[:7]
        df = df.merge(d.rename(columns={f"search_{k}": f"s_{k}"})[["period", f"s_{k}"]], on="period", how="left")
    for name, fp in MACRO.items():
        m = pd.read_csv(fp); col = [c for c in m.columns if c != "quarter"][0]
        mp = dict(zip(m["quarter"], m[col]))
        df[name] = [mp.get(q_of(p), np.nan) for p in df["period"]]
    df = df.sort_values("period").reset_index(drop=True)
    Z = df[list(MACRO)].to_numpy(float)

    h1 = pd.read_csv(H1)
    rows = []
    for _, r in h1.iterrows():
        a, k, E, lag = r["tone"], r["search"], int(r["E"]), int(r["lag"])
        tcol, scol = f"tone_{a}", f"s_{k}"
        if tcol not in df or scol not in df:
            continue
        x = df[tcol].to_numpy(float)
        y = df[scol].shift(-lag).to_numpy(float)
        pr = partial_spearman(x, y, Z)
        if pr is None:
            continue
        rows.append({"tone": a, "search": k, "E": E, "lag": lag,
                     "raw_align": r["align"], "ctrl_align": round(E*pr, 3)})
    res = pd.DataFrame(rows)
    (OUTD/"h1_partial.csv").unlink(missing_ok=True)
    res.to_csv(OUTD/"h1_partial.csv", index=False, encoding="utf-8-sig")

    raw_rate = (res["raw_align"] > 0).mean()
    ctrl_rate = (res["ctrl_align"] > 0).mean()
    print(f"이론 일치율  통제전 {raw_rate:.0%}  →  거시통제후 {ctrl_rate:.0%}")
    print(f"평균 align  통제전 {res['raw_align'].mean():+.3f}  →  통제후 {res['ctrl_align'].mean():+.3f}")
    print("\n[통제 후에도 남는 괴리(ctrl_align<0)] = 거시로 설명 안 되는 진짜 역설")
    for _, r in res[res["ctrl_align"] < 0].sort_values("ctrl_align").iterrows():
        print(f"  {r['tone']:10}×{r['search']:11} raw={r['raw_align']:+.2f} → ctrl={r['ctrl_align']:+.2f}")
    print(f"\n→ {OUTD/'h1_partial.csv'}")


if __name__ == "__main__":
    run()
