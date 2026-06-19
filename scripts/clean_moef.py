"""
기존 raw/moef/*.txt 정리  [2026-06-16]
- collect_moef.py 와 동일한 INCLUDE/EXCLUDE 기준 + 2016~2024 구간을 적용해
  노이즈(추경호 동정·행사·월간 재정동향 등)와 구간 밖 파일을 골라낸다.
- 기본은 '미리보기'(이동 안 함). 실제 이동은:  python scripts/clean_moef.py --apply
- 삭제 대신 raw/moef/_excluded/ 로 이동 (복구 가능).
- --apply 시, 유지 파일의 본문 보일러플레이트도 함께 정제한다.
"""

import re
import sys
import shutil
from pathlib import Path

MOEF_DIR = Path(__file__).parents[1] / "raw" / "moef"
EXC_DIR  = MOEF_DIR / "_excluded"
APPLY    = "--apply" in sys.argv
YEAR_MIN, YEAR_MAX = 2016, 2024

INCLUDE_KEYWORDS = [
    "경제정책방향", "하반기 경제정책", "예산안", "세입예산",
    "추가경정예산", "추경예산", "국가재정운용계획",
]
EXCLUDE_KEYWORDS = [
    "추경호", "차관", "장관", "면담", "축사", "출국", "방문", "간담회",
    "참석", "컨퍼런스", "포럼", "세미나", "리플렛", "공개토론회", "토론회",
    "착수회의", "월간 재정동향", "재정동향", "발간", "동향",
    "기사 관련", "제하", "해명", "설명자료",
]
BOILERPLATE = [
    "바로가기", "누리집", "메인메뉴", "본문 바로가기", "메뉴 바로가기",
    "로그인", "회원가입", "사이트맵", "검색어", "통합검색", "글자크기",
    "담당부서", "담당자", "연락처", "첨부파일", "다운로드", "이전글", "다음글",
    "목록", "인쇄", "페이스북", "트위터", "공유", "copyright", "All Rights",
    "기획재정부", "정부세종청사", "전화", "대표전화",
]


def is_policy_target(title: str) -> bool:
    if any(ex in title for ex in EXCLUDE_KEYWORDS):
        return False
    return any(inc in title for inc in INCLUDE_KEYWORDS)


def parse(fname: str):
    m = re.match(r"moef_(\d{6})_(.*)", fname)
    if not m:
        return None, None
    return m.group(1), m.group(2)


def clean_body(path: Path):
    """본문에서 보일러플레이트 라인 제거 (헤더 [URL]/[DATE]/[TITLE] 보존)."""
    txt = path.read_text(encoding="utf-8")
    parts = txt.split("\n\n", 1)
    if len(parts) != 2:
        return
    header, body = parts
    out, prev = [], None
    for ln in body.split("\n"):
        s = ln.strip()
        if not s or len(s) < 2 or any(bp in s for bp in BOILERPLATE):
            continue
        if s != prev:
            out.append(s)
        prev = s
    path.write_text(header + "\n\n" + "\n".join(out), encoding="utf-8")


def main():
    files = sorted(MOEF_DIR.glob("moef_*.txt"))
    keep, drop = [], []
    for f in files:
        yyyymm, title = parse(f.stem)
        if yyyymm is None:
            drop.append((f, "형식불일치"))
            continue
        year = int(yyyymm[:4])
        if not (YEAR_MIN <= year <= YEAR_MAX):
            drop.append((f, f"구간밖({year})"))
        elif not is_policy_target(title):
            drop.append((f, "노이즈/비정책"))
        else:
            keep.append(f)

    print(f"총 {len(files)}건 -> 유지 {len(keep)} / 제외 {len(drop)}")
    print("\n[제외 예시 20건]")
    for f, why in drop[:20]:
        print(f"  - ({why}) {f.name[:60]}")

    if not APPLY:
        print("\n미리보기입니다. 실제 이동하려면:  python scripts/clean_moef.py --apply")
        return

    EXC_DIR.mkdir(exist_ok=True)
    for f, _ in drop:
        shutil.move(str(f), str(EXC_DIR / f.name))
    for f in keep:
        clean_body(f)
    print(f"\n{len(drop)}건을 {EXC_DIR} 로 이동. 유지 {len(keep)}건 본문 정제 완료.")


if __name__ == "__main__":
    main()
