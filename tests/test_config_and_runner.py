import unittest

from src.seogeo_reporter.config import AppConfig
from src.seogeo_reporter.parsing import _count_alias_occurrences


class ConfigAndParsingRefactorTests(unittest.TestCase):
    def test_app_config_validation(self) -> None:
        cfg = AppConfig(run_mode="mock", prompt_mode="mock")
        cfg.validate()

        bad = AppConfig(run_mode="invalid", prompt_mode="mock")
        with self.assertRaises(ValueError):
            bad.validate()

    def test_alias_word_boundary_for_ascii(self) -> None:
        text = "brand is good, rebrand is different"
        self.assertEqual(_count_alias_occurrences(text, "brand"), 1)

    def test_alias_contains_for_korean(self) -> None:
        text = "브랜드a 추천, 브랜드a 비교"
        self.assertEqual(_count_alias_occurrences(text, "브랜드a"), 2)


if __name__ == "__main__":
    unittest.main()
