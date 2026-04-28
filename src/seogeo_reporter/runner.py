from __future__ import annotations

import json

from .cli import build_connectors, build_prompt_tracker
from .config import app_config_from_env
from .date_utils import month_range
from .pipeline import MonthlyReportPipeline
from .excel_writer import SeoGeoExcelWriter
from .runtime import default_report_month


def run_monthly_job() -> dict[str, str]:
    cfg = app_config_from_env()
    month = cfg.report_month or default_report_month()
    month_range(month)  # validate

    ga4, gsc = build_connectors(cfg.run_mode, cfg.ga4_property_id, cfg.google_access_token)
    tracker = build_prompt_tracker(cfg.prompt_mode)
    writer = SeoGeoExcelWriter() if cfg.report_output_path else None

    pipeline = MonthlyReportPipeline(ga4=ga4, gsc=gsc, tracker=tracker, excel_writer=writer)

    prompt_set = [
        {
            "prompt_id": "P001",
            "prompt_type": "직접형",
            "prompt_text": "SEO GEO 리포트 자동화 솔루션 추천해줘",
        }
    ]

    collected = pipeline.collect(client_name=cfg.client_name, site_url=cfg.site_url, month=month, prompt_set=prompt_set)
    payload = pipeline.build_payload(collected)

    if cfg.report_output_path:
        output = pipeline.export_excel(payload, cfg.report_output_path)
        return {"status": "ok", "month": month, "excel_output": str(output)}

    return {"status": "ok", "month": month, "prompt_rows": str(len(payload.prompt_rows))}


def main() -> None:
    try:
        result = run_monthly_job()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(2)


if __name__ == "__main__":
    main()
