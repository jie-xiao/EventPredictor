# app/services/gdelt_service.py
"""GDELT 2.0 API client - optional data source for conflict event data."""
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone


class GdeltService:
    """Minimal GDELT 2.0 client. Disabled by default - enable in config.yaml."""

    BASE_URL = "https://api.gdeltproject.org/api/v2"

    def __init__(self, enabled: bool = False, timeout: int = 30):
        self.enabled = enabled
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _ensure_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def query_events(
        self,
        query: str,
        start_date: Optional[str] = None,
        max_records: int = 50,
    ) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        await self._ensure_client()

        if start_date is None:
            start_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y%m%d%H%M%S")

        params = {
            "query": query,
            "mode": "artlist",
            "format": "json",
            "maxrecords": max_records,
            "startdatetime": start_date,
        }
        resp = await self._client.get(f"{self.BASE_URL}/doc/georaw", params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("articles", [])

    async def query_by_country(
        self, country_code: str, max_records: int = 30
    ) -> List[Dict[str, Any]]:
        """Query GDELT for events involving a specific country (ISO 2-letter code)."""
        return await self.query_events(f"sourcecountry:{country_code}", max_records=max_records)

    async def get_goldstein_for_event(
        self, event_title: str, event_description: str
    ) -> Optional[Dict[str, Any]]:
        """Try to find GDELT Goldstein score for a given event."""
        if not self.enabled:
            return None
        keywords = " ".join(event_title.split()[:5])
        articles = await self.query_events(keywords, max_records=10)
        if not articles:
            return None
        scores = [a.get("goldsteinscale") for a in articles if a.get("goldsteinscale") is not None]
        if not scores:
            return None
        return {
            "goldstein_score": round(sum(scores) / len(scores), 2),
            "article_count": len(articles),
            "source": "gdelt",
        }


# Global singleton - disabled by default
gdelt_service = GdeltService()
