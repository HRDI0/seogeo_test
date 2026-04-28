from __future__ import annotations

from .models import PromptResult, Tier


def classify_tier(result: PromptResult) -> Tier:
    """Rule-based tier classification for prompt visibility outcomes."""
    if result.brand_mention_yn and result.official_link_yn:
        return Tier.TIER_1

    if result.brand_mention_yn:
        return Tier.TIER_2

    has_indirect_signal = bool(result.mention_position) or result.competitor_mention_count > 0 or bool(result.cited_page_type)
    if has_indirect_signal:
        return Tier.TIER_3

    return Tier.TIER_4


def score_tier(tier: Tier) -> float:
    score_map = {
        Tier.TIER_1: 100.0,
        Tier.TIER_2: 75.0,
        Tier.TIER_3: 40.0,
        Tier.TIER_4: 0.0,
    }
    return score_map[tier]


def enrich_tier(result: PromptResult) -> PromptResult:
    tier = classify_tier(result)
    result.tier = tier
    result.tier_score = score_tier(tier)
    return result
