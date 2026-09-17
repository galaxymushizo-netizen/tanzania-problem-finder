import requests
from typing import Any

from app.collectors.base import BaseCollector
from app.config import Config
from app.models import RawSearchResult
from app.logging_config import logger


class BraveSearchCollector(BaseCollector):
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self):
        super().__init__(rate_limit_delay=1.0)
        self.api_key = Config.BRAVE_API_KEY

    def search(self, query: str, num_results: int = 10) -> list[RawSearchResult]:
        if not self.api_key:
            logger.warning("Brave Search API haijewekwa, inaachwa")
            return []

        results = []
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }
        params: dict[str, Any] = {
            "q": query,
            "count": min(num_results, 20),
            "country": "TZ",
            "search_lang": "en",
        }

        try:
            resp = requests.get(
                self.BASE_URL, headers=headers, params=params, timeout=15
            )
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("web", {}).get("results", []):
                results.append(
                    RawSearchResult(
                        title=item.get("title", ""),
                        snippet=item.get("description", ""),
                        url=item.get("url", ""),
                        query_used=query,
                        source="brave_search",
                    )
                )
        except requests.RequestException as e:
            logger.error("Brave Search API hitilafu: %s", e)

        return results[:num_results]
