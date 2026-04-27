# SEOGEO 리포트 자동 생성기

`SEOGEO_리포트양식.xlsx` 템플릿을 기준으로 아래 5개 우선순위를 코드로 진행한 상태입니다.

1. Google OAuth 및 토큰 저장소 구현
2. GA4/GSC 실데이터 커넥터 구현
3. Prompt API 커넥터(OpenAI/Gemini/Perplexity) 구현
4. Browser 추적기(Playwright) 구현
5. 엑셀 템플릿 셀 매핑 Writer 구현

## 포함 기능

- OAuth URL 생성 / 코드 교환 / 토큰 갱신 / 파일 토큰 저장소
- GA4 Data API (`runReport`) 커넥터
- GSC Search Analytics 커넥터 (전월/당월 키워드 병합)
- Prompt API 트래커
  - OpenAI Responses + web search
  - Gemini grounding
  - Perplexity
- Playwright 기반 브라우저 추적기 (스크린샷/HTML 저장)
- 엑셀 작성기 (`openpyxl` 설치 시 동작)
- 월간 파이프라인 + CLI 실행기

## Hybrid AI Visibility 추적 구조

이 프로젝트는 API-only가 아닌 하이브리드 추적 구조를 지원하도록 확장했습니다.

- Prompt Library: `src/seogeo_reporter/prompt_library.py`
- Hybrid Pipeline: `src/seogeo_reporter/hybrid_pipeline.py`
- Capture/Signal 모델: `src/seogeo_reporter/hybrid_models.py`
- Parsing: `src/seogeo_reporter/parsing.py`
- Metrics: `src/seogeo_reporter/scoring.py`
- SERP 수집기 스텁: `src/seogeo_reporter/serp_collectors.py`
- 환경설정 로더/검증: `src/seogeo_reporter/config.py`

가시성 등급(Tier 0~4):
- Tier 0: 브랜드 미언급
- Tier 1: 브랜드 언급
- Tier 2: 브랜드 + 제3자 citation
- Tier 3: 브랜드 + 공식 도메인 citation
- Tier 4: 상위 추천/긍정 문맥 + 공식 citation

## 배포/보안 준비

- 배포 가이드: `docs/deployment-vercel-render-r2.md`
- 인프라 템플릿: `deploy/render.yaml`
- 환경변수 예시:
  - `deploy/vercel.env.example`
  - `deploy/render.env.example`
- 토큰 암호화 모듈: `src/seogeo_reporter/security.py`
- 암호화 저장소: `SecureTokenStore` (`src/seogeo_reporter/auth.py`)

## 배치 실행 엔트리포인트

```bash
python -m src.seogeo_reporter.runner
```

환경변수:
- `REPORT_MONTH` (기본: 전월 자동 계산)
- `RUN_MODE` (`mock`/`real`)
- `PROMPT_MODE` (`mock`/`openai`/`gemini`/`perplexity`/`browser`)
- `TOKEN_STORE_MODE` (`plain`/`encrypted`)

## 전체 기능 테스트 스크립트

```bash
scripts/test_all_features.sh
```

스크립트에서 수행하는 항목:
- 단위 테스트 전체 실행
- CLI mock 프롬프트 모드 실행/JSON 검증
- OAuth URL 출력/JSON 검증
- browser 모드 의도된 실패(playwright 미설치) 검증
- `openpyxl` 설치 시 엑셀 출력 검증(미설치 시 skip)

## 빠른 실행 (Mock)

```bash
python -m src.seogeo_reporter.cli --month 2026-03 --mode mock --prompt-mode mock
```

## OAuth URL 출력

```bash
python -m src.seogeo_reporter.cli --month 2026-03 --print-oauth-url
```

## 실데이터 실행 예시

```bash
python -m src.seogeo_reporter.cli \
  --month 2026-03 \
  --mode real \
  --prompt-mode openai \
  --property-id 123456789 \
  --access-token "$GOOGLE_ACCESS_TOKEN"
```

## 엑셀 파일 출력

```bash
python -m src.seogeo_reporter.cli --month 2026-03 --excel-out out/report_2026-03.xlsx
```

> `openpyxl` 미설치 환경에서는 엑셀 출력 시 예외가 발생합니다.
> `playwright` 미설치 환경에서는 browser 모드 실행 시 예외가 발생합니다.
