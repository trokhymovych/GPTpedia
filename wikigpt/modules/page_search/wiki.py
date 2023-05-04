import logging
from typing import Any

import mwapi

from wikigpt.modules.constants import (DEFAULT_NUMBER_OF_SEARCH_RESULTS,
                                       DEFAULT_SEARCH_SCORE)
from wikigpt.modules.entities import PageSearchResult
from wikigpt.modules.page_search.base import PageSearchBase

logger = logging.getLogger(__name__)


class PageSearchWiki(PageSearchBase):

    def __init__(self, logger_object: logging.Logger = logger, **kwargs: Any):
        super().__init__(logger_object, **kwargs)
        self.session = mwapi.Session('https://en.wikipedia.org')

    def search(self, query: str, **kwargs) -> PageSearchResult:
        n_results = kwargs.get("n_results", DEFAULT_NUMBER_OF_SEARCH_RESULTS)
        params = {
            "action": "query",
            "format": 2,
            "list": "search",
            "srsearch": query,
            "srprop": "size|redirecttitle|sectiontitle",
            "srlimit": n_results
        }
        response = self.session.get(**params)
        results_list = response.get("query", {}).get("search", [])
        pages_names = [page["title"] for page in results_list]
        search_result = PageSearchResult(
            query=query,
            n_results=len(results_list),
            pages_names=pages_names,
            metadata=results_list,
            scores=[DEFAULT_SEARCH_SCORE for _ in results_list]
        )
        return search_result
