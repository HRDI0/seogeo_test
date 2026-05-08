import unittest

from src.seogeo_reporter.browser_tracker import build_engine_url, extract_links_from_html, extract_text_from_html


class BrowserTrackerUtilsTests(unittest.TestCase):
    def test_build_engine_url(self) -> None:
        url = build_engine_url("perplexity", "브랜드A 공식몰 링크")
        self.assertIn("perplexity.ai", url)
        self.assertIn("%EA%B3%B5%EC%8B%9D%EB%AA%B0", url)

    def test_extract_links_from_html_deduplicates(self) -> None:
        html = '<a href="https://example.com/a">a</a><a href="https://example.com/a/">a2</a><a href="https://x.com?q=1">x</a>'
        links = extract_links_from_html(html)
        self.assertEqual(2, len(links))
        self.assertIn("https://example.com/a", links)

    def test_extract_text_from_html(self) -> None:
        html = "<html><head><style>.a{}</style></head><body><h1>브랜드A</h1><script>1</script><p>공식몰 안내</p></body></html>"
        text = extract_text_from_html(html)
        self.assertEqual("브랜드A 공식몰 안내", text)


if __name__ == "__main__":
    unittest.main()
