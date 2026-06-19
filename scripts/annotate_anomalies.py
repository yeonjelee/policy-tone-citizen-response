"""
이상치 주석 표 — '왜 이 시점에 이론이 깨졌나'  [2026-06-16]

이상치는 noise가 아니라 기존 정책-반응 관계가 깨진 '구조적 단절점'.
→ (달, 국면, z(D), LOF, 주도 괴리 채널, 추정 원인, 유형) 으로 정리.
유형: 실제사건(structural) / 데이터아티팩트(measurement) 구분(정직한 해석).

입력: processed/analysis/phase_assignments.csv
출력: processed/analysis/anomaly_annotations.csv + ANOMALY_NOTES.md
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parents[1]
A = ROOT / "processed" / "analysis" / "phase_assignments.csv"
OUTD = ROOT / "processed" / "analysis"
TONES = ["tone_inflation", "tone_growth", "tone_finstab", "tone_fiscal"]
SR = ["deposit", "loan", "realestate", "inflation", "currency", "invest"]
E = {"inflation": {"deposit": 1, "loan": -1, "realestate": -1, "inflation": 1, "currency": 1, "invest": -1},
     "growth":    {"deposit": 1, "loan": -1, "realestate": -1, "inflation": 1, "currency": 1, "invest": -1},
     "finstab":   {"deposit": 1, "loan": -1, "realestate": -1, "inflation": 0, "currency": 1, "invest": -1},
     "fiscal":    {"deposit": 1, "loan": -1, "realestate": -1, "inflation": -1, "currency": 0, "invest": -1}}

# 큐레이션된 원인 주석 (도메인 지식; 미상은 자동 채널설명+'확인필요')
EVENTS = {
    "2016-03": ("초기 재정톤 표본부족(MOEF 문서 희소)로 fiscal 톤 불안정", "데이터아티팩트"),
    "2016-04": ("초기 재정톤 표본부족 아티팩트(fiscal×invest 극단 z)", "데이터아티팩트"),
    "2016-05": ("초기 재정톤 표본부족 아티팩트", "데이터아티팩트"),
    "2019-05": ("저물가·미중 무역분쟁·부동산 규제(9.13 여파) — 긴축톤 대비 부동산 관심 잔존", "실제사건"),
    "2020-03": ("코로나19 팬데믹 패닉 — 환율 급등·증시 폭락·긴급 금리인하", "실제사건"),
    "2022-10": ("고강도 긴축 + 레고랜드 자금경색, 부동산 경착륙·전세 불안 — 긴축인데 대출·부동산 검색 급증", "실제사건"),
    "2022-11": ("레고랜드 사태 여진·자금시장 경색 지속", "실제사건"),
    "2024-12": ("비상계엄·정국 충격 — 환율 급등", "실제사건"),
}


def z(x):
    return (x - x.mean()) / x.std(ddof=0)


def run():
    a = pd.read_csv(A)
    zt = {t: z(a[t]) for t in TONES}
    zs = {k: z(a[f"s_{k}"]) for k in SR}
    flagged = a[(a["anom_theory"] == 1) | (a["anom_lof"] == 1)].copy()

    rows = []
    for i, r in flagged.iterrows():
        contribs = {}
        for tn in TONES:
            an = tn.replace("tone_", "")
            for k in SR:
                if E[an][k] == 0:
                    continue
                contribs[f"{an}×{k}"] = E[an][k] * zt[tn][i] * zs[k][i]
        worst = sorted(contribs.items(), key=lambda x: x[1])[:2]
        channel = ", ".join(f"{c}({v:+.1f})" for c, v in worst)
        cause, kind = EVENTS.get(r["period"], (f"주도채널={worst[0][0]}; 원인 확인필요", "확인필요"))
        rows.append({
            "period": r["period"], "phase": r["phase"], "zD": round(r["zD"], 2),
            "anom_theory": int(r["anom_theory"]), "anom_lof": int(r["anom_lof"]),
            "dominant_channel": channel, "추정원인": cause, "유형": kind,
        })
    res = pd.DataFrame(rows).sort_values("period")
    (OUTD / "anomaly_annotations.csv").unlink(missing_ok=True)
    res.to_csv(OUTD / "anomaly_annotations.csv", index=False, encoding="utf-8-sig")

    md = ["# 이상치(이례 시점) 해석\n",
          "정책-시민 관계가 깨진 구조적 단절점. 실제사건 vs 데이터아티팩트 구분.\n",
          "| 시점 | 국면 | z(D) | 탐지 | 주도 괴리 채널 | 추정 원인 | 유형 |",
          "|---|---|---|---|---|---|---|"]
    for _, r in res.iterrows():
        det = ("이론" if r["anom_theory"] else "") + ("·LOF" if r["anom_lof"] else "")
        md.append(f"| {r['period']} | {r['phase']} | {r['zD']:+.1f} | {det} | "
                  f"{r['dominant_channel']} | {r['추정원인']} | {r['유형']} |")
    (ROOT / "ANOMALY_NOTES.md").unlink(missing_ok=True)
    (ROOT / "ANOMALY_NOTES.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"이상치 {len(res)}건 주석 완료 → anomaly_annotations.csv, ANOMALY_NOTES.md")
    print(res[["period", "phase", "zD", "유형", "추정원인"]].to_string(index=False))


if __name__ == "__main__":
    run()
