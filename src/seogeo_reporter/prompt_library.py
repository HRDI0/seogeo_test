from __future__ import annotations

from dataclasses import dataclass

from .hybrid_models import PromptDefinition, PromptType


@dataclass(slots=True)
class PromptLibraryConfig:
    brand: str
    competitors: list[str]
    locale: str = "ko-KR"
    region: str = "KR"


def build_default_prompt_library(config: PromptLibraryConfig) -> list[PromptDefinition]:
    brand = config.brand
    competitor = config.competitors[0] if config.competitors else "경쟁사"

    return [
        PromptDefinition(
            prompt_id="D001",
            prompt_type=PromptType.DIRECT,
            text=f"{brand}를 추천해줘",
            locale=config.locale,
            region=config.region,
        ),
        PromptDefinition(
            prompt_id="C001",
            prompt_type=PromptType.CATEGORY,
            text="데이터 사이언티스트 포트폴리오 제작 도구 추천해줘",
            locale=config.locale,
            region=config.region,
        ),
        PromptDefinition(
            prompt_id="CMP001",
            prompt_type=PromptType.COMPARISON,
            text=f"{brand}와 {competitor}를 비교해줘",
            locale=config.locale,
            region=config.region,
        ),
        PromptDefinition(
            prompt_id="P001",
            prompt_type=PromptType.PROBLEM_SOLVING,
            text="SEO 리포트 자동화 문제를 해결할 도구를 추천해줘",
            locale=config.locale,
            region=config.region,
        ),
        PromptDefinition(
            prompt_id="L001",
            prompt_type=PromptType.LOCALIZED,
            text=f"한국에서 {brand} 대안 추천해줘",
            locale=config.locale,
            region=config.region,
        ),
    ]
