import requests
from typing import Any

from app.collectors.base import BaseCollector
from app.config import Config
from app.models import RawSearchResult
from app.logging_config import logger


class GoogleSearchCollector(BaseCollector):
    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self):
        super().__init__(rate_limit_delay=1.0)
        self.api_key = Config.GOOGLE_API_KEY
        self.search_engine_id = Config.GOOGLE_SEARCH_ENGINE_ID

    def search(self, query: str, num_results: int = 10) -> list[RawSearchResult]:
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Search API not configured, skipping")
            return []

        results = []
        for start_index in range(1, num_results + 1, 10):
            params: dict[str, Any] = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(10, num_results - len(results)),
                "start": start_index,
                "lr": "lang_sw",
                "gl": "tz",
            }

            try:
                resp = requests.get(self.BASE_URL, params=params, timeout=15)
                resp.raise_for_status()
                data = resp.json()

                for item in data.get("items", []):
                    results.append(
                        RawSearchResult(
                            title=item.get("title", ""),
                            snippet=item.get("snippet", ""),
                            url=item.get("link", ""),
                            query_used=query,
                            source="google_search",
                        )
                    )
            except requests.RequestException as e:
                logger.error("Google Search API error: %s", e)
                break

        return results
