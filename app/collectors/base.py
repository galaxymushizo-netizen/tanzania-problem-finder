import time
from abc import ABC, abstractmethod

from app.models import RawSearchResult
from app.logging_config import logger


class BaseCollector(ABC):
    def __init__(self, rate_limit_delay: float = 1.0):
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0

    def _throttle(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    @abstractmethod
    def search(self, query: str, num_results: int = 10) -> list[RawSearchResult]:
        ...

    def search_multiple(
        self, queries: list[str], num_results: int = 10
    ) -> list[RawSearchResult]:
        all_results = []
        for query in queries:
            try:
                self._throttle()
                results = self.search(query, num_results)
                all_results.extend(results)
                logger.info(
                    "%s: query='%s' -> %d results",
                    self.__class__.__name__,
                    query,
                    len(results),
                )
            except Exception as e:
                logger.error(
                    "%s failed for '%s': %s",
                    self.__class__.__name__,
                    query,
                    e,
                )
        return all_results
