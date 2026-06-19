"""
한은 결정문·의사록 PDF → 텍스트 변환 (비크롤링 대안)  [2026-06-16]

크롤링이 막히거나 불안하면, 한은 사이트에서 PDF를 직접 내려받아 이 스크립트로
한 번에 텍스트화한다. 어조 라벨링 입력으로 그대로 쓸 수 있다.

[사용법]
1) 한국은행 → 통화정책 → 통화정책방향 회의 페이지에서 연도를 바꿔가며
   '결정문'(국문보도자료)·'의사록' PDF를 내려받는다.
   https://www.bok.or.kr/portal/singl/crncyPolicyDrcMtg/listYear.do?mtgSe=A&menuNo=200755&pYear=2024
2) 받은 파일을 아래 폴더에 넣는다(파일명에 'YYYY-MM' 또는 'YYYYMM' 포함 권장):
   raw/bok_pdf_inbox/mpb/        ← 결정문 PDF
   raw/bok_pdf_inbox/minutes/    ← 의사록 PDF
   (날짜를 파일명에 못 넣으면 PDF 본문 첫 부분에서 날짜를 자동 추출 시도)
3) 실행:  python scripts/extract_bok_pdfs.py
   → raw/bok_mpb/bok_mpb_YYYYMM.txt , raw/bok_minutes/bok_min_YYYYMM.txt 생성
"""

import re
from pathlib import Path

import pdfplumber

ROOT     = Path(__file__).parents[1]
INBOX    = ROOT / "raw" / "bok_pdf_inbox"
JOBS = [
    ("mpb",     INBOX / "mpb",     ROOT / "raw" / "bok_mpb",     "bok_mpb"),
    ("minutes", INBOX / "minutes", ROOT / "raw" / "bok_minutes", "bok_min"),
]


def pdf_to_text(path: Path) -> str:
    pages = []
    with pdfplumber.open(path) as pdf:
        for pg in pdf.pages:
            pages.append(pg.extract_text() or "")
    return "\n".join(pages).strip()


def yyyymm_from_name(name: str) -> str:
    m = re.search(r"(20\d{2})[._\-]?(0[1-9]|1[0-2])", name)
    return f"{m.group(1)}{m.group(2)}" if m else ""


def yyyymm_from_text(text: str) -> str:
    # 본문 앞부분의 'YYYY년 M월' 또는 'YYYY. M. D' 패턴
    head = text[:600]
    m = re.search(r"(20\d{2})\s*[.년]\s*(\d{1,2})\s*[.월]", head)
    return f"{m.group(1)}{int(m.group(2)):02d}" if m else ""


def run():
    grand = 0
    for kind, in_dir, out_dir, prefix in JOBS:
        in_dir.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)
        pdfs = sorted(in_dir.glob("*.pdf"))
        print(f"\n[{kind}] 입력 {len(pdfs)}개 ← {in_dir}")
        for p in pdfs:
            try:
                text = pdf_to_text(p)
            except Exception as e:
                print(f"  ✗ {p.name}: PDF 오류 {e}")
                continue
            if len(text) < 100:
                print(f"  ✗ {p.name}: 텍스트 짧음({len(text)}자) — 스캔본일 수 있음")
                continue
            ym = yyyymm_from_name(p.name) or yyyymm_from_text(text)
            if not ym:
                print(f"  ✗ {p.name}: 날짜 식별 실패 → 파일명에 YYYY-MM 추가 후 재시도")
                continue
            out = out_dir / f"{prefix}_{ym}.txt"
            out.write_text(f"[SOURCE] {p.name}\n[DATE] {ym}\n\n{text}", encoding="utf-8")
            grand += 1
            print(f"  ✓ {ym} ← {p.name} ({len(text):,}자)")
    print(f"\n총 {grand}개 텍스트 생성.")
    if grand == 0:
        print("입력 PDF가 없습니다. raw/bok_pdf_inbox/mpb · minutes 에 PDF를 넣으세요.")


if __name__ == "__main__":
    run()
