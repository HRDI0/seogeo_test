# 배포 준비 가이드 (Vercel + Render + Cloudflare R2)

## 1) 권장 배치

- Frontend: Vercel
- Backend API/Worker/Cron: Render
- Storage: Cloudflare R2

## 2) 토큰 보안 분리 원칙

1. 프론트엔드(Vercel)는 Google OAuth 클라이언트 secret/refresh token을 절대 보관하지 않는다.
2. OAuth 교환/갱신은 Render 백엔드에서만 수행한다.
3. 저장 시 반드시 암호화된 저장소(`SecureTokenStore`)를 사용한다.
4. 암호화 키 2종은 분리한다.
   - `TOKEN_ENC_KEY`: AES 암호화 키
   - `TOKEN_MAC_KEY`: 무결성(HMAC) 키
5. 암호화 키는 Render 환경변수 Secret으로만 주입하고, 코드/레포지토리에 저장하지 않는다.

## 3) 키 생성

```bash
python -c "from src.seogeo_reporter.security import generate_key_b64; print(generate_key_b64())"
python -c "from src.seogeo_reporter.security import generate_key_b64; print(generate_key_b64())"
```

위 2개 값을 각각 `TOKEN_ENC_KEY`, `TOKEN_MAC_KEY`에 저장.

## 4) 환경변수 파일

- Vercel: `deploy/vercel.env.example`
- Render: `deploy/render.env.example`
- Infra blueprint: `deploy/render.yaml`

## 5) R2 운영 체크리스트

- 버킷 기본 private
- 업로드는 presigned URL
- 다운로드는 signed URL 또는 백엔드 프록시
- 수명 주기 정책(스크린샷/HTML snapshot 보존 기간) 적용
- 객체 키 규칙: `client_id/yyyy-mm/run_id/...`

## 6) 운영 체크리스트

- API, worker, cron을 서로 다른 서비스로 분리 배포
- worker/cron만 prompt/browser 작업 권한 부여
- 프론트엔드에는 백엔드 base URL만 노출
- 감사 로그: 토큰 접근/복호화 이벤트 기록
- 키 로테이션 절차 문서화(신규 키로 재암호화 배치)
