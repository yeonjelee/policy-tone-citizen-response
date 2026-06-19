# 참고 문헌 (Related Work)

본 프로젝트의 세 축(정책 톤 측정 · 검색 반응 · 미디어 프레이밍)은 각각 확립된 문헌 위에 있다.
아래는 핵심 선행연구와 우리 설계와의 연결.

## 1. 정책 어조 측정 — 텍스트마이닝 톤/감성 지수

- **박기영·이영준·김수현 등, "텍스트 마이닝을 활용한 금융통화위원회 의사록 분석"** (한국은행).
  경제·금융 용어 형태소분석기 **eKoNLPy** + 감성사전 구축 → 금통위 의사록 hawkish/dovish 톤 지수.
  https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE07999969
  → *우리 BoW/축별 사전·연속 톤 지수의 직접적 선행. eKoNLPy 극성사전을 시드로 사용.*
- **유각준·조두연, "한국은행 총재의 통화정책 커뮤니케이션이 금융시장에 미치는 영향: 감성 분석 중심"** (한국은행).
  https://www.bok.or.kr/portal/bbs/P0000556/view.do?menuNo=500838&nttId=10093818
- **BIS, "Machine learning for measuring central bank policy"** (IFC Bulletin).
  https://www.bis.org/ifc/publ/ifcb59_24.pdf
- Hawkish-Dovish(HD) 지수 계열 — 매파(+1)~비둘기(−1) 스케일 + Semantic Orientation(사전 공기빈도) 방식.
  → *우리 `−1~+1` 스케일과 `(P−N)/(P+N)` net-tone의 근거.*
  ECB WP: https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2085.en.pdf

## 2. 검색량 = 대중 반응/주의(attention)의 대리지표

- **OECD, Google Trends 기반 주간 경제활동 추적** — 소비·주택·고용 검색이 경제활동 예측.
  https://oecdecoscope.blog/2020/12/14/can-google-trends-be-used-to-track-economic-activity-in-real-time1/
- NAVER 상대검색량(RSV) 활용(한국 맥락) 예: COVID-19 위험인식 연구.
  https://www.medrxiv.org/content/10.1101/2020.04.23.20077552.full.pdf
  → *검색을 시민 반응 프록시로 쓰는 표준적 접근.*

## 3. 미디어 프레이밍 → 기대·행동 (H2)

- **Lamla & Lein, "The Role of Media for Consumers' Inflation Expectation Formation."**
  미디어가 **보도량(volume) 채널 vs 논조(tone) 채널** 두 경로로 기대에 영향.
  https://www.sciencedirect.com/science/article/abs/pii/S0167268114001450
  → *"프레이밍이 반응을 조절한다"(H2)의 이론적 근거.*
- **SF Fed, "Can the News Drive Inflation Expectations?"** — 뉴스가 가계 기대를 움직이며,
  고물가 뉴스가 **비대칭적으로** 더 크게 작용. *우리 '이론 이탈/이상치'와 연결.*
  https://www.frbsf.org/research-and-insights/publications/economic-letter/2022/11/can-news-drive-inflation-expectations/
- NBER, "The Causal Effect of News on Inflation Expectations." https://www.nber.org/papers/w34088

## 본 연구의 차별점

선행연구는 보통 한 축씩 다룬다. 본 연구는 (1) 정책 톤 + (2) 네이버 검색 반응 +
(3) **언론사 정치성향별** 프레이밍을 하나로 결합하고, **이론 기대부호로부터의 괴리**를
이상치로 보아 **정책-시민 국면을 군집화**하며, 결과를 **금융상품 매핑**으로 잇는다(한국·네이버 맥락).

## 사용 리소스

- **eKoNLPy** (Korean economic NLP, sentiment lexicon) — 금통위 톤 사전. 우리 4축 방향 사전의 시드.
  https://github.com/entelecheia/eKoNLPy
