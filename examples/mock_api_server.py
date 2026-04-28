from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload: dict, code: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path

        if path.endswith(":runReport"):
            self._json(
                {
                    "rows": [
                        {
                            "dimensionValues": [{"value": "Organic Search"}],
                            "metricValues": [{"value": "10"}, {"value": "2"}],
                        },
                        {
                            "dimensionValues": [{"value": "Referral"}],
                            "metricValues": [{"value": "5"}, {"value": "1"}],
                        },
                    ]
                }
            )
            return

        if "/searchAnalytics/query" in path:
            self._json(
                {
                    "rows": [
                        {
                            "keys": ["seo 리포트 자동화"],
                            "clicks": 5,
                            "impressions": 100,
                            "ctr": 0.05,
                            "position": 9.1,
                        }
                    ]
                }
            )
            return

        if path == "/v1/responses":
            self._json(
                {
                    "output": [
                        {
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": "브랜드A를 추천합니다.",
                                    "annotations": [{"url": "https://brand-a.com"}],
                                }
                            ]
                        }
                    ]
                }
            )
            return

        if path.startswith("/v1beta/models/") and path.endswith(":generateContent"):
            self._json(
                {
                    "candidates": [
                        {
                            "content": {"parts": [{"text": "Gemini 추천 결과"}]},
                            "groundingMetadata": {
                                "groundingChunks": [{"web": {"uri": "https://brand-a.com/guide"}}]
                            },
                        }
                    ]
                }
            )
            return

        if path == "/chat/completions":
            self._json(
                {
                    "choices": [{"message": {"content": "Perplexity 추천 결과"}}],
                    "citations": ["https://brand-a.com/help"],
                }
            )
            return

        self._json({"error": f"unknown path: {path}"}, 404)


def main() -> None:
    server = HTTPServer(("127.0.0.1", 18080), Handler)
    print("mock_api_server listening on 127.0.0.1:18080")
    server.serve_forever()


if __name__ == "__main__":
    main()
