from __future__ import annotations

import json
import os

from .cli import build_connectors, build_prompt_tracker
from .runtime import default_report_month
from .pipeline import MonthlyReportPipeline
from .excel_writer import SeoGeoExcelWriter


def run_monthly_job() -> dict[str, str]:
    month = os.getenv("REPORT_MONTH", default_report_month())
    mode = os.getenv("RUN_MODE", "mock")
    prompt_mode = os.getenv("PROMPT_MODE", "mock")
    client_name = os.getenv("CLIENT_NAME", "Demo Client")
    site_url = os.getenv("SITE_URL", "https://example.com")

    property_id = os.getenv("GA4_PROPERTY_ID", "")
    access_token = os.getenv("GOOGLE_ACCESS_TOKEN", "")
    excel_out = os.getenv("REPORT_OUTPUT_PATH", "")

    ga4, gsc = build_connectors(mode, property_id, access_token)
    tracker = build_prompt_tracker(prompt_mode)
    writer = SeoGeoExcelWriter() if excel_out else None

    pipeline = MonthlyReportPipeline(ga4=ga4, gsc=gsc, tracker=tracker, excel_writer=writer)

    prompt_set = [
        {
            "prompt_id": "P001",
            "prompt_type": "직접형",
            "prompt_text": "SEO GEO 리포트 자동화 솔루션 추천해줘",
        }
    ]

    collected = pipeline.collect(client_name=client_name, site_url=site_url, month=month, prompt_set=prompt_set)
    payload = pipeline.build_payload(collected)

    if excel_out:
        output = pipeline.export_excel(payload, excel_out)
        return {"status": "ok", "month": month, "excel_output": str(output)}

    return {"status": "ok", "month": month, "prompt_rows": str(len(payload.prompt_rows))}


def main() -> None:
    result = run_monthly_job()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
