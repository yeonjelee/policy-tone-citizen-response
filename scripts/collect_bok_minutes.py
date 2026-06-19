"""
금융통화위원회 의사록 수집  [재작성 v7 · 2026-06-16]
출력: raw/bok_minutes/bok_min_YYYYMM.txt  (의사록 PDF → 텍스트)
구간: 2016~2024

실제 구조(디버그 HTML 분석): 연도=POST(pYear), 의사록=표 td2의 PDF 첨부.
의사록은 회의 후 약 6주 뒤 공개 → 최근 회차는 링크가 없을 수 있음.
  python scripts/collect_bok_minutes.py [--debug]
"""

import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
import bok_common as bc

OUT_DIR = Path(__file__).parents[1] / "raw" / "bok_minutes"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DEBUG = "--debug" in sys.argv
YEARS = list(range(2016, 2025))
KIND, PREFIX = "minutes", "bok_min"


def run():
    session = requests.Session()
    session.get(f"{bc.LIST_URL}?mtgSe=A&menuNo={bc.MENU_NO}", headers=bc.HEADERS, timeout=30)
    collected = {f.stem for f in OUT_DIR.glob("*.txt")}
    print(f"이미 수집된 파일: {len(collected)}개")
    total = 0

    for year in YEARS:
        print(f"\n[{year}년]")
        try:
            html = bc.fetch_year_html(session, year)
        except Exception as e:
            print(f"  페이지 오류: {e}")
            continue

        rows = bc.parse_rows(html, year, KIND, debug=DEBUG)
        if not rows:
            print("  의사록 0건 (미공개거나 구조 불일치)")
            if DEBUG:
                p = Path(__file__).parents[1] / f"debug_{PREFIX}_{year}.html"
                p.write_text(html, encoding="utf-8")
                print(f"  [디버그] HTML 저장 → {p.name}")
            continue

        for ym, url, title in rows:
            fname = f"{PREFIX}_{ym}"
            if fname in collected:
                continue
            try:
                text = bc.download_text(session, url)
            except Exception as e:
                print(f"  {ym}: 다운로드 오류 {e}")
                continue
            if len(text) < 100:
                print(f"  {ym}: 텍스트 짧음/PDF아님 ({len(text)}자) — {title}")
                continue
            (OUT_DIR / f"{fname}.txt").write_text(
                f"[URL] {url}\n[DATE] {ym}\n[TITLE] {title}\n\n{text}", encoding="utf-8")
            collected.add(fname)
            total += 1
            print(f"  {ym}: 저장 ({len(text):,}자) {title}")
            time.sleep(0.8)
        time.sleep(1.0)

    print(f"\n수집 완료. 신규 {total}개 → {OUT_DIR}")
    if total == 0 and not collected:
        print("⚠️  0건. 의사록은 회의 후 6주 뒤 공개. --debug 로 표 구조 확인.")


if __name__ == "__main__":
    run()
