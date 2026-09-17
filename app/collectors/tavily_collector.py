import requests
from typing import Any

from app.collectors.base import BaseCollector
from app.config import Config
from app.models import RawSearchResult
from app.logging_config import logger


class TavilySearchCollector(BaseCollector):
    BASE_URL = "https://api.tavily.com/search"

    def __init__(self):
        super().__init__(rate_limit_delay=1.0)
        self.api_key = Config.TAVILY_API_KEY

    def search(self, query: str, num_results: int = 10) -> list[RawSearchResult]:
        if not self.api_key:
            logger.warning("Tavily Search API haijewekwa, inaachwa")
            return []

        results = []
        payload: dict[str, Any] = {
            "api_key": self.api_key,
            "query": query,
            "max_results": min(num_results, 20),
            "search_depth": "basic",
            "include_answer": False,
        }

        try:
            resp = requests.post(
                self.BASE_URL, json=payload, timeout=15
            )
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("results", []):
                results.append(
                    RawSearchResult(
                        title=item.get("title", ""),
                        snippet=item.get("content", ""),
                        url=item.get("url", ""),
                        query_used=query,
                        source="tavily",
                    )
                )
        except requests.RequestException as e:
            logger.error("Tavily Search API hitilafu: %s", e)

        return results[:num_results]
