"""
기획재정부 보도자료 수집 (재정정책 발표문)  [수정본 2026-06-16]
수집 대상: 경제정책방향 · 예산안 · 추가경정예산 · 국가재정운용계획 (2016~2024)
출력: raw/moef/moef_YYYYMM_제목.txt

[v5 수정 내역]
- (버그4) '추경' 부분문자열이 차관 이름 '추경호'에 오매칭 → 동정 보도 88건 오수집.
  → '추경' 단독 키워드 제거. '추가경정예산'/'추경예산'만 인정 + EXCLUDE(이름·동정·행사) 배제.
- (방침) '월간 재정동향' 등 단순 발간 안내 제외.
- (버그5) 본문에 GNB/푸터 보일러플레이트("바로가기 메뉴", "전자정부 누리집" 등) 혼입
  → clean_text()로 네비/안내 라인 제거.
- 수집 구간 2016~2024 (분석 구간 축소 반영).

참고: 도메인은 수집 당시 동작한 mofe.go.kr 유지(정식 도메인은 moef.go.kr).
"""

import time
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUT_DIR = Path(__file__).parents[1] / "raw" / "moef"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://mofe.go.kr"
BBS_ID   = "MOSFBBS_000000000028"
MENU_NO  = "4010100"
LIST_URL   = f"{BASE_URL}/nw/nes/nesdta.do?bbsId={BBS_ID}&menuNo={MENU_NO}"
DETAIL_URL = f"{BASE_URL}/nw/nes/detailNesDtaView.do"

DEBUG = "--debug" in sys.argv
YEAR_MIN, YEAR_MAX = 2016, 2024   # 분석 구간

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": BASE_URL,
}

# ── 필터 (버그4 수정 핵심) ──────────────────
# 포함: 실질 정책 문서만. '추경' 단독은 쓰지 않는다(이름 '추경호' 오매칭 방지).
INCLUDE_KEYWORDS = [
    "경제정책방향", "하반기 경제정책", "예산안", "세입예산",
    "추가경정예산", "추경예산", "국가재정운용계획",
]
# 제외: 인물·동정·행사·단순발간 (월간 재정동향 포함)
EXCLUDE_KEYWORDS = [
    "추경호", "차관", "장관", "면담", "축사", "출국", "방문", "간담회",
    "참석", "컨퍼런스", "포럼", "세미나", "리플렛", "공개토론회", "토론회",
    "착수회의", "월간 재정동향", "재정동향", "발간", "동향",
    "기사 관련", "제하", "해명", "설명자료",
]

# 본문 보일러플레이트 라인 패턴 (버그5)
BOILERPLATE = [
    "바로가기", "누리집", "메인메뉴", "본문 바로가기", "메뉴 바로가기",
    "로그인", "회원가입", "사이트맵", "검색어", "통합검색", "글자크기",
    "담당부서", "담당자", "연락처", "첨부파일", "다운로드", "이전글", "다음글",
    "목록", "인쇄", "페이스북", "트위터", "공유", "copyright", "All Rights",
    "기획재정부", "정부세종청사", "전화", "대표전화",
]


def safe_filename(s: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "_", s)[:50]


def parse_date_from_str(text: str) -> str:
    m = re.search(r"(\d{4})[.\-/](\d{2})[.\-/]?\d*", text)
    return f"{m.group(1)}{m.group(2)}" if m else ""


def extract_ntt_id(href: str) -> str:
    m = re.search(r"fn_egov_select\(['\"]([^'\"]+)['\"]", href)
    return m.group(1) if m else ""


def build_detail_url(ntt_id: str) -> str:
    return f"{DETAIL_URL}?searchBbsId1={BBS_ID}&searchNttId1={ntt_id}&menuNo={MENU_NO}"


def is_policy_target(title: str) -> bool:
    """포함 키워드 1개 이상 + 제외 키워드 0개."""
    if any(ex in title for ex in EXCLUDE_KEYWORDS):
        return False
    return any(inc in title for inc in INCLUDE_KEYWORDS)


