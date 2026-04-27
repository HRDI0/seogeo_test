from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict

from .auth import GoogleOAuthService, oauth_config_from_env
from .browser_tracker import BrowserRunConfig, PlaywrightPromptTracker
from .collectors import MockPromptTracker
from .connectors import (
    GoogleHttpClient,
    MockGA4Connector,
    MockGSCConnector,
    RealGA4Connector,
    RealGSCConnector,
)
from .excel_writer import SeoGeoExcelWriter
from .pipeline import MonthlyReportPipeline
from .prompt_apis import ApiEngineConfig, GeminiPromptTracker, OpenAIPromptTracker, PerplexityPromptTracker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SEOGEO monthly report runner")
    parser.add_argument("--client", default="Demo Client")
    parser.add_argument("--site", default="https://example.com")
    parser.add_argument("--month", required=True, help="YYYY-MM")
    parser.add_argument("--mode", choices=["mock", "real"], default="mock")
    parser.add_argument("--prompt-mode", choices=["mock", "openai", "gemini", "perplexity", "browser"], default="mock")
    parser.add_argument("--property-id", default="")
    parser.add_argument("--access-token", default="")
    parser.add_argument("--excel-out", default="")
    parser.add_argument("--print-oauth-url", action="store_true")
    return parser.parse_args()


def build_prompt_tracker(prompt_mode: str):
    if prompt_mode == "mock":
        return MockPromptTracker()
    if prompt_mode == "browser":
        return PlaywrightPromptTracker(BrowserRunConfig(engine="browser"))

    if prompt_mode == "openai":
        return OpenAIPromptTracker(ApiEngineConfig(model="gpt-4.1", api_key=os.getenv("OPENAI_API_KEY", "")))
    if prompt_mode == "gemini":
        return GeminiPromptTracker(ApiEngineConfig(model="gemini-2.5-pro", api_key=os.getenv("GEMINI_API_KEY", "")))
    return PerplexityPromptTracker(ApiEngineConfig(model="sonar", api_key=os.getenv("PERPLEXITY_API_KEY", "")))


def build_connectors(mode: str, property_id: str, access_token: str):
    if mode == "mock":
        return MockGA4Connector(), MockGSCConnector()

    if not property_id or not access_token:
        raise ValueError("real mode requires --property-id and --access-token")
    client = GoogleHttpClient(access_token=access_token)
    return RealGA4Connector(property_id=property_id, client=client), RealGSCConnector(client=client)


def main() -> None:
    args = parse_args()

    if args.print_oauth_url:
        oauth = GoogleOAuthService(oauth_config_from_env())
        url, state = oauth.build_auth_url()
        print(json.dumps({"auth_url": url, "state": state}, ensure_ascii=False, indent=2))
        return

    ga4, gsc = build_connectors(args.mode, args.property_id, args.access_token)
    tracker = build_prompt_tracker(args.prompt_mode)
    writer = SeoGeoExcelWriter() if args.excel_out else None

    pipeline = MonthlyReportPipeline(
        ga4=ga4,
        gsc=gsc,
        tracker=tracker,
        excel_writer=writer,
    )

    prompt_set = [
        {
            "prompt_id": "P001",
            "prompt_type": "직접형",
            "prompt_text": "SEO GEO 리포트 자동화 솔루션 추천해줘",
        }
    ]

    collected = pipeline.collect(
        client_name=args.client,
        site_url=args.site,
        month=args.month,
        prompt_set=prompt_set,
    )
    payload = pipeline.build_payload(collected)

    if args.excel_out:
        path = pipeline.export_excel(payload, args.excel_out)
        print(json.dumps({"excel_output": str(path)}, ensure_ascii=False, indent=2))
        return

    print(json.dumps(asdict(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
