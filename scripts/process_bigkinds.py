"""
빅카인즈 다운로드 엑셀 → 정제 기사 데이터  [v3 · 2026-06-16]
(크롤러 collect_bigkinds.py 의 '수동 다운로드' 폴백. 비로그인 검색이 막혔거나
 본문 전체가 필요할 때 사용. 출력 포맷은 크롤러와 동일.)

[수집 절차]
1) https://www.bigkinds.or.kr 로그인 → '뉴스 분석'
2) 기간 2016-01-01 ~ 2024-12-31, 토픽별 검색식 입력
   * 정치 중립 = 키워드 검열이 아니라 '언론사 균형'. 보수 조중동만 쓰지 말고
     진보(한겨레·경향)·중도·경제지를 모두 포함(전체 선택 권장).
3) STEP 03 '데이터 다운로드'로 엑셀 저장(많으면 연도/반기 분할)
4) 토픽 폴더에 넣기: raw/news_inbox/<토픽>/*.xlsx  (폴더명이 topic 으로 기록)
5) 실행:  python scripts/process_bigkinds.py

[출력]
- raw/news/articles.csv               (일자·분기·언론사·성향·제목·키워드·URL·topic)
- raw/news/news_quarterly_counts.csv  (분기 × 토픽)
- raw/news/news_quarterly_by_lean.csv (분기 × 매체성향)
"""

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from news_outlets import classify_lean

ROOT  = Path(__file__).parents[1]
INBOX = ROOT / "raw" / "news_inbox"
OUT   = ROOT / "raw" / "news"
SUGGESTED = ["monetary", "fiscal", "deposit", "loan", "realestate",
             "inflation", "currency", "invest"]
Y_MIN, Y_MAX = 2016, 2024


def find_col(cols, *keys):
    for k in keys:
        for c in cols:
            if k in str(c):
                return c
    return None


def norm_date(v) -> str:
    s = re.sub(r"[^0-9]", "", str(v))
    return s[:8] if len(s) >= 8 else ""


def to_quarter(ymd: str) -> str:
    y, m = int(ymd[:4]), int(ymd[4:6])
    return f"{y}Q{(m - 1)//3 + 1}"


def load_file(path: Path, topic: str) -> pd.DataFrame:
    df = pd.read_excel(path, dtype=str) if path.suffix.lower() in (".xlsx", ".xls") \
        else pd.read_csv(path, dtype=str)
    cols = df.columns
    c = {
        "date":  find_col(cols, "일자", "날짜", "date"),
        "press": find_col(cols, "언론사", "press"),
        "title": find_col(cols, "제목", "title"),
        "kw":    find_col(cols, "키워드", "특성추출", "keyword"),
        "url":   find_col(cols, "URL", "url", "원문"),
        "id":    find_col(cols, "뉴스 식별자", "식별자", "id"),
    }
    if c["date"] is None or c["title"] is None:
        print(f"  ✗ {path.name}: 날짜/제목 컬럼 못 찾음 (컬럼: {list(cols)[:6]}...)")
        return pd.DataFrame()
    press = df[c["press"]] if c["press"] else ""
    out = pd.DataFrame({
        "news_id":  df[c["id"]] if c["id"] else "",
        "date":     df[c["date"]].map(norm_date),
        "press":    press,
        "press_lean": (press.map(classify_lean) if c["press"] else "etc"),
        "title":    df[c["title"]],
        "keywords": df[c["kw"]] if c["kw"] else "",
        "url":      df[c["url"]] if c["url"] else "",
        "topic":    topic,
    })
    out = out[out["date"].str.len() == 8].copy()
    out["year"] = out["date"].str[:4].astype(int)
    out = out[(out["year"] >= Y_MIN) & (out["year"] <= Y_MAX)]
    out["quarter"] = out["date"].map(to_quarter)
    return out


def gather():
    files = []
    if INBOX.is_dir():
        for d in sorted(p for p in INBOX.iterdir() if p.is_dir()):
            for p in list(d.glob("*.xls*")) + list(d.glob("*.csv")):
                files.append((p, d.name))
    for p in list(INBOX.glob("*.xls*")) + list(INBOX.glob("*.csv")):
        files.append((p, "all"))
    return files


def run():
    INBOX.mkdir(parents=True, exist_ok=True)
    for t in SUGGESTED:
        (INBOX / t).mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    files = gather()
    if not files:
        print(f"입력 없음. 빅카인즈 엑셀을 {INBOX}/<토픽>/ 에 넣으세요.")
        print(f"추천 토픽 폴더: {', '.join(SUGGESTED)}")
        return

    frames = []
    for p, topic in files:
        df = load_file(p, topic)
        if not df.empty:
            print(f"  ✓ {topic}/{p.name}: {len(df)}건")
            frames.append(df)
    if not frames:
        print("정제 가능한 데이터 없음.")
        return

    raw = pd.concat(frames, ignore_index=True)
    before = len(raw)
    has_id = raw["news_id"].astype(str).str.len().gt(0)
    alldf = pd.concat([
        raw[has_id].drop_duplicates(subset=["news_id"]),
        raw[~has_id].drop_duplicates(subset=["title", "date"]),
    ], ignore_index=True).sort_values("date").reset_index(drop=True)
    print(f"\n총 {before}건 → 중복 제거 후 {len(alldf)}건")

    alldf.to_csv(OUT / "articles.csv", index=False, encoding="utf-8-sig")
    qs = [f"{y}Q{q}" for y in range(Y_MIN, Y_MAX + 1) for q in range(1, 5)]
    alldf.groupby(["quarter", "topic"]).size().unstack(fill_value=0).reindex(qs, fill_value=0)\
         .to_csv(OUT / "news_quarterly_counts.csv", encoding="utf-8-sig")
    alldf.groupby(["quarter", "press_lean"]).size().unstack(fill_value=0).reindex(qs, fill_value=0)\
         .to_csv(OUT / "news_quarterly_by_lean.csv", encoding="utf-8-sig")

    print(f"→ raw/news/articles.csv ({len(alldf)}건)")
    print(f"  성향분포: {alldf['press_lean'].value_counts().to_dict()}")
    print(f"  기간 {alldf['date'].min()} ~ {alldf['date'].max()}")


if __name__ == "__main__":
    run()
