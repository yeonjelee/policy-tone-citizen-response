"""
MOEF 본문 재수집 (첨부 PDF → 텍스트)  [2026-06-16]

문제: raw/moef/*.txt 의 본문이 실제 정책내용이 아니라 사이트 메뉴(GNB)였다.
      진짜 내용은 상세페이지의 HWP/PDF 첨부에 있음(PDF 다수 존재). BOK와 동일.
해결: 기존 파일의 [URL](상세페이지)을 다시 방문 → PDF 첨부 다운로드 → 텍스트 추출 →
      해당 .txt 의 본문을 교체(헤더 [URL]/[DATE]/[TITLE] 보존).

목록 재크롤 불필요(이미 90개 URL 보유). mofe.go.kr 접속 필요 → 본인 PC에서 실행.

사용:
  python scripts/recollect_moef.py --debug --limit 2   # 먼저 2건으로 구조 확인
  python scripts/recollect_moef.py                      # 전체 재수집
  (0건/실패 시 저장되는 debug_moef_detail.html 와 출력된 후보 링크를 공유)

의존성: requests, beautifulsoup4, pdfplumber
"""

import io
import re
import sys
import time
from pathlib import Path

import requests
import pdfplumber
from bs4 import BeautifulSoup

MOEF_DIR = Path(__file__).parents[1] / "raw" / "moef"
ROOT = Path(__file__).parents[1]
BASE = "https://mofe.go.kr"
DEBUG = "--debug" in sys.argv
LIMIT = None
for a in sys.argv:
    if a.startswith("--limit"):
        try: LIMIT = int(a.split("=")[-1]) if "=" in a else int(sys.argv[sys.argv.index(a)+1])
        except Exception: LIMIT = 2

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": BASE,
}
DOWN_HINTS = ["filedown", "fms", "downfile", "fn_egov_down", "/down", "fileidx", "atchfile"]
SKIP_NAME  = ["별첨", "참고", "붙임", "붙 임", "info", "양식"]


def read_detail_url(path: Path) -> str:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:4]:
        m = re.match(r"\[URL\]\s*(\S+)", line)
        if m:
            return m.group(1)
    return ""


def abs_url(href: str) -> str:
    if href.startswith("http"):
        return href
    return BASE + href if href.startswith("/") else f"{BASE}/{href}"


def resolve_download(href: str, onclick: str) -> str:
    if href and not href.lower().startswith("javascript") and href != "#":
        return abs_url(href.replace("&amp;", "&"))
    # onclick 안의 (atchFileId, fileSn) 인자 → eGov FileDown 추정
    args = re.findall(r"['\"]([A-Za-z0-9_\-\.]{3,})['\"]", onclick or "")
    if len(args) >= 2:
        return f"{BASE}/cmm/fms/FileDown.do?atchFileId={args[0]}&fileSn={args[1]}"
    if len(args) == 1:
        return f"{BASE}/cmm/fms/FileDown.do?atchFileId={args[0]}&fileSn=0"
    return ""


def find_pdf_links(html: str):
    """(파일명, 다운로드URL) 후보 리스트. PDF 우선, 별첨류 후순위."""
    soup = BeautifulSoup(html, "html.parser")
    cands = []
    for a in soup.find_all("a"):
        name = (a.get_text(strip=True) or "") + " " + (a.get("title") or "")
        href = a.get("href", "") or ""
        onclick = a.get("onclick", "") or ""
        blob = (href + " " + onclick).lower()
        is_pdf = ".pdf" in name.lower()
        is_dl = any(h in blob for h in DOWN_HINTS) or ".pdf" in blob or ".hwp" in blob
        if not (is_pdf or is_dl):
            continue
        url = resolve_download(href, onclick)
        if url:
            cands.append((name.strip()[:60], url, is_pdf))
    # PDF 우선 + 별첨 후순위 정렬
    cands.sort(key=lambda c: (not c[2], any(s in c[0] for s in SKIP_NAME)))
    return cands


def pdf_text(session, url) -> str:
    r = session.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    if r.content[:4] != b"%PDF":
        return ""
    pages = []
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        for pg in pdf.pages:
            pages.append(pg.extract_text() or "")
    return "\n".join(pages).strip()


def run():
    files = sorted(MOEF_DIR.glob("moef_*.txt"))
    if LIMIT:
        files = files[:LIMIT]
    session = requests.Session()
    ok = 0
    dumped = False
    for p in files:
        url = read_detail_url(p)
        if not url:
            print(f"  ✗ {p.name[:40]}: [URL] 없음"); continue
        try:
            html = session.get(url, headers=HEADERS, timeout=30).text
        except Exception as e:
            print(f"  ✗ {p.name[:40]}: 상세 요청오류 {e}"); continue

        cands = find_pdf_links(html)
        if DEBUG and not dumped:
            (ROOT / "debug_moef_detail.html").write_text(html, encoding="utf-8")
            print(f"  [디버그] 상세 HTML 저장 → debug_moef_detail.html")
            print(f"  [디버그] 첨부 후보 {len(cands)}건:")
            for nm, u, isp in cands[:8]:
                print(f"     pdf={isp} | {nm} | {u[:80]}")
            dumped = True

        text = ""
        for nm, u, isp in cands:
            try:
                text = pdf_text(session, u)
            except Exception:
                text = ""
            if len(text) > 300:
                break
        if len(text) < 300:
            print(f"  ✗ {p.name[:40]}: PDF 본문 못 얻음(첨부 {len(cands)}건)"); continue

        head = "\n".join(p.read_text(encoding="utf-8", errors="replace").splitlines()[:3])
        p.write_text(f"{head}\n\n{text}", encoding="utf-8")
        ok += 1
        print(f"  ✓ {p.name[:45]} ({len(text):,}자)")
        time.sleep(0.6)

    print(f"\n재수집 완료. 본문 교체 {ok}/{len(files)}건.")
    if ok == 0:
        print("0건 → debug_moef_detail.html 와 위 '첨부 후보' 출력을 공유하면 링크 패턴을 맞춰드립니다.")


if __name__ == "__main__":
    run()
