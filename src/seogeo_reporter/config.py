from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class AppConfig:
    run_mode: str = "mock"
    prompt_mode: str = "mock"
    report_month: str | None = None
    client_name: str = "Demo Client"
    site_url: str = "https://example.com"
    ga4_property_id: str = ""
    google_access_token: str = ""
    report_output_path: str = ""

    def validate(self) -> None:
        if self.run_mode not in {"mock", "real"}:
            raise ValueError(f"Invalid RUN_MODE: {self.run_mode}")
        if self.prompt_mode not in {"mock", "openai", "gemini", "perplexity", "browser"}:
            raise ValueError(f"Invalid PROMPT_MODE: {self.prompt_mode}")



def app_config_from_env() -> AppConfig:
    cfg = AppConfig(
        run_mode=os.getenv("RUN_MODE", "mock"),
        prompt_mode=os.getenv("PROMPT_MODE", "mock"),
        report_month=os.getenv("REPORT_MONTH") or None,
        client_name=os.getenv("CLIENT_NAME", "Demo Client"),
        site_url=os.getenv("SITE_URL", "https://example.com"),
        ga4_property_id=os.getenv("GA4_PROPERTY_ID", ""),
        google_access_token=os.getenv("GOOGLE_ACCESS_TOKEN", ""),
        report_output_path=os.getenv("REPORT_OUTPUT_PATH", ""),
    )
    cfg.validate()
    return cfg
