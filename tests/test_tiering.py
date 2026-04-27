import unittest

from src.seogeo_reporter.models import PromptResult, Tier
from src.seogeo_reporter.tiering import classify_tier, enrich_tier


class TieringTests(unittest.TestCase):
    def test_tier_1_when_brand_and_official_link(self) -> None:
        row = PromptResult(
            engine="gpt",
            capture_method="api",
            prompt_id="p1",
            prompt_type="직접형",
            prompt_text="x",
            answer_text="x",
            brand_mention_yn=True,
            official_link_yn=True,
        )
        self.assertEqual(classify_tier(row), Tier.TIER_1)

    def test_tier_2_when_brand_without_official_link(self) -> None:
        row = PromptResult(
            engine="gpt",
            capture_method="api",
            prompt_id="p2",
            prompt_type="직접형",
            prompt_text="x",
            answer_text="x",
            brand_mention_yn=True,
            official_link_yn=False,
        )
        self.assertEqual(classify_tier(row), Tier.TIER_2)

    def test_tier_4_when_no_signal(self) -> None:
        row = PromptResult(
            engine="gpt",
            capture_method="api",
            prompt_id="p3",
            prompt_type="직접형",
            prompt_text="x",
            answer_text="x",
            brand_mention_yn=False,
            official_link_yn=False,
            mention_position=None,
        )
        enriched = enrich_tier(row)
        self.assertEqual(enriched.tier, Tier.TIER_4)
        self.assertEqual(enriched.tier_score, 0.0)


if __name__ == "__main__":
    unittest.main()
