from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .collectors import MockPromptTracker
from .connectors import MockGA4Connector, MockGSCConnector
from .pipeline import MonthlyReportPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SEOGEO monthly report scaffold")
    parser.add_argument("--client", default="Demo Client")
    parser.add_argument("--site", default="https://example.com")
    parser.add_argument("--month", required=True, help="YYYY-MM")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = MonthlyReportPipeline(
        ga4=MockGA4Connector(),
        gsc=MockGSCConnector(),
        tracker=MockPromptTracker(),
    )
    prompt_set = [
        {
            "prompt_id": "P001",
            "prompt_type": "직접형",
            "prompt_text": "SEO GEO 리포트 자동화 솔루션 추천해줘",
            "engine": "gpt",
            "capture_method": "api",
        }
    ]
    collected = pipeline.collect(
        client_name=args.client,
        site_url=args.site,
        month=args.month,
        prompt_set=prompt_set,
    )
    payload = pipeline.build_payload(collected)
    print(json.dumps(asdict(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
