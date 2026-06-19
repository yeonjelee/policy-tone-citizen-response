"""
시각화 — PPT용 핵심 그림 4종  [2026-06-16]
출력: processed/figures/*.png
  1) tone_timeline   : 정책 톤 4축 월별 추이(긴축=+1)
  2) h1_heatmap      : 정책긴축→검색 이론 일치 히트맵(초록=이론대로, 빨강=괴리)
  3) deviation_timeline : 월별 괴리 D + 이상치 표시
  4) phase_tsne      : 국면 t-SNE 산점도(색=국면)
의존성: pandas, matplotlib
한글폰트: 맑은고딕/애플고딕/나눔 자동 탐색(본인 PC에서 정상 출력)
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

ROOT = Path(__file__).parents[1]
TONE = ROOT / "processed/tone/tone_monthly.csv"
H1 = ROOT / "processed/analysis/h1_concordance.csv"
DEV = ROOT / "processed/analysis/deviation_monthly.csv"
PHASE = ROOT / "processed/analysis/phase_assignments.csv"
ANOM = ROOT / "processed/analysis/anomaly_annotations.csv"
FIG = ROOT / "processed/figures"
FIG.mkdir(parents=True, exist_ok=True)

for cand in ["Malgun Gothic", "AppleGothic", "NanumGothic", "NanumBarunGothic", "Apple SD Gothic Neo"]:
    if any(cand == f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.family"] = cand
        break
plt.rcParams["axes.unicode_minus"] = False


def tone_timeline():
    df = pd.read_csv(TONE)
    x = range(len(df))
    fig, ax = plt.subplots(figsize=(11, 4.2))
    names = {"tone_inflation": "물가(긴축)", "tone_growth": "성장(긴축)",
             "tone_finstab": "금융안정", "tone_fiscal": "재정(긴축)"}
    for c, lab in names.items():
        if c in df:
            ax.plot(x, df[c], label=lab, linewidth=1.6)
    ax.axhline(0, color="gray", lw=0.7, ls="--")
    step = max(1, len(df)//10)
    ax.set_xticks(list(x)[::step]); ax.set_xticklabels(df["period"][::step], rotation=45, fontsize=8)
    ax.set_ylabel("톤 (긴축 +1 / 완화 −1)"); ax.set_title("정책 톤 4축 월별 추이")
    ax.legend(ncol=4, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    fig.tight_layout(); fig.savefig(FIG/"tone_timeline.png", dpi=130, bbox_inches="tight"); plt.close(fig)


def h1_heatmap():
    d = pd.read_csv(H1)
    tones = ["inflation", "growth", "finstab", "fiscal"]
    cols = ["deposit", "loan", "realestate", "inflation", "currency", "invest"]
    klab = {"inflation": "물가", "growth": "성장", "finstab": "금융안정", "fiscal": "재정",
            "deposit": "예금", "loan": "대출", "realestate": "부동산", "currency": "환율", "invest": "투자"}
    import numpy as np
    M = np.full((len(tones), len(cols)), np.nan)
    for _, r in d.iterrows():
        if r["tone"] in tones and r["search"] in cols:
            M[tones.index(r["tone"]), cols.index(r["search"])] = r["align"]
    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(M, cmap="RdYlGn", vmin=-0.5, vmax=0.5, aspect="auto")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels([klab[c]+"검색" for c in cols])
    ax.set_yticks(range(len(tones))); ax.set_yticklabels([klab[t]+"(긴축)" for t in tones])
    for i in range(len(tones)):
        for j in range(len(cols)):
            v = M[i, j]
            ax.text(j, i, "무관" if pd.isna(v) else f"{v:.2f}", ha="center", va="center", fontsize=9)
    ax.set_title("정책 긴축 → 시민 검색 '이론 일치'(초록) vs 괴리(빨강)")
    fig.colorbar(im, label="정합도", shrink=0.8)
    fig.tight_layout(); fig.savefig(FIG/"h1_heatmap.png", dpi=130, bbox_inches="tight"); plt.close(fig)


def deviation_timeline():
    df = pd.read_csv(DEV)
    x = range(len(df))
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.bar(x, df["D_deviation"], color="#D85A30", width=0.9)
    ax.plot(x, df["REV_loan_re"], color="#185FA5", lw=1.4, label="대출·부동산 역방향(REV)")
    if ANOM.exists():
        an = pd.read_csv(ANOM)
        pmap = {p: i for i, p in enumerate(df["period"])}
        for _, r in an.iterrows():
            p = str(r["period"])
            if p in pmap:
                ax.annotate(p, (pmap[p], df["D_deviation"].iloc[pmap[p]]),
                            fontsize=7, rotation=90, va="bottom", ha="center", color="#444")
    step = max(1, len(df)//10)
    ax.set_xticks(list(x)[::step]); ax.set_xticklabels(df["period"][::step], rotation=45, fontsize=8)
    ax.set_ylabel("괴리 D"); ax.set_title("이론 괴리·이상치 타임라인"); ax.legend(fontsize=9)
    fig.tight_layout(); fig.savefig(FIG/"deviation_timeline.png", dpi=130, bbox_inches="tight"); plt.close(fig)


def phase_tsne():
    df = pd.read_csv(PHASE)
    if "tsne_x" not in df:
        return
    fig, ax = plt.subplots(figsize=(7, 6))
    for ph, g in df.groupby("phase"):
        ax.scatter(g["tsne_x"], g["tsne_y"], label=f"국면 {ph}", s=40, alpha=0.8)
    ax.set_title("국면 군집 (t-SNE)"); ax.set_xticks([]); ax.set_yticks([])
    ax.legend(fontsize=9, loc="best")
    fig.tight_layout(); fig.savefig(FIG/"phase_tsne.png", dpi=130, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    for fn in [tone_timeline, h1_heatmap, deviation_timeline, phase_tsne]:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except Exception as e:
            print(f"  ✗ {fn.__name__}: {e}")
    print(f"→ {FIG}/ 에 PNG 저장")
