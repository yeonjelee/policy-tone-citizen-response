"""
H2 — 보도 부정 논조가 정책-시민 괴리를 설명하는가  [2026-06-16]  (METHODOLOGY §6)

프레이밍 변수 F = 기사 제목의 부정 논조 강도(news_tone), 분기 집계.
검증: F 가 괴리 D / 대출·부동산 역방향 REV / 이상치와 연관되는가.
  '같은 정책이라도 보도가 공격적일 때 시민 불안 반응이 더 컸나'

입력: raw/news/articles.csv, processed/analysis/deviation_monthly.csv
출력: processed/analysis/h2_framing_quarterly.csv + 콘솔(상관)
의존성: pandas, scipy
"""
import sys
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
from news_tone import score_negativity

ROOT = Path(__file__).parents[1]
OUTD = ROOT / "processed" / "analysis"
# 토픽 → 관련 정책 톤축(부정논조를 비교할 맥락)
FISCAL_TOPICS = {"fiscal"}


def to_q(yyyymmdd):
    s = str(yyyymmdd)
    return f"{s[:4]}Q{(int(s[4:6])-1)//3 + 1}"


def run():
    OUTD.mkdir(parents=True, exist_ok=True)
    a = pd.read_csv(ROOT / "raw/news/articles.csv", dtype=str)
    a["neg"] = a["title"].map(lambda t: score_negativity(t)[2])
    a = a.dropna(subset=["neg"])
    a["neg"] = a["neg"].astype(float)
    a["q"] = a["date"].map(to_q)

    # 분기별 부정논조 F (전체 + 토픽군)
    F = a.groupby("q")["neg"].mean().rename("F_neg_all")
    Fre = a[a["topic"].isin(["realestate", "loan"])].groupby("q")["neg"].mean().rename("F_neg_re_loan")
    n_art = a.groupby("q").size().rename("n_articles")

    # 괴리(월→분기)
    dev = pd.read_csv(OUTD / "deviation_monthly.csv")
    dev["q"] = dev["period"].astype(str).str[:4] + "Q" + \
        ((dev["period"].astype(str).str[5:7].astype(int) - 1)//3 + 1).astype(str)
    devq = dev.groupby("q")[["D_deviation", "REV_loan_re"]].mean()

    df = pd.concat([F, Fre, n_art, devq], axis=1).dropna(subset=["F_neg_all", "D_deviation"])
    (OUTD / "h2_framing_quarterly.csv").unlink(missing_ok=True)
    df.to_csv(OUTD / "h2_framing_quarterly.csv", encoding="utf-8-sig")

    print(f"분기 {len(df)}개 | 기사 {int(a.shape[0]):,}건")
    print("\n[H2 상관 — 보도 부정논조 F vs 괴리]")
    for fx in ["F_neg_all", "F_neg_re_loan"]:
        for dy in ["D_deviation", "REV_loan_re"]:
            sub = df[[fx, dy]].dropna()
            if len(sub) >= 8:
                rho, p = spearmanr(sub[fx], sub[dy])
                star = "*" if p < 0.05 else ("." if p < 0.1 else "")
                print(f"  {fx:16} ~ {dy:12}: ρ={rho:+.2f} (p={p:.2f}){star}  n={len(sub)}")

    print("\n[부정논조 상위 6분기]")
    print(df.sort_values("F_neg_all", ascending=False).head(6)[
        ["F_neg_all", "F_neg_re_loan", "D_deviation", "REV_loan_re", "n_articles"]].round(2).to_string())
    print(f"\n→ {OUTD/'h2_framing_quarterly.csv'}")


if __name__ == "__main__":
    run()
