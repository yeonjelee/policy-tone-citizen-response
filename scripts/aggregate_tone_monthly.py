"""
문서별 톤 → 월별 톤 시계열 (LOCF)  [2026-06-16]
입력: processed/tone/doc_tone.csv
출력: processed/tone/tone_monthly.csv  (period=YYYY-MM, 2016-01~2024-12)

규칙(METHODOLOGY §1·§2):
  - 소스 라우팅: inflation·growth·finstab = 한은(mpb+min), fiscal = 기재부(moef).
  - 같은 달 여러 문서 → 표현수(np+nn) 가중평균.
  - 정책기조 지속 가정 → 빈 달은 LOCF(직전값 유지).
  - 부호 = 긴축(+1)/완화(−1).

주의: fiscal 은 eKoNLPy(통화 사전)로 표본 희소→불안정(현재 +1 고정). 커스텀 재정사전
      적용 전까지 '잠정'. inflation·growth·finstab 우선 사용.
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parents[1]
OUT  = ROOT / "processed" / "tone"
AXES = ["inflation", "growth", "finstab", "fiscal"]
ROUTE = {"inflation": ["mpb", "min"], "growth": ["mpb", "min"],
         "finstab": ["mpb", "min"], "fiscal": ["moef"]}


def month_index():
    return [f"{y}-{m:02d}" for y in range(2016, 2025) for m in range(1, 13)]


def run():
    df = pd.read_csv(OUT / "doc_tone.csv", dtype={"date": str})
    df = df[df["date"].str.len() >= 6].copy()
    df["period"] = df["date"].str[:4] + "-" + df["date"].str[4:6]

    out = pd.DataFrame({"period": month_index()})
    for a in AXES:
        sub = df[df["source"].isin(ROUTE[a])].copy()
        sub["w"] = sub[f"np_{a}"].fillna(0) + sub[f"nn_{a}"].fillna(0)
        sub = sub[sub[f"tone_{a}"].notna() & (sub["w"] > 0)]
        sub["wx"] = sub[f"tone_{a}"] * sub["w"]
        gp = sub.groupby("period")
        g = (gp["wx"].sum() / gp["w"].sum()).rename(a)     # 가중평균(경고 없음)
        out = out.merge(g, on="period", how="left")
        out[a] = out[a].ffill()                            # LOCF
    out = out.rename(columns={a: f"tone_{a}" for a in AXES})

    (OUT / "tone_monthly.csv").unlink(missing_ok=True)
    out.to_csv(OUT / "tone_monthly.csv", index=False, encoding="utf-8-sig")
    print(f"→ tone_monthly.csv ({len(out)}개월)")
    for a in AXES:
        col = f"tone_{a}"
        n = out[col].notna().sum()
        rng = f"{out[col].min():+.2f}~{out[col].max():+.2f}" if n else "n/a"
        print(f"  {col}: 채워진 달 {n}/{len(out)}  범위 {rng}")
    out["y"] = out["period"].str[:4]
    print("\n연도별 평균(긴축=+1):")
    print(out.groupby("y")[[f"tone_{a}" for a in AXES]].mean().round(2).to_string())


if __name__ == "__main__":
    run()
