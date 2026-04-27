# AI Visibility / AEO·GEO Hybrid Architecture

## 목표

- API-only 추적의 한계를 보완하기 위해,
  - LLM API 응답 수집
  - SERP/AI Overview 수집
  - 실제 UI 브라우저 캡처
  를 결합한 하이브리드 추적 파이프라인을 구성한다.

## 파이프라인

1. Prompt Library 생성 (직접형/카테고리형/비교형/문제해결형/지역형)
2. Execution Layer
   - API tracker (OpenAI/Gemini/Perplexity)
   - SERP collector (Google AI Overview)
   - Browser tracker (Playwright)
3. Capture Layer
   - raw text
   - citation URLs
   - HTML/screenshot/source-panel
4. Parsing Layer
   - mention/citation/official-domain/competitor/sentiment/position
5. Scoring Layer
   - Mention Rate
   - Citation Rate
   - Official Link Rate
   - Share of Voice (추가 예정)
   - Tier 0~4

## 구현된 모듈

- `src/seogeo_reporter/prompt_library.py`
- `src/seogeo_reporter/hybrid_pipeline.py`
- `src/seogeo_reporter/hybrid_models.py`
- `src/seogeo_reporter/parsing.py`
- `src/seogeo_reporter/scoring.py`
- `src/seogeo_reporter/serp_collectors.py`

## 단계별 권장 운영

- 기본: API 대량 수집
- 검증: 상위 중요 프롬프트만 브라우저 캡처
- 확장: SERP API + UI 캡처 비교로 데이터 품질 교차 검증
