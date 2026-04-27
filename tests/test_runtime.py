import datetime as dt
import os
import unittest

from src.seogeo_reporter.auth import FileTokenStore, SecureTokenStore
from src.seogeo_reporter.runtime import build_token_store_from_env, default_report_month
from src.seogeo_reporter.security import generate_key_b64


class RuntimeTests(unittest.TestCase):
    def test_default_report_month_uses_previous_month(self) -> None:
        self.assertEqual(default_report_month(dt.date(2026, 1, 5)), "2025-12")
        self.assertEqual(default_report_month(dt.date(2026, 4, 27)), "2026-03")

    def test_build_plain_store(self) -> None:
        old = os.environ.get("TOKEN_STORE_MODE")
        os.environ["TOKEN_STORE_MODE"] = "plain"
        try:
            store = build_token_store_from_env(base_dir=".tmp_tokens_plain")
            self.assertIsInstance(store, FileTokenStore)
        finally:
            if old is None:
                os.environ.pop("TOKEN_STORE_MODE", None)
            else:
                os.environ["TOKEN_STORE_MODE"] = old

    def test_build_encrypted_store(self) -> None:
        old_mode = os.environ.get("TOKEN_STORE_MODE")
        old_enc = os.environ.get("TOKEN_ENC_KEY")
        old_mac = os.environ.get("TOKEN_MAC_KEY")
        os.environ["TOKEN_STORE_MODE"] = "encrypted"
        os.environ["TOKEN_ENC_KEY"] = generate_key_b64()
        os.environ["TOKEN_MAC_KEY"] = generate_key_b64()
        try:
            store = build_token_store_from_env(base_dir=".tmp_tokens_secure")
            self.assertIsInstance(store, SecureTokenStore)
        finally:
            if old_mode is None:
                os.environ.pop("TOKEN_STORE_MODE", None)
            else:
                os.environ["TOKEN_STORE_MODE"] = old_mode
            if old_enc is None:
                os.environ.pop("TOKEN_ENC_KEY", None)
            else:
                os.environ["TOKEN_ENC_KEY"] = old_enc
            if old_mac is None:
                os.environ.pop("TOKEN_MAC_KEY", None)
            else:
                os.environ["TOKEN_MAC_KEY"] = old_mac


if __name__ == "__main__":
    unittest.main()
