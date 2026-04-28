#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python examples/mock_api_server.py > /tmp/mock_api_server.log 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID >/dev/null 2>&1 || true' EXIT
sleep 1

python - <<'PY'
from src.seogeo_reporter.connectors import GoogleHttpClient, RealGA4Connector, RealGSCConnector
from src.seogeo_reporter.prompt_apis import ApiEngineConfig, OpenAIPromptTracker, GeminiPromptTracker, PerplexityPromptTracker

client = GoogleHttpClient(access_token="demo-token")
ga4 = RealGA4Connector(property_id="123456", client=client, ga4_endpoint_base="http://127.0.0.1:18080")
gsc = RealGSCConnector(client=client, gsc_endpoint_base="http://127.0.0.1:18080")

summary = ga4.fetch_monthly_summary(site_url="https://example.com", month="2026-03")
keywords = gsc.fetch_keyword_metrics(site_url="https://example.com", month="2026-03")
print("[PASS] GA4 summary", summary)
print("[PASS] GSC rows", len(keywords))

prompt_set = [{"prompt_id": "P001", "prompt_type": "직접형", "prompt_text": "브랜드A 추천해줘"}]

openai = OpenAIPromptTracker(ApiEngineConfig(model="gpt-4.1", api_key="demo"), endpoint="http://127.0.0.1:18080/v1/responses")
gemini = GeminiPromptTracker(ApiEngineConfig(model="gemini-2.5-pro", api_key="demo"), endpoint_base="http://127.0.0.1:18080")
perplexity = PerplexityPromptTracker(ApiEngineConfig(model="sonar", api_key="demo"), endpoint="http://127.0.0.1:18080/chat/completions")

print("[PASS] OpenAI rows", len(openai.run(prompt_set)))
print("[PASS] Gemini rows", len(gemini.run(prompt_set)))
print("[PASS] Perplexity rows", len(perplexity.run(prompt_set)))
PY

echo "All example API verification checks passed."
