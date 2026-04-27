from __future__ import annotations

import json
import os
import secrets
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


GOOGLE_AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


@dataclass(slots=True)
class OAuthClientConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list[str]


class OAuthError(RuntimeError):
    pass


class FileTokenStore:
    """Simple JSON token store per tenant/site key."""

    def __init__(self, base_dir: str = ".secrets/tokens") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = key.replace("/", "_").replace(":", "_")
        return self.base_dir / f"{safe}.json"

    def save(self, key: str, token_payload: dict[str, Any]) -> None:
        path = self._path(key)
        payload = dict(token_payload)
        payload["saved_at"] = int(time.time())
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, key: str) -> dict[str, Any] | None:
        path = self._path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))


class GoogleOAuthService:
    def __init__(self, config: OAuthClientConfig) -> None:
        self.config = config

    def build_auth_url(self, state: str | None = None, access_type: str = "offline") -> tuple[str, str]:
        csrf_state = state or secrets.token_urlsafe(24)
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.config.scopes),
            "state": csrf_state,
            "access_type": access_type,
            "prompt": "consent",
        }
        return f"{GOOGLE_AUTH_BASE}?{urllib.parse.urlencode(params)}", csrf_state

    def exchange_code(self, code: str) -> dict[str, Any]:
        payload = {
            "code": code,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": self.config.redirect_uri,
            "grant_type": "authorization_code",
        }
        return self._post_form(GOOGLE_TOKEN_URL, payload)

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        payload = {
            "refresh_token": refresh_token,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "refresh_token",
        }
        return self._post_form(GOOGLE_TOKEN_URL, payload)

    @staticmethod
    def _post_form(url: str, payload: dict[str, str]) -> dict[str, Any]:
        data = urllib.parse.urlencode(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, method="POST")
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # network/HTTP context propagated
            raise OAuthError(f"OAuth token request failed: {exc}") from exc


def oauth_config_from_env() -> OAuthClientConfig:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/oauth/callback")
    scopes = [
        "https://www.googleapis.com/auth/analytics.readonly",
        "https://www.googleapis.com/auth/webmasters.readonly",
    ]
    return OAuthClientConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scopes,
    )
