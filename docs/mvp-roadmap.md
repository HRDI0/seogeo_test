# 구현 상태 (우선순위 반영)

## 1) Google OAuth 및 토큰 저장소

- `GoogleOAuthService`
  - 인증 URL 생성
  - authorization code 교환
  - refresh token 갱신
- `FileTokenStore`
  - 사이트/클라이언트 key 기반 JSON 저장

## 2) GA4/GSC 실데이터 커넥터

- `RealGA4Connector`
  - `runReport` 호출
  - Organic/Referral/Conversions 요약 집계
- `RealGSCConnector`
  - Search Analytics 호출
  - 전월/당월 query 지표 병합

## 3) Prompt API 커넥터

- `OpenAIPromptTracker`
- `GeminiPromptTracker`
- `PerplexityPromptTracker`

공통 `BaseApiPromptTracker`로 결과를 `PromptResult`로 정규화.

## 4) Browser 추적기

- `PlaywrightPromptTracker`
  - 프롬프트별 screenshot + HTML snapshot 저장
  - 런타임 의존성(playwright) 없을 경우 명확한 예외 반환

## 5) 엑셀 템플릿 Writer

- `SeoGeoExcelWriter`
  - 템플릿 복사 후 시트별 셀 작성
  - `리포트개요`, `GEO프롬프트테스트결과`, `중위키워드추적`, `월간종합리포트`
  - 런타임 의존성(openpyxl) 없을 경우 명확한 예외 반환

## 남은 작업

- 실제 운영용 engine별 browser adapter (로그인/네비게이션)
- 키워드/프롬프트 대량 처리용 큐/스케줄러 통합
- 엑셀 시트별 정확 셀 매핑 검증 (실양식 기준)
