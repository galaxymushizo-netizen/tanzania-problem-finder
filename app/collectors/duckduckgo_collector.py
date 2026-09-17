from ddgs import DDGS

from app.collectors.base import BaseCollector
from app.models import RawSearchResult
from app.logging_config import logger


class DuckDuckGoCollector(BaseCollector):
    def __init__(self):
        super().__init__(rate_limit_delay=2.0)
        self._ddgs = None

    def _get_ddgs(self):
        if self._ddgs is None:
            self._ddgs = DDGS()
        return self._ddgs

    def search(self, query: str, num_results: int = 10) -> list[RawSearchResult]:
        results = []
        try:
            ddgs = self._get_ddgs()
            raw = list(ddgs.text(query, region="tz-en", max_results=num_results))
            for item in raw:
                results.append(
                    RawSearchResult(
                        title=item.get("title", ""),
                        snippet=item.get("body", ""),
                        url=item.get("href", ""),
                        query_used=query,
                        source="duckduckgo",
                    )
                )
        except Exception as e:
            logger.error("DuckDuckGo search error: %s", e)

        return results[:num_results]
