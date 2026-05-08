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
    brand_counts = [_count_alias_occurrences(text, alias.lower()) for alias in brand_aliases]
    brand_mention_count = sum(brand_counts)
    brand_mentioned = brand_mention_count > 0

    competitor_mentions = 0
    for alias in competitor_aliases:
        competitor_mentions += _count_alias_occurrences(text, alias.lower())

    citation_urls = list(dict.fromkeys(artifact.citations + artifact.source_panel_urls))
    official, third_party = _split_citations(citation_urls, official_domains)

    sentiment = _detect_sentiment(text)
    position_hint = _detect_position_hint(text)
    brand_importance_score = _compute_brand_importance_score(
        raw_text=artifact.raw_text,
        brand_aliases=brand_aliases,
        brand_mention_count=brand_mention_count,
    )

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
        brand_mention_count=brand_mention_count,
        brand_importance_score=brand_importance_score,
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


def _count_alias_occurrences(text: str, alias: str) -> int:
    if not alias:
        return 0
    if re.fullmatch(r"[a-z0-9._-]+", alias):
        pattern = re.compile(rf"\b{re.escape(alias)}\b")
        return len(pattern.findall(text))
    return text.count(alias)


def _compute_brand_importance_score(raw_text: str, brand_aliases: list[str], brand_mention_count: int) -> float:
    if not raw_text.strip() or brand_mention_count <= 0:
        return 0.0
    text = raw_text.lower()
    earliest = 1.0
    for alias in brand_aliases:
        idx = text.find(alias.lower())
        if idx >= 0:
            earliest = min(earliest, idx / max(len(text), 1))
    position_score = 1.0 - earliest
    freq_score = min(1.0, brand_mention_count / 8.0)
    score = (position_score * 0.6) + (freq_score * 0.4)
    return round(score * 100, 2)
