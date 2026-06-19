"""
정책 톤 점수 산출  [v2 · 2026-06-16]
  - inflation·growth·finstab : 한은 결정문·의사록(mpb·min) → eKoNLPy 축별 점수
  - fiscal                   : 기재부(moef) → 커스텀 재정사전(fiscal_lexicon) 문서단위 점수

부호 = 긴축(+1)/완화·확장(−1) 통일(METHODOLOGY §2).
  tone = (P − N)/(P + N).

출력: processed/tone/doc_tone.csv
  doc_id, source, date(YYYYMM), quarter,
  tone_inflation/growth/finstab/fiscal, 각 축 표본수 np_*/nn_*

선행: MOEF는 recollect_moef.py 로 본문(PDF) 재수집 후 실행해야 fiscal 이 유의미.
의존성: kiwipiepy, ekonlpy
실행: python scripts/score_tone.py
"""

import sys
from pathlib import Path

import pandas as pd
from kiwipiepy import Kiwi
from ekonlpy.sentiment import MPKO

sys.path.insert(0, str(Path(__file__).parent))
from preprocess_tone import (AXIS_KEYWORDS, SOURCES, parse_meta, to_quarter,
                             is_boiler, tag_axes)
from fiscal_lexicon import score_fiscal

ROOT = Path(__file__).parents[1]
OUT  = ROOT / "processed" / "tone"
MON_AXES = ["inflation", "growth", "finstab"]   # eKoNLPy(BOK)
ALL_AXES = MON_AXES + ["fiscal"]

kiwi = Kiwi()
mpko = MPKO()


def score_monetary(path: Path) -> dict:
    """BOK 문서: eKoNLPy 로 inflation/growth/finstab."""
    _, body = parse_meta(path, "bok")
    acc = {a: [0, 0] for a in MON_AXES}
    for sent in kiwi.split_into_sents(body):
        s = sent.text.strip()
        if is_boiler(s):
            continue
        axes = [a for a in tag_axes(s) if a in MON_AXES]
        if not axes:
            continue
        toks = mpko.tokenize(s)
        if not toks:
            continue
        sc = mpko.get_score(toks)
        for a in axes:
            acc[a][0] += sc["Positive"]
            acc[a][1] += abs(sc["Negative"])
    return acc


def score_doc(path: Path, source: str) -> dict:
    date, body = parse_meta(path, source)
    row = {"doc_id": path.stem, "source": source, "date": date,
           "quarter": to_quarter(date)}
    # 기본 None
    for a in ALL_AXES:
        row[f"tone_{a}"] = None
        row[f"np_{a}"] = 0
        row[f"nn_{a}"] = 0

    if source in ("mpb", "min"):
        acc = score_monetary(path)
        for a in MON_AXES:
            p, n = acc[a]
            row[f"tone_{a}"] = (p - n) / (p + n) if (p + n) > 0 else None
            row[f"np_{a}"], row[f"nn_{a}"] = p, n
    elif source == "moef":
        P, N, pol = score_fiscal(body)          # 문서단위 재정사전
        row["tone_fiscal"] = pol
        row["np_fiscal"], row["nn_fiscal"] = P, N
    return row


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for source, d in SOURCES:
        files = sorted(d.glob("*.txt")) if d.is_dir() else []
        print(f"[{source}] {len(files)}개 점수화...")
        for j, p in enumerate(files, 1):
            try:
                rows.append(score_doc(p, source))
            except Exception as e:
                print(f"  x {p.name}: {e}")
            if j % 20 == 0:
                print(f"    {j}/{len(files)}")
    if not rows:
        print("점수화할 문서 없음."); return

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    (OUT / "doc_tone.csv").unlink(missing_ok=True)
    df.to_csv(OUT / "doc_tone.csv", index=False, encoding="utf-8-sig")
    print(f"\n→ processed/tone/doc_tone.csv ({len(df)}문서)")

    df["year"] = df["date"].str[:4]
    print("\n연도 | infl  growth finstab | fiscal(MOEF)  (긴축=+1)")
    for y, g in df.groupby("year"):
        bok = g[g.source.isin(["mpb", "min"])]
        moef = g[g.source == "moef"]
        vals = [bok[f"tone_{a}"].mean() for a in MON_AXES]
        fv = moef["tone_fiscal"].mean()
        s = "  ".join(f"{v:+.2f}" if pd.notna(v) else " n/a " for v in vals)
        fs = f"{fv:+.2f}" if pd.notna(fv) else " n/a "
        print(f"{y} | {s} | {fs}")


if __name__ == "__main__":
    run()
