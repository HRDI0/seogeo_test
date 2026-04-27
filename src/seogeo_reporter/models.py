from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Tier(str, Enum):
    TIER_1 = "Tier 1"
    TIER_2 = "Tier 2"
    TIER_3 = "Tier 3"
    TIER_4 = "Tier 4"


@dataclass(slots=True)
class PromptResult:
    engine: str
    capture_method: str  # api | browser
    prompt_id: str
    prompt_type: str
    prompt_text: str
    answer_text: str
    citations: list[str] = field(default_factory=list)
    visible_links: list[str] = field(default_factory=list)
    screenshot_path: str | None = None
    html_snapshot_path: str | None = None
    brand_mention_yn: bool = False
    official_link_yn: bool = False
    mention_position: str | None = None
    competitor_mention_count: int = 0
    cited_page_type: str | None = None
    tier: Tier | None = None
    tier_score: float | None = None
    notes: str | None = None


@dataclass(slots=True)
class KeywordMonthlyMetric:
    keyword: str
    previous_impressions: int
    current_impressions: int
    previous_clicks: int
    current_clicks: int
    previous_ctr: float
    current_ctr: float
    previous_position: float
    current_position: float


@dataclass(slots=True)
class MonthlyReportInput:
    client_name: str
    site_url: str
    month: str
    ga4_summary: dict[str, Any]
    gsc_keywords: list[KeywordMonthlyMetric]
    prompt_results: list[PromptResult]


@dataclass(slots=True)
class MonthlyReportPayload:
    overview: dict[str, Any]
    prompt_rows: list[dict[str, Any]]
    keyword_rows: list[dict[str, Any]]
    summary_rows: list[dict[str, Any]]
