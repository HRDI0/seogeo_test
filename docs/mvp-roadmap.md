# MVP 로드맵

## Phase 1 — GA4/GSC + 엑셀 자동 채우기

- OAuth scope 최소화
  - GA4: `analytics.readonly`
  - GSC: `webmasters.readonly`
- 수집 스키마 확정
  - `ga4_monthly_metrics`
  - `gsc_query_metrics`
- 템플릿 탭 매핑
  - `중위키워드추적`
  - `월간종합리포트`

## Phase 2 — API 기반 프롬프트 추적

- 공통 `PromptTracker` 인터페이스로 엔진별 구현
  - OpenAI Responses + web_search
  - Gemini grounding
  - Perplexity Sonar
- 실행 결과 정규화
  - citations
  - official link 여부
  - 브랜드 언급 위치
- Tier 자동 판정

## Phase 3 — Browser 기반 검증

- Playwright 워커 분리
- 스크린샷/HTML snapshot 아티팩트 저장
- UI 기반 신호 추출
  - citation 카드 가시성
  - 링크 노출 여부
  - 추가 패널(소스, 쇼핑, 지도 등)

## 운영 정책

- 기본은 API 모드
- Browser 모드는 검증/증빙용
- 월간 비교를 위해 실행 조건 고정
  - locale: `ko-KR`
  - 지역/계정/시간대 통제
