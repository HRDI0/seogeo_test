from __future__ import annotations

from dataclasses import dataclass

from .browser_tracker import PlaywrightPromptTracker
from .collectors import PromptTracker
from .hybrid_models import CaptureArtifact, ParsedSignal, PromptDefinition
from .parsing import parse_capture
from .scoring import VisibilityMetrics, compute_visibility_metrics


@dataclass(slots=True)
class HybridConfig:
    brand_aliases: list[str]
    competitor_aliases: list[str]
    official_domains: list[str]
    browser_validation_sample_size: int = 10


class HybridVisibilityPipeline:
    """API-first + browser validation pipeline for AI visibility tracking."""

    def __init__(
        self,
        api_tracker: PromptTracker,
        browser_tracker: PlaywrightPromptTracker | None,
        config: HybridConfig,
    ) -> None:
        self.api_tracker = api_tracker
        self.browser_tracker = browser_tracker
        self.config = config

    def run(self, prompts: list[PromptDefinition]) -> tuple[list[ParsedSignal], VisibilityMetrics]:
        prompt_payload = [{"prompt_id": p.prompt_id, "prompt_type": p.prompt_type.value, "prompt_text": p.text} for p in prompts]

        api_results = self.api_tracker.run(prompt_payload)
        captures: list[CaptureArtifact] = [
            CaptureArtifact(
                engine=r.engine,
                mode=r.capture_method,
                prompt_id=r.prompt_id,
                raw_text=r.answer_text,
                citations=r.citations,
                source_panel_urls=r.visible_links,
                screenshot_path=r.screenshot_path,
                html=r.html_snapshot_path,
            )
            for r in api_results
        ]

        if self.browser_tracker:
            sample = prompt_payload[: self.config.browser_validation_sample_size]
            browser_results = self.browser_tracker.run(sample)
            captures.extend(
                CaptureArtifact(
                    engine=r.engine,
                    mode=r.capture_method,
                    prompt_id=r.prompt_id,
                    raw_text=r.answer_text,
                    citations=r.citations,
                    source_panel_urls=r.visible_links,
                    screenshot_path=r.screenshot_path,
                    html=r.html_snapshot_path,
                )
                for r in browser_results
            )

        signals = [
            parse_capture(
                artifact=c,
                brand_aliases=self.config.brand_aliases,
                competitor_aliases=self.config.competitor_aliases,
                official_domains=self.config.official_domains,
            )
            for c in captures
        ]

        metrics = compute_visibility_metrics(signals)
        return signals, metrics
