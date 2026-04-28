import tempfile
import unittest

from src.seogeo_reporter.auth import FileTokenStore
from src.seogeo_reporter.connectors import _parse_ga4_channel_rows
from src.seogeo_reporter.date_utils import month_range, previous_month


class ConnectorAuthTests(unittest.TestCase):
    def test_previous_month_rollover(self) -> None:
        self.assertEqual(previous_month("2026-01"), "2025-12")
        self.assertEqual(previous_month("2026-11"), "2026-10")

    def test_month_range_uses_last_day(self) -> None:
        feb = month_range("2026-02")
        self.assertEqual(feb.start_date, "2026-02-01")
        self.assertEqual(feb.end_date, "2026-02-28")

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

    def test_parse_ga4_channel_rows(self) -> None:
        rows = [
            {
                "dimensionValues": [{"value": "Organic Search"}],
                "metricValues": [{"value": "10"}, {"value": "2"}],
            },
            {
                "dimensionValues": [{"value": "Referral"}],
                "metricValues": [{"value": "5"}, {"value": "1"}],
            },
        ]
        summary = _parse_ga4_channel_rows(rows)
        self.assertEqual(summary.organic_sessions, 10)
        self.assertEqual(summary.referral_sessions, 5)
        self.assertEqual(summary.conversions, 3)


if __name__ == "__main__":
    unittest.main()
