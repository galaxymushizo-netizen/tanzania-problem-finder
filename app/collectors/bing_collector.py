import requests
from typing import Any

from app.collectors.base import BaseCollector
from app.config import Config
from app.models import RawSearchResult
from app.logging_config import logger


class BingSearchCollector(BaseCollector):
    BASE_URL = "https://api.bing.microsoft.com/v7.0/search"

    def __init__(self):
        super().__init__(rate_limit_delay=1.0)
        self.api_key = Config.BING_API_KEY

    def search(self, query: str, num_results: int = 10) -> list[RawSearchResult]:
        if not self.api_key:
            logger.warning("Bing Search API haijewekwa, inaachwa")
            return []

        results = []
        for offset in range(0, min(num_results, 50), 10):
            count = min(10, num_results - len(results))
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            params: dict[str, Any] = {
                "q": query,
                "count": count,
                "offset": offset,
                "mkt": "en-TZ",
                "safesearch": "Off",
            }

            try:
                resp = requests.get(
                    self.BASE_URL, headers=headers, params=params, timeout=15
                )
                resp.raise_for_status()
                data = resp.json()

                for item in data.get("webPages", {}).get("value", []):
                    results.append(
                        RawSearchResult(
                            title=item.get("name", ""),
                            snippet=item.get("snippet", ""),
                            url=item.get("url", ""),
                            query_used=query,
                            source="bing_search",
                        )
                    )
            except requests.RequestException as e:
                logger.error("Bing Search API hitilafu: %s", e)
                break

        return results
