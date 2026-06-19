"""
빅카인즈(BigKinds) 기사 크롤러  [v2 · 이어받기(resume) 지원 · 2026-06-16]
출력: raw/news/articles.csv + news_quarterly_counts.csv + news_quarterly_by_lean.csv
구간: 2016-01-01 ~ 2024-12-31

[이어받기]
- 수집 단위 = (토픽 × 검색어 × 연도). 단위가 끝날 때마다
  중간결과를 raw/news/_articles_partial.csv 에 '추가 저장'하고
  raw/news/_checkpoint.json 에 완료 단위를 기록한다.
- 중간에 멈춰도, 다시 실행하면 이미 끝난 단위는 건너뛰고 '멈춘 지점부터' 이어서 수집.
- 처음부터 다시 하려면:  python scripts/collect_bigkinds.py --reset

모든 언론사를 수집(providerCodes 비움)하고 news_outlets.classify_lean 으로
매체 성향을 라벨링한다. 실행:
  python scripts/collect_bigkinds.py [--debug] [--reset]
"""

import re
import sys
import json
import time
from pathlib import Path

import requests
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from news_outlets import classify_lean

ROOT = Path(__file__).parents[1]
OUT  = ROOT / "raw" / "news"
PARTIAL = OUT / "_articles_partial.csv"
CKPT    = OUT / "_checkpoint.json"

DEBUG = "--debug" in sys.argv
RESET = "--reset" in sys.argv

BASE = "https://www.bigkinds.or.kr"
SEARCH_URL = f"{BASE}/api/news/search.do"
Y_MIN, Y_MAX = 2016, 2024
PAGE = 100
MAX_PER_QUERY = 10000

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Content-Type": "application/json;charset=UTF-8",
    "Referer": f"{BASE}/v2/news/index.do",
    "Origin": BASE,
}

TOPICS = {
    "monetary":  ["기준금리", "통화정책", "한국은행 금리"],
    "fiscal":    ["추가경정예산", "예산안", "재정정책", "국가재정"],
    "deposit":   ["예금금리", "정기예금"],
    "loan":      ["대출금리", "주택담보대출", "가계대출"],
    "realestate":["부동산 정책", "집값", "주택시장"],
    "inflation": ["소비자물가", "물가상승", "인플레이션"],
    "currency":  ["원달러 환율", "환율"],
    "invest":    ["재테크", "주식투자"],
}

COLUMNS = ["news_id", "date", "quarter", "press", "press_lean", "title", "topic", "url"]