def clean_text(raw: str) -> str:
    """보일러플레이트/네비 라인 제거."""
    lines = []
    for ln in raw.split("\n"):
        s = ln.strip()
        if not s or len(s) < 2:
            continue
        if any(bp in s for bp in BOILERPLATE):
            continue
        lines.append(s)
    # 연속 중복 제거
    out, prev = [], None
    for s in lines:
        if s != prev:
            out.append(s)
        prev = s
    return "\n".join(out)


def get_list_page(session: requests.Session, page: int) -> tuple[list[dict], bool]:
    url = f"{LIST_URL}&pageIndex={page}"
    try:
        resp = session.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"  목록 요청 오류 (page {page}): {e}")
        return [], True

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for a in soup.select("a[href*='fn_egov_select']"):
        href, title = a.get("href", ""), a.get_text(strip=True)
        if not href or not title:
            continue
        ntt_id = extract_ntt_id(href)
        if not ntt_id:
            continue
        date_str = ""
        parent = a.find_parent(["li", "div", "tr"])
        if parent:
            m = re.search(r"(\d{4}\.\d{2}\.\d{2})", parent.get_text(" ", strip=True))
            if m:
                date_str = m.group(1)
        items.append({"title": title, "url": build_detail_url(ntt_id), "date": date_str})

    if not items:
        return [], True
    is_last = f"pageIndex={page + 1}" not in resp.text
    return items, is_last


def extract_article_text(session: requests.Session, url: str) -> str:
    resp = session.get(url, headers={**HEADERS, "Referer": LIST_URL}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    for sel in ["div.cont_area", "div.view_con", "div.bbs_content", "div.content_area",
                "div.bbs_view", "div.view_cont", "div.cont_view", "div#content_area",
                "div.board_view", "article", "div#cont_area", "div.view_body"]:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True)) > 100:
            return clean_text(el.get_text(separator="\n", strip=True))

    body = soup.body
    if body:
        for tag in body.select("header, footer, nav, script, style, .header, .footer, .gnb, .lnb, .snb"):
            tag.decompose()
        return clean_text(body.get_text(separator="\n", strip=True))
    return clean_text(soup.get_text(separator="\n", strip=True))


def collect_moef():
    existing = {f.stem for f in OUT_DIR.glob("*.txt")}
    print(f"이미 수집된 파일: {len(existing)}개\n목록 URL: {LIST_URL}")

    session = requests.Session()
    try:
        session.get(BASE_URL, headers=HEADERS, timeout=20)
        time.sleep(0.5)
    except Exception as e:
        print(f"  세션 초기화 경고: {e}")

    page, stop, total = 1, False, 0
    while not stop:
        print(f"\n[페이지 {page}]")
        items, is_last = get_list_page(session, page)
        if not items:
            print("  항목 없음. 종료.")
            break

        for item in items:
            yyyymm = parse_date_from_str(item["date"])
            year = int(yyyymm[:4]) if len(yyyymm) >= 4 else None
            if year and year < YEAR_MIN:
                print(f"  {YEAR_MIN} 이전 도달 → 종료.")
                stop = True
                break
            if year and year > YEAR_MAX:
                continue
            if not is_policy_target(item["title"]):
                if DEBUG:
                    print(f"  필터제외: {item['title'][:40]}")
                continue

            fname = f"moef_{yyyymm}_{safe_filename(item['title'])}"
            if fname in existing:
                continue
            try:
                text = extract_article_text(session, item["url"])
                if len(text) < 100:
                    print(f"  본문 짧음 스킵: {item['title'][:40]}")
                    continue
                (OUT_DIR / f"{fname}.txt").write_text(
                    f"[URL] {item['url']}\n[DATE] {item['date']}\n"
                    f"[TITLE] {item['title']}\n\n{text}", encoding="utf-8")
                existing.add(fname)
                total += 1
                print(f"  ✅ {item['date']} | {item['title'][:45]}")
                time.sleep(0.8)
            except Exception as e:
                print(f"  오류: {item['title'][:30]} - {e}")

        if is_last:
            print("  마지막 페이지.")
            break
        page += 1
        time.sleep(1.2)

    print(f"\n기재부 수집 완료. 신규 {total}개 → {OUT_DIR}")
    print("기존 노이즈 파일 정리: python scripts/clean_moef.py")


if __name__ == "__main__":
    collect_moef()
