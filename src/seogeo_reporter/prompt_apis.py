from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Any

from .collectors import PromptTracker
from .models import PromptResult


class PromptApiError(RuntimeError):
    pass


@dataclass(slots=True)
class ApiEngineConfig:
    model: str
    api_key: str

    def validate(self) -> None:
        if not self.model:
            raise ValueError("model is required")
        if not self.api_key:
            raise ValueError("api_key is required")


class BaseApiPromptTracker(PromptTracker):
    engine_name = "api"

    def __init__(self, config: ApiEngineConfig) -> None:
        config.validate()
        self.config = config

    def run(self, prompt_set: list[dict[str, str]]) -> list[PromptResult]:
        output: list[PromptResult] = []
        for item in prompt_set:
            prompt = item["prompt_text"]
            response = self._ask(prompt)
            output.append(
                PromptResult(
                    engine=self.engine_name,
                    capture_method="api",
                    prompt_id=item["prompt_id"],
                    prompt_type=item.get("prompt_type", "직접형"),
                    prompt_text=prompt,
                    answer_text=response.get("answer_text", ""),
                    citations=response.get("citations", []),
                    visible_links=response.get("visible_links", response.get("citations", [])),
                    brand_mention_yn=response.get("brand_mention_yn", False),
                    official_link_yn=response.get("official_link_yn", False),
                    mention_position=response.get("mention_position"),
                    competitor_mention_count=response.get("competitor_mention_count", 0),
                    cited_page_type=response.get("cited_page_type"),
                )
            )
        return output

    def _ask(self, prompt: str) -> dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    def _post_json(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
        req = urllib.request.Request(
            url=url,
            method="POST",
            data=json.dumps(payload).encode("utf-8"),
        )
        for k, v in headers.items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise PromptApiError(f"Prompt API request failed ({url}): {exc}") from exc


class OpenAIPromptTracker(BaseApiPromptTracker):
    engine_name = "gpt"

    def __init__(self, config: ApiEngineConfig, endpoint: str = "https://api.openai.com/v1/responses") -> None:
        super().__init__(config)
        self.endpoint = endpoint

    def _ask(self, prompt: str) -> dict[str, Any]:
        payload = {
            "model": self.config.model,
            "input": prompt,
            "tools": [{"type": "web_search"}],
        }
        data = self._post_json(
            url=self.endpoint,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            payload=payload,
        )
        text_parts: list[str] = []
        citations: list[str] = []

        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") != "output_text":
                    continue
                text_parts.append(content.get("text", ""))
                for annotation in content.get("annotations", []):
                    url = annotation.get("url")
                    if url:
                        citations.append(url)

        return {
            "answer_text": "\n".join(filter(None, text_parts)),
            "citations": sorted(set(citations)),
        }


class GeminiPromptTracker(BaseApiPromptTracker):
    engine_name = "gemini"

    def __init__(self, config: ApiEngineConfig, endpoint_base: str = "https://generativelanguage.googleapis.com") -> None:
        super().__init__(config)
        self.endpoint_base = endpoint_base.rstrip("/")

    def _ask(self, prompt: str) -> dict[str, Any]:
        url = f"{self.endpoint_base}/v1beta/models/{self.config.model}:generateContent?key={self.config.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "tools": [{"googleSearch": {}}],
        }
        data = self._post_json(url, {"Content-Type": "application/json"}, payload)
        candidates = data.get("candidates", [])
        text_parts: list[str] = []
        citations: list[str] = []
        if candidates:
            parts = (candidates[0].get("content") or {}).get("parts", [])
            for part in parts:
                if "text" in part:
                    text_parts.append(part["text"])
            grounding = candidates[0].get("groundingMetadata", {}).get("groundingChunks", [])
            for chunk in grounding:
                uri = (chunk.get("web") or {}).get("uri")
                if uri:
                    citations.append(uri)
        return {
            "answer_text": "\n".join(text_parts),
            "citations": sorted(set(citations)),
        }


class PerplexityPromptTracker(BaseApiPromptTracker):
    engine_name = "perplexity"

    def __init__(self, config: ApiEngineConfig, endpoint: str = "https://api.perplexity.ai/chat/completions") -> None:
        super().__init__(config)
        self.endpoint = endpoint

    def _ask(self, prompt: str) -> dict[str, Any]:
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "return_citations": True,
        }
        data = self._post_json(
            self.endpoint,
            {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            payload,
        )
        answer = ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "")
        citations = data.get("citations", [])
        return {
            "answer_text": answer,
            "citations": citations,
        }
