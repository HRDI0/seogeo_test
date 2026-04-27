from __future__ import annotations

from dataclasses import dataclass

from .hybrid_models import ParsedSignal


@dataclass(slots=True)
class VisibilityMetrics:
    mention_rate: float
    citation_rate: float
    official_link_rate: float
    avg_competitor_mentions: float


def compute_visibility_metrics(signals: list[ParsedSignal]) -> VisibilityMetrics:
    if not signals:
        return VisibilityMetrics(0.0, 0.0, 0.0, 0.0)

    total = len(signals)
    mention_count = sum(1 for s in signals if s.brand_mentioned)
    citation_count = sum(1 for s in signals if s.official_citation_urls or s.third_party_citation_urls)
    official_count = sum(1 for s in signals if s.official_citation_urls)
    competitor_sum = sum(s.competitor_mentions for s in signals)

    return VisibilityMetrics(
        mention_rate=mention_count / total,
        citation_rate=citation_count / total,
        official_link_rate=official_count / total,
        avg_competitor_mentions=competitor_sum / total,
    )
