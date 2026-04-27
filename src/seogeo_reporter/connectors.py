from __future__ import annotations

from dataclasses import dataclass

from .models import KeywordMonthlyMetric


@dataclass(slots=True)
class GA4MonthlySummary:
    organic_sessions: int
    referral_sessions: int
    conversions: int


class GA4Connector:
    def fetch_monthly_summary(self, site_url: str, month: str) -> GA4MonthlySummary:
        raise NotImplementedError


class GSCConnector:
    def fetch_keyword_metrics(self, site_url: str, month: str) -> list[KeywordMonthlyMetric]:
        raise NotImplementedError


class MockGA4Connector(GA4Connector):
    def fetch_monthly_summary(self, site_url: str, month: str) -> GA4MonthlySummary:
        _ = (site_url, month)
        return GA4MonthlySummary(
            organic_sessions=1200,
            referral_sessions=340,
            conversions=56,
        )


class MockGSCConnector(GSCConnector):
    def fetch_keyword_metrics(self, site_url: str, month: str) -> list[KeywordMonthlyMetric]:
        _ = (site_url, month)
        return [
            KeywordMonthlyMetric(
                keyword="seo 리포트 자동화",
                previous_impressions=1200,
                current_impressions=1560,
                previous_clicks=32,
                current_clicks=55,
                previous_ctr=2.67,
                current_ctr=3.52,
                previous_position=12.4,
                current_position=9.8,
            )
        ]
