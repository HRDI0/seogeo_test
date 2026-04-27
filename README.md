# SEOGEO 리포트 자동 생성기 (MVP 설계/스캐폴딩)

이 저장소는 `SEOGEO_리포트양식.xlsx` 템플릿을 기준으로,

1. GA4/GSC API 데이터 수집
2. GEO 프롬프트 추적(API + 브라우저)
3. Tier 자동 판정
4. 월간 엑셀 리포트 출력

을 구현하기 위한 초기 코드 스캐폴딩입니다.

## 현재 포함된 범위

- 도메인 모델 (`src/seogeo_reporter/models.py`)
- Tier 규칙 판정 엔진 (`src/seogeo_reporter/tiering.py`)
- API/브라우저 추적기 인터페이스 (`src/seogeo_reporter/collectors.py`)
- Google 커넥터 인터페이스 (`src/seogeo_reporter/connectors.py`)
- 월간 파이프라인 오케스트레이터 (`src/seogeo_reporter/pipeline.py`)
- 실행 예시 CLI (`src/seogeo_reporter/cli.py`)
- 단계별 구현 가이드 (`docs/mvp-roadmap.md`)

> 참고: 엑셀 템플릿 실제 쓰기(`openpyxl`/`ExcelJS`)는 런타임 의존성 확보 후 `ExcelWriter` 구현체를 연결하면 됩니다.

## 빠른 실행

```bash
python -m src.seogeo_reporter.cli --month 2026-03
```

샘플 데이터 기반으로 파이프라인이 실행되며, 최종 페이로드(JSON)가 출력됩니다.

## 다음 작업 우선순위

1. Google OAuth 및 토큰 저장소 구현
2. GA4/GSC 실데이터 커넥터 구현
3. Prompt API 커넥터(OpenAI/Gemini/Perplexity) 구현
4. Browser 추적기(Playwright) 구현
5. `SEOGEO_리포트양식.xlsx` 셀 매핑 기반 Writer 구현
