"""
정책 텍스트 전처리 → 문장 분할 → 축 태깅 → 문서×축 BoW  [2026-06-16]

입력: raw/bok_mpb/*.txt (결정문), raw/bok_minutes/*.txt (의사록), raw/moef/*.txt (재정)
출력(processed/tone/):
  - doc_meta.csv      : 문서 메타(doc_id, source, date, quarter, n_sent, n_token)
  - sentences.csv     : 문장 단위(doc_id, sent_idx, quarter, source, axes, has_neg, sentence)
  - doc_axis_bow.csv  : 문서×축 BoW 롱포맷(doc_id, source, quarter, axis, token, tag, count)

설계 메모:
  - 점수화는 '문서별'로 산출(추후 분기/문장 어떤 단위로든 재집계 가능).
  - 결정문 1건이 물가·성장·금융·재정 문단을 다 담으므로, 문장을 '축'에 태깅한 뒤
    축별 토큰만 모은다(BoW가 4축 섞이지 않게). 복수 축 허용.
  - 방향(+/-) 사전·스케일은 이 단계에서 정하지 않는다. 토큰화·축 분리까지만.
  - has_neg(부정문 표시)는 추후 부정어 처리용으로 미리 기록.

의존성: pip install kiwipiepy
실행:  python scripts/preprocess_tone.py   (의사록이 길어 수 분 소요)
"""

import re
import sys
from pathlib import Path

import pandas as pd
from kiwipiepy import Kiwi

ROOT = Path(__file__).parents[1]
OUT  = ROOT / "processed" / "tone"
SOURCES = [
    ("mpb", ROOT / "raw" / "bok_mpb"),
    ("min", ROOT / "raw" / "bok_minutes"),
    ("moef", ROOT / "raw" / "moef"),
]

# 축 태깅 키워드(주제어). 방향어(둔화·확대 등)는 여기 넣지 않는다 → 점수화 단계 몫.
AXIS_KEYWORDS = {
    "inflation": ["물가", "소비자물가", "인플레", "디스인플레", "기대인플레",
                  "근원물가", "물가상승", "오름세", "cpi"],
    "growth":    ["성장", "경기", "고용", "일자리", "취업", "실업", "내수",
                  "수출", "설비투자", "경제성장", "경제활동", "gdp", "생산", "소비"],
    "finstab":   ["금융안정", "금융시장", "금융불균형", "가계부채", "부채", "레버리지",
                  "자본유출", "외환", "환율", "신용", "시스템리스크", "거시건전성",
                  "자산가격", "주택가격", "금융기관"],
    "fiscal":    ["재정", "예산", "추경", "추가경정", "국채", "재정수지", "재정건전성",
                  "세입", "세출", "국가채무", "재정지출", "국가재정", "적자", "흑자"],
}

# 본문에서 제외할 boilerplate 신호(문장에 포함되면 버림)
BOILERPLATE = ["문의처", "공보관", "Tel", "Fax", "E-mail", "전화", "배포시",
               "보도자료는", "인터넷", "수록되어", "취급하여", "붙임 참조"]

# 유지할 형태소 품사(내용어)
KEEP_TAGS = {"NNG", "NNP", "VV", "VA", "VV-I", "VA-I", "VX-I", "MAG", "XR", "SL"}
NEG_FORMS = {"않", "없", "못", "아니", "안"}

DEBUG = "--debug" in sys.argv
kiwi = Kiwi()


def parse_meta(path: Path, source: str):
    """파일에서 날짜(YYYYMM)·본문 추출."""
    text = path.read_text(encoding="utf-8", errors="replace")
    body = text
    date = ""
    for line in text.splitlines()[:6]:
        m = re.match(r"\[DATE\]\s*([0-9.\-]+)", line)
        if m:
            date = re.sub(r"[^0-9]", "", m.group(1))[:6]
    if "\n\n" in text:
        body = text.split("\n\n", 1)[1]
    if len(date) < 6:
        m = re.search(r"(\d{6})", path.stem)
        date = m.group(1) if m else ""
    return date, body


