from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


class SerpCollectorError(RuntimeError):
    pass


class SerpApiCollector:
    """Collects Google AI Overview blocks from SerpApi-like endpoint."""

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("SERP_API_KEY is required")
        self.api_key = api_key

    def collect_google_ai_overview(self, query: str, hl: str = "ko", gl: str = "kr") -> dict[str, Any]:
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "hl": hl,
            "gl": gl,
        }
        url = f"https://serpapi.com/search.json?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url=url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise SerpCollectorError(f"SERP collection failed: {exc}") from exc
