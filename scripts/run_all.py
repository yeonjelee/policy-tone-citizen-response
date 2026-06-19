"""
전체 데이터 수집 실행 스크립트

실행 전 준비:
  1. .env.example 을 복사하여 .env 생성 후 API 키 입력
  2. pip install -r requirements.txt

실행:
  python scripts/run_all.py [--skip 단계명]
  예) python scripts/run_all.py --skip bok_mpb,bok_minutes  (크롤링 제외)
"""

import sys
import argparse
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

STEPS = [
    ("ecos",        "collect_ecos.py",        "ECOS 거시변수 (기준금리·CPI·환율)"),
    ("kosis",       "collect_kosis.py",        "KOSIS 실업률"),
    ("krx",         "collect_krx.py",          "KRX KOSPI 수익률"),
    ("naver",       "collect_naver.py",         "네이버 데이터랩 검색트렌드"),
    ("bok_mpb",     "collect_bok_mpb.py",       "한은 통화정책방향 결정문"),
    ("bok_minutes", "collect_bok_minutes.py",   "금통위 의사록"),
    ("moef",        "collect_moef.py",          "기재부 재정정책 발표문"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip", default="", help="건너뛸 단계 이름 (쉼표 구분)")
    parser.add_argument("--only", default="", help="이 단계만 실행 (쉼표 구분)")
    args = parser.parse_args()

    skip_set = set(args.skip.split(",")) if args.skip else set()
    only_set = set(args.only.split(",")) if args.only else set()

    print("=" * 60)
    print("데이터 수집 시작")
    print("=" * 60)

    results = {}
    for name, script, desc in STEPS:
        if name in skip_set:
            print(f"\n[스킵] {desc}")
            continue
        if only_set and name not in only_set:
            continue

        print(f"\n{'─'*50}")
        print(f"▶  {desc}")
        print(f"{'─'*50}")

        ret = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / script)],
            cwd=str(SCRIPTS_DIR.parent)
        )
        results[name] = "✅ 완료" if ret.returncode == 0 else "❌ 오류"

    print("\n" + "=" * 60)
    print("수집 결과 요약")
    print("=" * 60)
    for name, status in results.items():
        print(f"  {status}  {name}")


if __name__ == "__main__":
    main()
