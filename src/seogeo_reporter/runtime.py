from __future__ import annotations

import datetime as dt
import os

from .auth import FileTokenStore, SecureTokenStore
from .date_utils import previous_month
from .security import token_cipher_from_env


def default_report_month(today: dt.date | None = None) -> str:
    base = today or dt.date.today()
    current = f"{base.year:04d}-{base.month:02d}"
    return previous_month(current)


def build_token_store_from_env(base_dir: str = ".secrets/tokens") -> FileTokenStore:
    mode = os.getenv("TOKEN_STORE_MODE", "plain").lower()
    if mode == "encrypted":
        return SecureTokenStore(cipher=token_cipher_from_env(), base_dir=base_dir)
    if mode == "plain":
        return FileTokenStore(base_dir=base_dir)
    raise ValueError(f"Unsupported TOKEN_STORE_MODE: {mode}")
