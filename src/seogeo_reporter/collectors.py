from __future__ import annotations

from .models import PromptResult


class PromptTracker:
    def run(self, prompt_set: list[dict[str, str]]) -> list[PromptResult]:
        raise NotImplementedError


class MockPromptTracker(PromptTracker):
    def run(self, prompt_set: list[dict[str, str]]) -> list[PromptResult]:
        rows: list[PromptResult] = []
        for item in prompt_set:
            rows.append(
                PromptResult(
                    engine=item.get("engine", "gpt"),
                    capture_method=item.get("capture_method", "api"),
                    prompt_id=item["prompt_id"],
                    prompt_type=item.get("prompt_type", "직접형"),
                    prompt_text=item["prompt_text"],
                    answer_text="브랜드 A는 공식 사이트에서 확인할 수 있습니다.",
                    citations=["https://example.com/blog/geo"],
                    visible_links=["https://example.com"],
                    brand_mention_yn=True,
                    official_link_yn=True,
                    mention_position="top",
                    competitor_mention_count=1,
                    cited_page_type="home",
                )
            )
        return rows
