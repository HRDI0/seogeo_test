import tempfile
import unittest

from src.seogeo_reporter.auth import FileTokenStore
from src.seogeo_reporter.connectors import _previous_month


class ConnectorAuthTests(unittest.TestCase):
    def test_previous_month_rollover(self) -> None:
        self.assertEqual(_previous_month("2026-01"), "2025-12")
        self.assertEqual(_previous_month("2026-11"), "2026-10")

    def test_file_token_store_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = FileTokenStore(base_dir=tmp)
            store.save("client/site", {"access_token": "abc", "refresh_token": "ref"})
            loaded = store.load("client/site")
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded["access_token"], "abc")
            self.assertEqual(loaded["refresh_token"], "ref")
            self.assertIn("saved_at", loaded)


if __name__ == "__main__":
    unittest.main()
