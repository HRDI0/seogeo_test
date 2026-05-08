from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import re

from .collectors import PromptTracker
from .models import PromptResult


@dataclass(slots=True)
class BrowserRunConfig:
    engine: str
    base_dir: str = "artifacts/browser"
    headless: bool = True
    locale: str = "ko-KR"
    navigation_timeout_ms: int = 45000
    slow_mo_ms: int = 150


@dataclass(frozen=True, slots=True)
class EngineRoute:
    query_url_template: str


ENGINE_ROUTES: dict[str, EngineRoute] = {
    "gpt": EngineRoute("https://chatgpt.com/?q={query}"),
    "gemini": EngineRoute("https://gemini.google.com/app"),
    "perplexity": EngineRoute("https://www.perplexity.ai/search/new?q={query}"),
    "google_ai_mode": EngineRoute("https://www.google.com/search?q={query}&udm=50"),
    "google_ai_overview": EngineRoute("https://www.google.com/search?q={query}"),
}


class PlaywrightPromptTracker(PromptTracker):
    """Browser-based tracker for visual evidence capture.

    Requires playwright to be installed in runtime environment.
    """

    def __init__(self, config: BrowserRunConfig) -> None:
        self.config = config

    def run(self, prompt_set: list[dict[str, str]]) -> list[PromptResult]:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Playwright is not installed. Install playwright to use browser mode.") from exc

        base = Path(self.config.base_dir)
        base.mkdir(parents=True, exist_ok=True)

        results: list[PromptResult] = []
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=self.config.headless, slow_mo=self.config.slow_mo_ms)
                context = browser.new_context(locale=self.config.locale)
                page = context.new_page()
                page.set_default_timeout(self.config.navigation_timeout_ms)

                for item in prompt_set:
                    target_url = build_engine_url(self.config.engine, item["prompt_text"])
                    page.goto(target_url, wait_until="domcontentloaded")
                    page.wait_for_timeout(800)
                    prompt_id = item["prompt_id"]
                    html_path = base / f"{prompt_id}.html"
                    screenshot_path = base / f"{prompt_id}.png"
                    html = page.content()
                    html_path.write_text(html, encoding="utf-8")
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    links = extract_links_from_html(html)

                    results.append(
                        PromptResult(
                            engine=self.config.engine,
                            capture_method="browser",
                            prompt_id=prompt_id,
                            prompt_type=item.get("prompt_type", "직접형"),
                            prompt_text=item["prompt_text"],
                            answer_text=extract_text_from_html(html),
                            citations=links,
                            visible_links=links,
                            screenshot_path=str(screenshot_path),
                            html_snapshot_path=str(html_path),
                        )
                    )
                browser.close()
        except Exception as exc:  # pragma: no cover - depends on runtime browser libs
            raise RuntimeError(f"Playwright browser execution failed: {exc}") from exc

        return results


def build_engine_url(engine: str, prompt_text: str) -> str:
    from urllib.parse import quote_plus

    route = ENGINE_ROUTES.get(engine)
    if route is None:
        return "about:blank"
    return route.query_url_template.format(query=quote_plus(prompt_text))


def extract_links_from_html(html: str) -> list[str]:
    urls = re.findall(r'href=["\'](https?://[^"\']+)["\']', html, flags=re.IGNORECASE)
    deduped: list[str] = []
    seen: set[str] = set()
    for url in urls:
        normalized = _normalize_url(url)
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(url)
    return deduped


def extract_text_from_html(html: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    query = parsed.query
    base = f"{parsed.scheme.lower()}://{host}{path}"
    return f"{base}?{query}" if query else base