def to_quarter(yyyymm: str) -> str:
    if len(yyyymm) < 6:
        return ""
    y, m = int(yyyymm[:4]), int(yyyymm[4:6])
    return f"{y}Q{(m - 1)//3 + 1}"


def is_boiler(s: str) -> bool:
    return any(b in s for b in BOILERPLATE) or len(s.strip()) < 6


def tag_axes(sent: str) -> list:
    low = sent.lower()
    return [ax for ax, kws in AXIS_KEYWORDS.items() if any(k in low for k in kws)]


def process_doc(path: Path, source: str):
    date, body = parse_meta(path, source)
    quarter = to_quarter(date)
    doc_id = path.stem

    sent_rows, bow_rows = [], []
    n_tok = 0
    # return_tokens=True: 문장분할 단계의 형태소를 재사용(재토큰화 생략 → 속도↑)
    for i, sent in enumerate(kiwi.split_into_sents(body, return_tokens=True)):
        s = sent.text.strip()
        if is_boiler(s):
            continue
        axes = tag_axes(s)
        toks = sent.tokens
        content = [(t.form, t.tag) for t in toks if t.tag in KEEP_TAGS and len(t.form) > 1]
        has_neg = any(t.form in NEG_FORMS for t in toks)
        n_tok += len(content)

        sent_rows.append({
            "doc_id": doc_id, "sent_idx": i, "quarter": quarter, "source": source,
            "axes": "|".join(axes), "has_neg": int(has_neg), "sentence": s,
        })
        for ax in (axes or ["none"]):
            for form, tag in content:
                bow_rows.append({"doc_id": doc_id, "source": source, "quarter": quarter,
                                 "axis": ax, "token": form, "tag": tag})

    meta = {"doc_id": doc_id, "source": source, "date": date, "quarter": quarter,
            "n_sent": len(sent_rows), "n_token": n_tok}
    return meta, sent_rows, bow_rows


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    metas, sents, bows = [], [], []
    for source, d in SOURCES:
        files = sorted(d.glob("*.txt")) if d.is_dir() else []
        print(f"[{source}] {len(files)}개 문서 처리...")
        for j, p in enumerate(files, 1):
            try:
                m, sr, br = process_doc(p, source)
            except Exception as e:
                print(f"  x {p.name}: {e}")
                continue
            metas.append(m); sents.extend(sr); bows.extend(br)
            if j % 20 == 0:
                print(f"    {j}/{len(files)}")

    if not metas:
        print("처리할 문서 없음. raw/bok_mpb·bok_minutes·moef 확인.")
        return

    df_meta = pd.DataFrame(metas)
    df_sent = pd.DataFrame(sents)
    df_bow = (pd.DataFrame(bows)
              .groupby(["doc_id", "source", "quarter", "axis", "token", "tag"])
              .size().reset_index(name="count"))

    for name, unlink_first in [("doc_meta.csv", df_meta), ("sentences.csv", df_sent),
                               ("doc_axis_bow.csv", df_bow)]:
        (OUT / name).unlink(missing_ok=True)   # 덮어쓰기 truncation 방지
    df_meta.to_csv(OUT / "doc_meta.csv", index=False, encoding="utf-8-sig")
    df_sent.to_csv(OUT / "sentences.csv", index=False, encoding="utf-8-sig")
    df_bow.to_csv(OUT / "doc_axis_bow.csv", index=False, encoding="utf-8-sig")

    print(f"\n문서 {len(df_meta)} · 문장 {len(df_sent)} · BoW행 {len(df_bow)}")
    ax_counts = {}
    for axs in df_sent["axes"]:
        for a in (axs.split("|") if axs else ["none"]):
            ax_counts[a] = ax_counts.get(a, 0) + 1
    print("축별 문장 수(복수 태깅 포함):")
    for a in ["inflation", "growth", "finstab", "fiscal", "none"]:
        print(f"  {a}: {ax_counts.get(a, 0)}")
    print(f"\n-> {OUT}/ (doc_meta, sentences, doc_axis_bow)")


if __name__ == "__main__":
    run()
