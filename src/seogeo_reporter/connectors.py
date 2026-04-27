from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

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
            raise GoogleApiError(f"Google API request failed: {exc}") from exc


class GA4Connector:
    def fetch_monthly_summary(self, site_url: str, month: str) -> GA4MonthlySummary:
        raise NotImplementedError


class GSCConnector:
    def fetch_keyword_metrics(self, site_url: str, month: str) -> list[KeywordMonthlyMetric]:
        raise NotImplementedError


class RealGA4Connector(GA4Connector):
    """Fetches monthly summary from GA4 Data API runReport endpoint."""

    def __init__(self, property_id: str, client: GoogleHttpClient) -> None:
        self.property_id = property_id
        self.client = client

    def fetch_monthly_summary(self, site_url: str, month: str) -> GA4MonthlySummary:
        _ = site_url
        start_date = f"{month}-01"
        end_date = f"{month}-31"
        url = f"https://analyticsdata.googleapis.com/v1beta/properties/{self.property_id}:runReport"
        payload = {
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "dimensions": [{"name": "sessionDefaultChannelGroup"}],
            "metrics": [{"name": "sessions"}, {"name": "conversions"}],
            "limit": 100,
        }
        data = self.client.post_json(url, payload)
        organic_sessions = 0
        referral_sessions = 0
        conversions = 0
        for row in data.get("rows", []):
            channel = row.get("dimensionValues", [{}])[0].get("value", "")
            sessions = int(float(row.get("metricValues", [{"value": "0"}])[0].get("value", "0")))
            row_conversions = int(float(row.get("metricValues", [{}, {"value": "0"}])[1].get("value", "0")))
            conversions += row_conversions
            if channel.lower() == "organic search":
                organic_sessions += sessions
            if channel.lower() == "referral":
                referral_sessions += sessions
        return GA4MonthlySummary(
            organic_sessions=organic_sessions,
            referral_sessions=referral_sessions,
            conversions=conversions,
        )


class RealGSCConnector(GSCConnector):
    """Fetches query level metrics from Search Console Search Analytics API."""

    def __init__(self, client: GoogleHttpClient, row_limit: int = 250) -> None:
        self.client = client
        self.row_limit = row_limit

    def fetch_keyword_metrics(self, site_url: str, month: str) -> list[KeywordMonthlyMetric]:
        current_start = f"{month}-01"
        current_end = f"{month}-31"
        prev_month = _previous_month(month)
        prev_start = f"{prev_month}-01"
        prev_end = f"{prev_month}-31"

        previous = self._query(site_url, prev_start, prev_end)
        current = self._query(site_url, current_start, current_end)

        keywords = sorted(set(previous) | set(current))
        rows: list[KeywordMonthlyMetric] = []
        for keyword in keywords:
            p = previous.get(keyword, {})
            c = current.get(keyword, {})
            rows.append(
                KeywordMonthlyMetric(
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
            )
        return rows

    def _query(self, site_url: str, start_date: str, end_date: str) -> dict[str, dict[str, float]]:
        encoded_site = urllib.parse.quote(site_url, safe="")
        api_url = f"https://searchconsole.googleapis.com/webmasters/v3/sites/{encoded_site}/searchAnalytics/query"
        payload = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": self.row_limit,
            "startRow": 0,
        }
        data = self.client.post_json(api_url, payload)
        output: dict[str, dict[str, float]] = {}
        for row in data.get("rows", []):
            key = (row.get("keys") or [""])[0]
            output[key] = {
                "clicks": float(row.get("clicks", 0)),
                "impressions": float(row.get("impressions", 0)),
                "ctr": float(row.get("ctr", 0)),
                "position": float(row.get("position", 0)),
            }
        return output


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


def _previous_month(month: str) -> str:
    year, mon = month.split("-")
    y = int(year)
    m = int(mon)
    if m == 1:
        return f"{y - 1}-12"
    return f"{y:04d}-{m - 1:02d}"
