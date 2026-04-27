from __future__ import annotations

from .models import PromptResult, Tier


def classify_tier(result: PromptResult) -> Tier:
    """Rule-based Tier classification aligned with report template semantics."""
    if result.brand_mention_yn and result.official_link_yn:
        return Tier.TIER_1
    if result.brand_mention_yn and not result.official_link_yn:
        return Tier.TIER_2
    if not result.brand_mention_yn and result.competitor_mention_count >= 0:
        # Indirect mention or weak relevance is treated as Tier 3.
        if result.mention_position:
            return Tier.TIER_3
    return Tier.TIER_4


def score_tier(tier: Tier) -> float:
    return {
        Tier.TIER_1: 100.0,
        Tier.TIER_2: 75.0,
        Tier.TIER_3: 40.0,
        Tier.TIER_4: 0.0,
    }[tier]


def enrich_tier(result: PromptResult) -> PromptResult:
    tier = classify_tier(result)
    result.tier = tier
    result.tier_score = score_tier(tier)
    return result
