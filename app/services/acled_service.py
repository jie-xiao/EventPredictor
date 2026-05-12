# app/services/acled_service.py
"""ACLED API client - optional data source for armed conflict event data."""
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone


class AcledService:
    """Minimal ACLED API client. Disabled by default - enable in config.yaml."""

    BASE_URL = "https://api.acleddata.com/acled/read"

    def __init__(self, enabled: bool = False, api_key: Optional[str] = None, timeout: int = 30):
        self.enabled = enabled
        self.api_key = api_key
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
        country: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        if not self.enabled or not self.api_key:
            return []
        await self._ensure_client()

        if start_date is None:
            start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")

        params = {
            "key": self.api_key,
            "limit": limit,
            "event_date": start_date,
            "event_date_where": ">=",
        }
        if country:
            params["country"] = country
        if event_type:
            params["event_type"] = event_type

        resp = await self._client.get(self.BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])

    async def get_casualty_count(
        self, event_title: str, event_description: str
    ) -> Optional[Dict[str, Any]]:
        """Try to find ACLED casualty count for a given event."""
        if not self.enabled or not self.api_key:
            return None
        keywords = " ".join(event_title.split()[:5])
        events = await self.query_events(limit=10)
        if not events:
            return None
        fatalities = [e.get("fatalities", 0) for e in events if e.get("fatalities")]
        return {
            "casualty_count": sum(fatalities),
            "event_count": len(events),
            "source": "acled",
        }


# Global singleton - disabled by default
acled_service = AcledService()
