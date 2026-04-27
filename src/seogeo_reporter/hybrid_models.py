from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PromptType(str, Enum):
    DIRECT = "direct"
    CATEGORY = "category"
    COMPARISON = "comparison"
    PROBLEM_SOLVING = "problem_solving"
    LOCALIZED = "localized"


class VisibilityTier(str, Enum):
    TIER_0 = "Tier 0"  # brand not mentioned
    TIER_1 = "Tier 1"  # brand mentioned
    TIER_2 = "Tier 2"  # brand + third-party citation
    TIER_3 = "Tier 3"  # brand + official citation
    TIER_4 = "Tier 4"  # top recommendation + official citation + positive context


@dataclass(slots=True)
class PromptDefinition:
    prompt_id: str
    prompt_type: PromptType
    text: str
    locale: str = "ko-KR"
    region: str = "KR"
    persona: str | None = None


@dataclass(slots=True)
class CaptureArtifact:
    engine: str
    mode: str  # api|serp|browser
    prompt_id: str
    raw_text: str
    citations: list[str] = field(default_factory=list)
    html: str | None = None
    screenshot_path: str | None = None
    source_panel_urls: list[str] = field(default_factory=list)
    detected_modules: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ParsedSignal:
    prompt_id: str
    engine: str
    brand_mentioned: bool
    competitor_mentions: int
    official_citation_urls: list[str]
    third_party_citation_urls: list[str]
    sentiment: str
    position_hint: str | None
    detected_modules: list[str]
    tier: VisibilityTier
