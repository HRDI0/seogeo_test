from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from .date_utils import month_range, previous_month
from .models import KeywordMonthlyMetric


@dataclass(slots=True)
class GA4MonthlySummary:
    organic_sessions: int
    referral_sessions: int
    conversions: int


class GoogleApiError(RuntimeError):
    pass


class GoogleHttpClient:
    def __init__(self, access_token: str) -> None:
        if not access_token:
            raise ValueError("access_token is required")
        self.access_token = access_token

    def post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        raw = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url=url, data=raw, method="POST")
        req.add_header("Authorization", f"Bearer {self.access_token}")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise GoogleApiError(f"Google API request failed ({url}): {exc}") from exc


class GA4Connector:
    def fetch_monthly_summary(self, site_url: str, month: str) -> GA4MonthlySummary:
        raise NotImplementedError


class GSCConnector:
    def fetch_keyword_metrics(self, site_url: str, month: str) -> list[KeywordMonthlyMetric]:
        raise NotImplementedError


class RealGA4Connector(GA4Connector):
    """Fetch monthly summary from GA4 Data API runReport endpoint."""

    def __init__(self, property_id: str, client: GoogleHttpClient, ga4_endpoint_base: str = "https://analyticsdata.googleapis.com") -> None:
        if not property_id:
            raise ValueError("property_id is required")
        self.property_id = property_id
        self.client = client
        self.ga4_endpoint_base = ga4_endpoint_base.rstrip("/")

    def fetch_monthly_summary(self, site_url: str, month: str) -> GA4MonthlySummary:
        _ = site_url
        current = month_range(month)
        url = f"{self.ga4_endpoint_base}/v1beta/properties/{self.property_id}:runReport"
        payload = {
            "dateRanges": [{"startDate": current.start_date, "endDate": current.end_date}],
            "dimensions": [{"name": "sessionDefaultChannelGroup"}],
            "metrics": [{"name": "sessions"}, {"name": "conversions"}],
            "limit": 100,
        }
        data = self.client.post_json(url, payload)
        return _parse_ga4_channel_rows(data.get("rows", []))


class RealGSCConnector(GSCConnector):
    """Fetch query-level metrics from Search Console Search Analytics API."""

    def __init__(self, client: GoogleHttpClient, row_limit: int = 250, gsc_endpoint_base: str = "https://searchconsole.googleapis.com") -> None:
        if row_limit <= 0:
            raise ValueError("row_limit must be > 0")
        self.client = client
        self.row_limit = row_limit
        self.gsc_endpoint_base = gsc_endpoint_base.rstrip("/")

    def fetch_keyword_metrics(self, site_url: str, month: str) -> list[KeywordMonthlyMetric]:
        current = month_range(month)
        prev = month_range(previous_month(month))

        previous_rows = self._query_all(site_url, prev.start_date, prev.end_date)
        current_rows = self._query_all(site_url, current.start_date, current.end_date)

        keywords = sorted(set(previous_rows) | set(current_rows))
        return [self._merge_keyword_rows(keyword, previous_rows.get(keyword), current_rows.get(keyword)) for keyword in keywords]

    def _query_all(self, site_url: str, start_date: str, end_date: str) -> dict[str, dict[str, float]]:
        start_row = 0
        output: dict[str, dict[str, float]] = {}

        while True:
            rows = self._query_page(site_url, start_date, end_date, start_row)
            if not rows:
                break

            for row in rows:
                key = (row.get("keys") or [""])[0]
                output[key] = {
                    "clicks": float(row.get("clicks", 0)),
                    "impressions": float(row.get("impressions", 0)),
                    "ctr": float(row.get("ctr", 0)),
                    "position": float(row.get("position", 0)),
                }

            if len(rows) < self.row_limit:
                break
            start_row += self.row_limit

        return output

    def _query_page(self, site_url: str, start_date: str, end_date: str, start_row: int) -> list[dict[str, Any]]:
        encoded_site = urllib.parse.quote(site_url, safe="")
        api_url = f"{self.gsc_endpoint_base}/webmasters/v3/sites/{encoded_site}/searchAnalytics/query"
        payload = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": self.row_limit,
            "startRow": start_row,
        }
        data = self.client.post_json(api_url, payload)
        return data.get("rows", [])

    @staticmethod
    def _merge_keyword_rows(
        keyword: str,
        previous: dict[str, float] | None,
        current: dict[str, float] | None,
    ) -> KeywordMonthlyMetric:
        p = previous or {}
        c = current or {}
        return KeywordMonthlyMetric(
            keyword=keyword,
            previous_impressions=int(p.get("impressions", 0)),
            current_impressions=int(c.get("impressions", 0)),
            previous_clicks=int(p.get("clicks", 0)),
            current_clicks=int(c.get("clicks", 0)),
            previous_ctr=float(p.get("ctr", 0.0)) * 100,
            current_ctr=float(c.get("ctr", 0.0)) * 100,
            previous_position=float(p.get("position", 0.0)),
            current_position=float(c.get("position", 0.0)),
        )


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


def _parse_ga4_channel_rows(rows: list[dict[str, Any]]) -> GA4MonthlySummary:
    organic_sessions = 0
    referral_sessions = 0
    conversions = 0

    for row in rows:
        channel = row.get("dimensionValues", [{}])[0].get("value", "")
        metric_values = row.get("metricValues", [])
        sessions = int(float((metric_values[0] if len(metric_values) > 0 else {}).get("value", "0")))
        row_conversions = int(float((metric_values[1] if len(metric_values) > 1 else {}).get("value", "0")))
        conversions += row_conversions

        channel_lower = channel.lower()
        if channel_lower == "organic search":
            organic_sessions += sessions
        elif channel_lower == "referral":
            referral_sessions += sessions

    return GA4MonthlySummary(
        organic_sessions=organic_sessions,
        referral_sessions=referral_sessions,
        conversions=conversions,
    )
