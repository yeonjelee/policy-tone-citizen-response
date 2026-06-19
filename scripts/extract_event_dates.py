"""
정책 이벤트 '정확한 날짜' 추출 (일별 이벤트 스터디용)  [2026-06-16]
- BOK 결정문: 본문의 결정일(YYYY년 M월 D일) → 통화정책 이벤트
- 기재부: [DATE] 헤더(YYYY.MM.DD) → 재정정책 이벤트
- doc_tone 와 병합해 각 이벤트의 톤(긴축/완화 부호) 부착

출력: processed/events/policy_events.csv (date, source, doc_id, tone_key, tone)
"""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parents[1]
OUT = ROOT / "processed" / "events"
OUT.mkdir(parents=True, exist_ok=True)
DATE_RE = re.compile(r'(20\d{2})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일')


def bok_date(path):
    m = DATE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None


def moef_date(path):
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:4]:
        m = re.match(r"\[DATE\]\s*(20\d{2})[.\-](\d{2})[.\-](\d{2})", line)
        if m:
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def run():
    tone = pd.read_csv(ROOT / "processed/tone/doc_tone.csv") if (ROOT/"processed/tone/doc_tone.csv").exists() else None
    rows = []
    for f in sorted((ROOT/"raw/bok_mpb").glob("*.txt")):
        d = bok_date(f)
        if not d:
            continue
        r = {"date": d, "source": "mpb", "doc_id": f.stem, "tone_key": "tone_inflation", "tone": None}
        if tone is not None:
            t = tone[tone["doc_id"] == f.stem]
            if len(t):
                r["tone"] = t["tone_inflation"].iloc[0]
        rows.append(r)
    for f in sorted((ROOT/"raw/moef").glob("*.txt")):
        d = moef_date(f)
        if not d:
            continue
        r = {"date": d, "source": "moef", "doc_id": f.stem, "tone_key": "tone_fiscal", "tone": None}
        if tone is not None:
            t = tone[tone["doc_id"] == f.stem]
            if len(t):
                r["tone"] = t["tone_fiscal"].iloc[0]
        rows.append(r)
    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    (OUT/"policy_events.csv").unlink(missing_ok=True)
    df.to_csv(OUT/"policy_events.csv", index=False, encoding="utf-8-sig")
    print(f"정책 이벤트 {len(df)}건 → policy_events.csv")
    print(f"  통화(mpb) {len(df[df.source=='mpb'])} · 재정(moef) {len(df[df.source=='moef'])}")
    print(f"  기간 {df['date'].min()} ~ {df['date'].max()}")
    print(df.head(4)[["date", "source", "tone"]].to_string(index=False))


if __name__ == "__main__":
    run()
