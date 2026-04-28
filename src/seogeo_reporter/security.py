from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import subprocess
from dataclasses import dataclass
from typing import Any


class SecurityError(RuntimeError):
    pass


@dataclass(slots=True)
class TokenCryptoConfig:
    encryption_key_b64: str
    mac_key_b64: str

    def encryption_key(self) -> bytes:
        key = base64.urlsafe_b64decode(self.encryption_key_b64.encode("utf-8"))
        if len(key) != 32:
            raise SecurityError("TOKEN_ENC_KEY must decode to 32 bytes")
        return key

    def mac_key(self) -> bytes:
        key = base64.urlsafe_b64decode(self.mac_key_b64.encode("utf-8"))
        if len(key) != 32:
            raise SecurityError("TOKEN_MAC_KEY must decode to 32 bytes")
        return key


class TokenCipher:
    """Encrypt-then-MAC token payloads using AES-256-CBC + HMAC-SHA256.

    Requires openssl binary in runtime.
    """

    version = "v1"

    def __init__(self, config: TokenCryptoConfig) -> None:
        self.enc_key = config.encryption_key()
        self.mac_key = config.mac_key()

    def encrypt_dict(self, payload: dict[str, Any]) -> str:
        plaintext = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        iv = secrets.token_bytes(16)
        ciphertext = _openssl_encrypt(plaintext=plaintext, key=self.enc_key, iv=iv)
        mac = hmac.new(self.mac_key, self._mac_input(iv, ciphertext), hashlib.sha256).digest()
        envelope = {
            "v": self.version,
            "iv": base64.urlsafe_b64encode(iv).decode("utf-8"),
            "ct": base64.urlsafe_b64encode(ciphertext).decode("utf-8"),
            "mac": base64.urlsafe_b64encode(mac).decode("utf-8"),
        }
        return base64.urlsafe_b64encode(json.dumps(envelope).encode("utf-8")).decode("utf-8")

    def decrypt_dict(self, token: str) -> dict[str, Any]:
        try:
            envelope = json.loads(base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8"))
            if envelope.get("v") != self.version:
                raise SecurityError("Unsupported token envelope version")
            iv = base64.urlsafe_b64decode(envelope["iv"].encode("utf-8"))
            ciphertext = base64.urlsafe_b64decode(envelope["ct"].encode("utf-8"))
            expected_mac = base64.urlsafe_b64decode(envelope["mac"].encode("utf-8"))
        except Exception as exc:
            raise SecurityError(f"Invalid encrypted token envelope: {exc}") from exc

        actual_mac = hmac.new(self.mac_key, self._mac_input(iv, ciphertext), hashlib.sha256).digest()
        if not hmac.compare_digest(actual_mac, expected_mac):
            raise SecurityError("Encrypted token MAC validation failed")

        plaintext = _openssl_decrypt(ciphertext=ciphertext, key=self.enc_key, iv=iv)
        return json.loads(plaintext.decode("utf-8"))

    @classmethod
    def _mac_input(cls, iv: bytes, ciphertext: bytes) -> bytes:
        return cls.version.encode("utf-8") + b"|" + iv + b"|" + ciphertext



def token_cipher_from_env() -> TokenCipher:
    enc_key = os.getenv("TOKEN_ENC_KEY", "")
    mac_key = os.getenv("TOKEN_MAC_KEY", "")
    if not enc_key or not mac_key:
        raise SecurityError("TOKEN_ENC_KEY and TOKEN_MAC_KEY are required for encrypted token storage")
    return TokenCipher(TokenCryptoConfig(encryption_key_b64=enc_key, mac_key_b64=mac_key))


def generate_key_b64() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8")


def _openssl_encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    cmd = [
        "openssl",
        "enc",
        "-aes-256-cbc",
        "-K",
        key.hex(),
        "-iv",
        iv.hex(),
    ]
    proc = subprocess.run(cmd, input=plaintext, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise SecurityError(f"OpenSSL encryption failed: {proc.stderr.decode('utf-8', errors='ignore').strip()}")
    return proc.stdout


def _openssl_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    cmd = [
        "openssl",
        "enc",
        "-d",
        "-aes-256-cbc",
        "-K",
        key.hex(),
        "-iv",
        iv.hex(),
    ]
    proc = subprocess.run(cmd, input=ciphertext, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise SecurityError(f"OpenSSL decryption failed: {proc.stderr.decode('utf-8', errors='ignore').strip()}")
    return proc.stdout
