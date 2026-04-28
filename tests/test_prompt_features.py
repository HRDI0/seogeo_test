import unittest
from unittest.mock import patch

from src.seogeo_reporter.browser_tracker import BrowserRunConfig, PlaywrightPromptTracker
from src.seogeo_reporter.prompt_apis import (
    ApiEngineConfig,
    GeminiPromptTracker,
    OpenAIPromptTracker,
    PerplexityPromptTracker,
)


class PromptApiTrackerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.prompt_set = [
            {
                "prompt_id": "P001",
                "prompt_type": "직접형",
                "prompt_text": "브랜드 공식 링크를 알려줘",
            }
        ]

    def test_openai_tracker_parses_text_and_citations(self) -> None:
        tracker = OpenAIPromptTracker(ApiEngineConfig(model="gpt-4.1", api_key="test-key"))
        fake_response = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": "브랜드 공식 사이트는 example.com 입니다.",
                            "annotations": [{"url": "https://example.com"}],
                        }
                    ]
                }
            ]
        }
        with patch.object(OpenAIPromptTracker, "_post_json", return_value=fake_response):
            rows = tracker.run(self.prompt_set)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].engine, "gpt")
        self.assertIn("example.com", rows[0].answer_text)
        self.assertEqual(rows[0].citations, ["https://example.com"])

    def test_gemini_tracker_parses_grounding(self) -> None:
        tracker = GeminiPromptTracker(ApiEngineConfig(model="gemini-2.5-pro", api_key="test-key"))
        fake_response = {
            "candidates": [
                {
                    "content": {"parts": [{"text": "추천 결과입니다."}]},
                    "groundingMetadata": {
                        "groundingChunks": [{"web": {"uri": "https://example.com/guide"}}]
                    },
                }
            ]
        }
        with patch.object(GeminiPromptTracker, "_post_json", return_value=fake_response):
            rows = tracker.run(self.prompt_set)

        self.assertEqual(rows[0].engine, "gemini")
        self.assertIn("추천 결과", rows[0].answer_text)
        self.assertEqual(rows[0].citations, ["https://example.com/guide"])

    def test_perplexity_tracker_parses_chat_payload(self) -> None:
        tracker = PerplexityPromptTracker(ApiEngineConfig(model="sonar", api_key="test-key"))
        fake_response = {
            "choices": [{"message": {"content": "Perplexity 답변"}}],
            "citations": ["https://example.com/news"],
        }
        with patch.object(PerplexityPromptTracker, "_post_json", return_value=fake_response):
            rows = tracker.run(self.prompt_set)

        self.assertEqual(rows[0].engine, "perplexity")
        self.assertEqual(rows[0].answer_text, "Perplexity 답변")
        self.assertEqual(rows[0].citations, ["https://example.com/news"])


class BrowserTrackerTests(unittest.TestCase):
    def test_browser_tracker_requires_playwright(self) -> None:
        tracker = PlaywrightPromptTracker(BrowserRunConfig(engine="browser"))
        with self.assertRaises(RuntimeError):
            tracker.run(
                [
                    {
                        "prompt_id": "P001",
                        "prompt_type": "직접형",
                        "prompt_text": "테스트",
                    }
                ]
            )


if __name__ == "__main__":
    unittest.main()
