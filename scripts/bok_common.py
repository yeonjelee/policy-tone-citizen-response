"""
한국은행 통화정책방향 회의 페이지 공통 크롤링 유틸  [재작성 v7 · 2026-06-16]
collect_bok_mpb.py / collect_bok_minutes.py 가 공유.

[디버그 HTML 분석으로 확인된 실제 구조 — v6까지 0건이던 진짜 원인]
1) 연도 선택이 GET(year=)이 아니라 POST 폼(name=stsfdgForm, <select name="pYear">).
   → 이전엔 ?year=YYYY 가 무시돼 항상 기본(최근)연도 1개 페이지만 받았음.
2) 결정문/의사록 본문이 HTML이 아니라 HWP/PDF '첨부파일'.
   표 컬럼:  회의일자(th) | 결정문(td0) | 기자간담회(td1) | 의사록(td2) | 이슈(td3)
   각 셀의 <a title="...pdf"> = /portal/cmmn/file/fileDown.do?...&fileSn=N
3) 회의일자 셀에 연도가 없음("01월 15일(목)") → 연도는 요청한 pYear 사용.

→ POST(pYear)로 연도별 표를 받고, 결정문=td0 / 의사록=td2 의 PDF를 내려받아
  pdfplumber 로 텍스트 추출.
"""

import io
import re
import requests
import pdfplumber
from bs4 import BeautifulSoup

BASE_URL = "https://www.bok.or.kr"
LIST_URL = f"{BASE_URL}/portal/singl/crncyPolicyDrcMtg/listYear.do"
MENU_NO  = "200755"

# 표에서 종류별 td 인덱스 (th=회의일자는 별도)
COL = {"decision": 0, "minutes": 2}

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": f"{LIST_URL}?mtgSe=A&menuNo={MENU_NO}",
}


def fetch_year_html(session: requests.Session, year: int) -> str:
    """연도별 표 페이지. 사이트 JS(yearMove)와 동일하게 GET + 'pYear' 사용.
    (v6는 틀린 'year=' → 무시, v7 POST → 500. 정답은 GET pYear.)"""
    url = f"{LIST_URL}?mtgSe=A&menuNo={MENU_NO}&pYear={year}"
    resp = session.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_rows(html: str, year: int, kind: str, debug: bool = False) -> list[tuple[str, str, str]]:
    """반환: [(yyyymm, 파일다운로드URL, 파일제목), ...]  kind=decision|minutes"""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="tableId") or soup.find("table")
    out: list[tuple[str, str, str]] = []
    if not table:
        if debug:
            print(f"  [디버그] {year}: 표 없음")
        return out
    col = COL[kind]
    body = table.find("tbody") or table
    for tr in body.find_all("tr"):
        th = tr.find("th")
        tds = tr.find_all("td")
        if not th or len(tds) <= col:
            continue
        mm = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", th.get_text(" ", strip=True))
        if not mm:
            continue
        yyyymm = f"{year}{int(mm.group(1)):02d}"
        url, title = _pick_file(tds[col])
        if url:
            out.append((yyyymm, url, title))
    if debug:
        print(f"  [디버그] {year} {kind}: {len(out)}건")
    return out


def _pick_file(cell) -> tuple[str, str]:
    """셀에서 PDF 우선, 없으면 HWP 다운로드 링크 추출."""
    for ext in (".pdf", ".hwp"):
        for a in cell.find_all("a", href=True):
            title = (a.get("title") or "").lower()
            if title.endswith(ext) and "fileDown" in a["href"]:
                href = a["href"].replace("&amp;", "&")
                full = BASE_URL + href if href.startswith("/") else href
                return full, a.get("title", "")
    return "", ""


def download_text(session: requests.Session, url: str) -> str:
    """PDF면 pdfplumber로 추출. HWP/기타면 빈 문자열(스킵 신호)."""
    r = session.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    if r.content[:4] != b"%PDF":
        return ""   # PDF 아님(예: HWP) → 호출부에서 스킵/경고
    pages = []
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        for pg in pdf.pages:
            pages.append(pg.extract_text() or "")
    return "\n".join(pages).strip()
