from __future__ import annotations

from dataclasses import asdict

from .collectors import PromptTracker
from .connectors import GA4Connector, GSCConnector
from .models import MonthlyReportInput, MonthlyReportPayload
from .tiering import enrich_tier


class MonthlyReportPipeline:
    def __init__(self, ga4: GA4Connector, gsc: GSCConnector, tracker: PromptTracker) -> None:
        self.ga4 = ga4
        self.gsc = gsc
        self.tracker = tracker

    def collect(self, client_name: str, site_url: str, month: str, prompt_set: list[dict[str, str]]) -> MonthlyReportInput:
        ga4_summary = asdict(self.ga4.fetch_monthly_summary(site_url=site_url, month=month))
        gsc_keywords = self.gsc.fetch_keyword_metrics(site_url=site_url, month=month)
        prompt_results = [enrich_tier(row) for row in self.tracker.run(prompt_set)]
        return MonthlyReportInput(
            client_name=client_name,
            site_url=site_url,
            month=month,
            ga4_summary=ga4_summary,
            gsc_keywords=gsc_keywords,
            prompt_results=prompt_results,
        )

    def build_payload(self, data: MonthlyReportInput) -> MonthlyReportPayload:
        overview = {
            "client_name": data.client_name,
            "site_url": data.site_url,
            "month": data.month,
        }
        prompt_rows = [asdict(row) for row in data.prompt_results]
        keyword_rows = [asdict(row) for row in data.gsc_keywords]
        summary_rows = [
            {
                "organic_sessions": data.ga4_summary.get("organic_sessions", 0),
                "referral_sessions": data.ga4_summary.get("referral_sessions", 0),
                "conversions": data.ga4_summary.get("conversions", 0),
            }
        ]
        return MonthlyReportPayload(
            overview=overview,
            prompt_rows=prompt_rows,
            keyword_rows=keyword_rows,
            summary_rows=summary_rows,
        )