# ── 체크포인트 ────────────────────────────
def load_done() -> set:
    if CKPT.exists():
        try:
            return set(json.loads(CKPT.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def save_done(done: set):
    CKPT.write_text(json.dumps(sorted(done), ensure_ascii=False), encoding="utf-8")


def append_rows(rows: list):
    if not rows:
        return
    df = pd.DataFrame(rows, columns=COLUMNS)
    df.to_csv(PARTIAL, mode="a", header=not PARTIAL.exists(), index=False, encoding="utf-8")


# ── 빅카인즈 호출 ─────────────────────────
def make_session() -> requests.Session:
    s = requests.Session()
    try:
        s.get(f"{BASE}/v2/news/index.do", headers=HEADERS, timeout=20)
    except Exception:
        pass
    return s


def search_page(session, key, sd, ed, start_no):
    body = {
        "indexName": "news", "searchKey": key, "searchKeys": [{}], "byLine": "",
        "searchFilterType": "1", "searchScopeType": "1",
        "searchSortType": "date", "sortMethod": "date",
        "startDate": sd, "endDate": ed,
        "categoryCodes": [], "providerCodes": [], "incidentCodes": [], "dateCodes": [],
        "editorialIs": False, "startNo": start_no, "resultNumber": PAGE,
        "isTmUsable": False, "isNotTmUsable": False,
    }
    r = session.post(SEARCH_URL, data=json.dumps(body), headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def _get(d, *keys):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
        for dk in d:
            if dk.lower() == k.lower() and d[dk] not in (None, ""):
                return d[dk]
    return ""


def extract_list(resp) -> list:
    for k in ("resultList", "documentList", "newsList", "list", "data"):
        v = resp.get(k) if isinstance(resp, dict) else None
        if isinstance(v, list):
            return v
        if isinstance(v, dict) and isinstance(v.get("list"), list):
            return v["list"]
    return []


def norm_date(v) -> str:
    s = re.sub(r"[^0-9]", "", str(v))
    return s[:8] if len(s) >= 8 else ""


def to_quarter(ymd: str) -> str:
    y, m = int(ymd[:4]), int(ymd[4:6])
    return f"{y}Q{(m - 1)//3 + 1}"


def fetch_unit(session, key, year, debug_state) -> list:
    """한 단위(검색어×연도)의 전체 페이지 수집."""
    sd, ed = f"{year}-01-01", f"{year}-12-31"
    rows, start_no = [], 1
    while start_no <= MAX_PER_QUERY:
        resp = search_page(session, key, sd, ed, start_no)
        if DEBUG and not debug_state["dumped"]:
            (ROOT / "debug_bigkinds_search.json").write_text(
                json.dumps(resp, ensure_ascii=False)[:20000], encoding="utf-8")
            print(f"  [디버그] 첫 응답 키: {list(resp)[:8]}")
            debug_state["dumped"] = True
        items = extract_list(resp)
        if not items:
            break
        for it in items:
            ymd = norm_date(_get(it, "DATE", "date", "newsDate", "PUBLISH_DATE"))
            if len(ymd) != 8:
                continue
            press = _get(it, "PROVIDER", "provider", "PRESS", "providerName")
            rows.append({
                "news_id": _get(it, "NEWS_ID", "newsId", "id"),
                "date": ymd, "quarter": to_quarter(ymd),
                "press": press, "press_lean": classify_lean(press),
                "title": re.sub("<[^>]+>", "", str(_get(it, "TITLE", "title"))),
                "topic": None,   # 호출부에서 채움
                "url": _get(it, "PROVIDER_LINK_PAGE", "url", "URL", "providerLinkPage"),
            })
        start_no += PAGE
        if len(items) < PAGE:
            break
        time.sleep(0.3)
    return rows


# ── 최종 집계 ─────────────────────────────
def finalize():
    if not PARTIAL.exists():
        print("누적 데이터 없음.")
        return
    df = pd.read_csv(PARTIAL, dtype=str)
    has_id = df["news_id"].astype(str).str.len().gt(0)
    df = pd.concat([
        df[has_id].drop_duplicates(subset=["news_id"]),
        df[~has_id].drop_duplicates(subset=["title", "date"]),
    ], ignore_index=True).sort_values("date").reset_index(drop=True)
    df.to_csv(OUT / "articles.csv", index=False, encoding="utf-8-sig")

    qs = [f"{y}Q{q}" for y in range(Y_MIN, Y_MAX + 1) for q in range(1, 5)]
    df.groupby(["quarter", "topic"]).size().unstack(fill_value=0).reindex(qs, fill_value=0)\
      .to_csv(OUT / "news_quarterly_counts.csv", encoding="utf-8-sig")
    df.groupby(["quarter", "press_lean"]).size().unstack(fill_value=0).reindex(qs, fill_value=0)\
      .to_csv(OUT / "news_quarterly_by_lean.csv", encoding="utf-8-sig")

    print(f"\n→ raw/news/articles.csv ({len(df)}건)  기간 {df['date'].min()}~{df['date'].max()}")
    print(f"  성향분포: {df['press_lean'].value_counts().to_dict()}")


def collect():
    OUT.mkdir(parents=True, exist_ok=True)
    if RESET:
        PARTIAL.unlink(missing_ok=True)
        CKPT.unlink(missing_ok=True)
        print("[reset] 체크포인트·누적파일 삭제, 처음부터 수집")

    # 전체 단위 목록
    units = [(t, k, y) for t, keys in TOPICS.items() for k in keys
             for y in range(Y_MIN, Y_MAX + 1)]
    done = load_done()
    todo = [u for u in units if f"{u[0]}|{u[1]}|{u[2]}" not in done]
    print(f"전체 {len(units)}단위 · 완료 {len(done)} · 남음 {len(todo)}")
    if not todo:
        print("모든 단위 완료. 최종 집계만 수행.")
        finalize()
        return

    session = make_session()
    debug_state = {"dumped": False}
    new_done = 0
    for topic, key, year in todo:
        uid = f"{topic}|{key}|{year}"
        try:
            rows = fetch_unit(session, key, year, debug_state)
        except KeyboardInterrupt:
            print("\n[중단] 사용자 중지. 지금까지 진행분은 저장됨. 다시 실행하면 이어집니다.")
            break
        except Exception as e:
            print(f"  ✗ {uid}: 요청오류 {e} (이 단위는 다음 실행에서 재시도)")
            continue
        for r in rows:
            r["topic"] = topic
        append_rows(rows)            # 중간결과 즉시 누적 저장
        done.add(uid)
        save_done(done)              # 체크포인트 갱신
        new_done += 1
        print(f"  ✓ {uid}: {len(rows)}건  (진행 {len(done)}/{len(units)})")
        time.sleep(0.2)

    print(f"\n이번 실행 신규 완료 {new_done}단위. 누적 완료 {len(done)}/{len(units)}.")
    if len(done) >= len(units):
        finalize()
        print("전체 완료 → 최종 CSV 생성.")
    else:
        print("아직 남은 단위 있음. 다시 실행하면 이어서 수집합니다.")
        print("현재까지 분으로 집계만 보려면 임시로 다시 실행 후 자동 finalize를 기다리세요.")


if __name__ == "__main__":
    collect()
