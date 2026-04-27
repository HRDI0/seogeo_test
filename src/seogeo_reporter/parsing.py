from __future__ import annotations

import re
from urllib.parse import urlparse

from .hybrid_models import CaptureArtifact, ParsedSignal, VisibilityTier


def parse_capture(
    artifact: CaptureArtifact,
    brand_aliases: list[str],
    competitor_aliases: list[str],
    official_domains: list[str],
) -> ParsedSignal:
    text = artifact.raw_text.lower()
    brand_mentioned = any(alias.lower() in text for alias in brand_aliases)

    competitor_mentions = 0
    for alias in competitor_aliases:
        competitor_mentions += len(re.findall(re.escape(alias.lower()), text))

    citation_urls = list(dict.fromkeys(artifact.citations + artifact.source_panel_urls))
    official, third_party = _split_citations(citation_urls, official_domains)

    sentiment = _detect_sentiment(text)
    position_hint = _detect_position_hint(text)

    tier = infer_visibility_tier(
        brand_mentioned=brand_mentioned,
        official_citations=official,
        third_party_citations=third_party,
        sentiment=sentiment,
        position_hint=position_hint,
    )

    return ParsedSignal(
        prompt_id=artifact.prompt_id,
        engine=artifact.engine,
        brand_mentioned=brand_mentioned,
        competitor_mentions=competitor_mentions,
        official_citation_urls=official,
        third_party_citation_urls=third_party,
        sentiment=sentiment,
        position_hint=position_hint,
        detected_modules=artifact.detected_modules,
        tier=tier,
    )


def infer_visibility_tier(
    brand_mentioned: bool,
    official_citations: list[str],
    third_party_citations: list[str],
    sentiment: str,
    position_hint: str | None,
) -> VisibilityTier:
    if not brand_mentioned:
        return VisibilityTier.TIER_0
    if not official_citations and not third_party_citations:
        return VisibilityTier.TIER_1
    if official_citations and sentiment == "positive" and position_hint == "top":
        return VisibilityTier.TIER_4
    if official_citations:
        return VisibilityTier.TIER_3
    return VisibilityTier.TIER_2


def _split_citations(urls: list[str], official_domains: list[str]) -> tuple[list[str], list[str]]:
    official_set = {d.lower() for d in official_domains}
    official: list[str] = []
    third_party: list[str] = []

    for url in urls:
        host = (urlparse(url).netloc or "").lower()
        if any(host == d or host.endswith(f".{d}") for d in official_set):
            official.append(url)
        else:
            third_party.append(url)

    return official, third_party


def _detect_sentiment(text: str) -> str:
    positive_words = ["추천", "최고", "좋", "권장"]
    negative_words = ["나쁘", "비추천", "문제", "오류"]

    if any(word in text for word in negative_words):
        return "negative"
    if any(word in text for word in positive_words):
        return "positive"
    return "neutral"


def _detect_position_hint(text: str) -> str | None:
    if any(token in text for token in ["1.", "첫", "top"]):
        return "top"
    return None
