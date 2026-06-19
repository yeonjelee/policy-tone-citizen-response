"""
국면 군집 — 중첩 2단계 (정책 기조 → 시민 반응) + 이상치  [2026-06-16]  (METHODOLOGY §7·§5)

1단계: z(톤 4축)에 계층군집(Ward) → 정책 기조 regime (K1, 실루엣 선택)
2단계: 각 regime 안에서 z(검색 6축)에 K-means → 시민 반응 하위유형 (K2)
프로파일: 거시·괴리(D/REV)는 '군집 피처가 아니라' 사후 프로파일링에만 사용(순환논리 방지)
이상치: z(D_deviation)>2 (이론 위반) & LOF (밀도 기반 이례) — 상보적 플래그
시각화: t-SNE 2D 좌표 저장

입력: processed/tone/tone_monthly.csv, raw/naver_trends/search_*_monthly.csv,
      processed/analysis/deviation_monthly.csv, raw/ecos·kosis·krx (분기→월 ffill, 프로파일용)
출력: processed/analysis/phase_assignments.csv, phase_profile.csv
의존성: pandas, scikit-learn, scipy
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE

ROOT = Path(__file__).parents[1]
TONE = ROOT / "processed" / "tone" / "tone_monthly.csv"
NAVER = ROOT / "raw" / "naver_trends"
DEV = ROOT / "processed" / "analysis" / "deviation_monthly.csv"
OUTD = ROOT / "processed" / "analysis"
TONES = ["tone_inflation", "tone_growth", "tone_finstab", "tone_fiscal"]
SEARCHES = ["deposit", "loan", "realestate", "inflation", "currency", "invest"]


def q_of(period):  # "2016-03" -> "2016Q1"
    y, m = period.split("-")
    return f"{y}Q{(int(m)-1)//3 + 1}"


def load_macro_monthly(periods):
    macro = {}
    files = {"base_rate": ROOT/"raw/ecos/base_rate.csv", "cpi_yoy": ROOT/"raw/ecos/cpi_yoy.csv",
             "exchange_rate": ROOT/"raw/ecos/exchange_rate.csv", "kospi_return": ROOT/"raw/krx/kospi_return.csv",
             "unemployment": ROOT/"raw/kosis/unemployment_quarterly.csv"}
    for name, fp in files.items():
        if not fp.exists():
            continue
        d = pd.read_csv(fp)
        col = [c for c in d.columns if c != "quarter"][0]
        m = dict(zip(d["quarter"], d[col]))
        macro[name] = [m.get(q_of(p), np.nan) for p in periods]
    return pd.DataFrame(macro)


def best_k(X, kmax, kind):
    best = (2, -1)
    for k in range(2, min(kmax, len(X)-1) + 1):
        if kind == "ward":
            lab = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(X)
        else:
            lab = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X)
        if len(set(lab)) < 2:
            continue
        s = silhouette_score(X, lab)
        if s > best[1]:
            best = (k, s)
    return best


def run():
    OUTD.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TONE); df["period"] = df["period"].astype(str).str[:7]
    for k in SEARCHES:
        s = pd.read_csv(NAVER/f"search_{k}_monthly.csv"); s["period"] = s["period"].astype(str).str[:7]
        df = df.merge(s.rename(columns={f"search_{k}": f"s_{k}"})[["period", f"s_{k}"]], on="period", how="left")
    dev = pd.read_csv(DEV); dev["period"] = dev["period"].astype(str).str[:7]
    df = df.merge(dev[["period", "D_deviation", "REV_loan_re"]], on="period", how="left")
    df = df.dropna(subset=TONES + [f"s_{k}" for k in SEARCHES]).sort_values("period").reset_index(drop=True)
    periods = df["period"].tolist()

    Zt = StandardScaler().fit_transform(df[TONES])
    Zs = StandardScaler().fit_transform(df[[f"s_{k}" for k in SEARCHES]])

    # 1단계: 정책 기조 regime
    K1, s1 = best_k(Zt, 5, "ward")
    df["regime"] = AgglomerativeClustering(n_clusters=K1, linkage="ward").fit_predict(Zt)
    print(f"[1단계] 정책기조 regime K1={K1} (실루엣 {s1:.2f})")

    # 2단계: regime 내 시민 반응 하위유형
    df["sub"] = 0
    for r in sorted(df["regime"].unique()):
        idx = df.index[df["regime"] == r]
        if len(idx) >= 8:
            K2, s2 = best_k(Zs[idx], 3, "kmeans")
            df.loc[idx, "sub"] = KMeans(n_clusters=K2, n_init=10, random_state=0).fit_predict(Zs[idx])
            print(f"  regime {r} (n={len(idx)}) → 반응 하위 K2={K2} (실루엣 {s2:.2f})")
        else:
            print(f"  regime {r} (n={len(idx)}) → 너무 작아 하위군집 생략")
    df["phase"] = df["regime"].astype(str) + "-" + df["sub"].astype(str)

    # 이상치: z(D) & LOF
    d = df["D_deviation"].fillna(0)
    df["zD"] = (d - d.mean()) / d.std(ddof=0)
    df["anom_theory"] = (df["zD"] > 2).astype(int)
    nn = min(20, max(5, len(df)//6))
    df["lof"] = LocalOutlierFactor(n_neighbors=nn).fit_predict(np.hstack([Zt, Zs]))  # -1=이상
    df["anom_lof"] = (df["lof"] == -1).astype(int)

    # t-SNE
    perp = max(5, min(30, len(df)//4))
    xy = TSNE(n_components=2, perplexity=perp, random_state=0, init="pca").fit_transform(np.hstack([Zt, Zs]))
    df["tsne_x"], df["tsne_y"] = xy[:, 0], xy[:, 1]

    macro = load_macro_monthly(periods)
    out = pd.concat([df[["period", "regime", "sub", "phase", "zD", "anom_theory", "anom_lof",
                         "tsne_x", "tsne_y", "D_deviation", "REV_loan_re"] + TONES +
                        [f"s_{k}" for k in SEARCHES]].reset_index(drop=True), macro], axis=1)
    (OUTD/"phase_assignments.csv").unlink(missing_ok=True)
    out.to_csv(OUTD/"phase_assignments.csv", index=False, encoding="utf-8-sig")

    # 프로파일
    prof = out.groupby("phase").agg(
        n=("period", "size"), 기간=("period", lambda x: f"{x.min()}~{x.max()}"),
        **{t: (t, "mean") for t in TONES},
        **{f"s_{k}": (f"s_{k}", "mean") for k in SEARCHES},
        D=("D_deviation", "mean"), REV=("REV_loan_re", "mean"),
        base_rate=("base_rate", "mean")).round(2)
    (OUTD/"phase_profile.csv").unlink(missing_ok=True)
    prof.to_csv(OUTD/"phase_profile.csv", encoding="utf-8-sig")

    print(f"\n총 {len(out)}개월 → 국면 {out['phase'].nunique()}개. 이상치: 이론 {out['anom_theory'].sum()} / LOF {out['anom_lof'].sum()}")
    print("\n[국면 프로파일] (긴축=+1, 검색 z아님 원지수)")
    show = ["n", "기간"] + TONES + ["D", "REV", "base_rate"]
    print(prof[show].to_string())
    print("\n[이상치 월]")
    for _, r in out[(out.anom_theory == 1) | (out.anom_lof == 1)].iterrows():
        tag = ("이론" if r.anom_theory else "") + ("·LOF" if r.anom_lof else "")
        print(f"  {r['period']} [{r['phase']}] zD={r['zD']:+.1f} {tag}")
    print(f"\n→ {OUTD}/phase_assignments.csv, phase_profile.csv")


if __name__ == "__main__":
    run()
