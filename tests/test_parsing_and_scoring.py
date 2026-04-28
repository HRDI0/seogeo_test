import unittest

from src.seogeo_reporter.hybrid_models import CaptureArtifact, VisibilityTier
from src.seogeo_reporter.parsing import parse_capture
from src.seogeo_reporter.scoring import compute_visibility_metrics


class ParsingScoringTests(unittest.TestCase):
    def test_parse_capture_tier3_with_official_citation(self) -> None:
        artifact = CaptureArtifact(
            engine="gpt",
            mode="api",
            prompt_id="p1",
            raw_text="브랜드A를 추천합니다.",
            citations=["https://brand-a.com/page", "https://review-site.com/post"],
        )
        signal = parse_capture(
            artifact,
            brand_aliases=["브랜드a"],
            competitor_aliases=["브랜드b"],
            official_domains=["brand-a.com"],
        )
        self.assertEqual(signal.tier, VisibilityTier.TIER_3)
        self.assertTrue(signal.brand_mentioned)
        self.assertEqual(len(signal.official_citation_urls), 1)

    def test_metrics_calculation(self) -> None:
        signals = [
            parse_capture(
                CaptureArtifact(
                    engine="gpt",
                    mode="api",
                    prompt_id="1",
                    raw_text="브랜드A 추천",
                    citations=["https://brand-a.com"],
                ),
                ["브랜드a"],
                ["경쟁사"],
                ["brand-a.com"],
            ),
            parse_capture(
                CaptureArtifact(
                    engine="gpt",
                    mode="api",
                    prompt_id="2",
                    raw_text="경쟁사 추천",
                    citations=["https://review.com"],
                ),
                ["브랜드a"],
                ["경쟁사"],
                ["brand-a.com"],
            ),
        ]
        metrics = compute_visibility_metrics(signals)
        self.assertAlmostEqual(metrics.mention_rate, 0.5)
        self.assertAlmostEqual(metrics.citation_rate, 1.0)
        self.assertAlmostEqual(metrics.official_link_rate, 0.5)


if __name__ == "__main__":
    unittest.main()
