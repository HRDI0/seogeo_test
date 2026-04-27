import tempfile
import unittest

from src.seogeo_reporter.auth import SecureTokenStore
from src.seogeo_reporter.security import TokenCipher, TokenCryptoConfig, generate_key_b64


class SecurityTests(unittest.TestCase):
    def _cipher(self) -> TokenCipher:
        return TokenCipher(
            TokenCryptoConfig(
                encryption_key_b64=generate_key_b64(),
                mac_key_b64=generate_key_b64(),
            )
        )

    def test_token_cipher_roundtrip(self) -> None:
        cipher = self._cipher()
        payload = {"access_token": "abc", "refresh_token": "def"}
        encrypted = cipher.encrypt_dict(payload)
        restored = cipher.decrypt_dict(encrypted)
        self.assertEqual(restored["access_token"], "abc")
        self.assertEqual(restored["refresh_token"], "def")

    def test_token_cipher_tamper_detection(self) -> None:
        cipher = self._cipher()
        encrypted = cipher.encrypt_dict({"access_token": "x"})
        tampered = encrypted[:-4] + "AAAA"
        with self.assertRaises(Exception):
            cipher.decrypt_dict(tampered)

    def test_secure_token_store_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SecureTokenStore(cipher=self._cipher(), base_dir=tmp)
            store.save("client/site", {"access_token": "aaa", "refresh_token": "bbb"})
            loaded = store.load("client/site")
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded["access_token"], "aaa")
            self.assertEqual(loaded["refresh_token"], "bbb")


if __name__ == "__main__":
    unittest.main()
