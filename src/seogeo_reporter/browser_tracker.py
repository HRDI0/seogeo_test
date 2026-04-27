from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .collectors import PromptTracker
from .models import PromptResult


@dataclass(slots=True)
class BrowserRunConfig:
    engine: str
    base_dir: str = "artifacts/browser"
    headless: bool = True


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
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=self.config.headless)
            context = browser.new_context(locale="ko-KR")
            page = context.new_page()

            for item in prompt_set:
                # Note: engine-specific login/navigation should be implemented in dedicated adapters.
                page.goto("about:blank")
                prompt_id = item["prompt_id"]
                html_path = base / f"{prompt_id}.html"
                screenshot_path = base / f"{prompt_id}.png"
                html_path.write_text(page.content(), encoding="utf-8")
                page.screenshot(path=str(screenshot_path), full_page=True)

                results.append(
                    PromptResult(
                        engine=self.config.engine,
                        capture_method="browser",
                        prompt_id=prompt_id,
                        prompt_type=item.get("prompt_type", "직접형"),
                        prompt_text=item["prompt_text"],
                        answer_text="",
                        citations=[],
                        visible_links=[],
                        screenshot_path=str(screenshot_path),
                        html_snapshot_path=str(html_path),
                    )
                )
            browser.close()

        return results
