import logging

from abc import ABC, abstractmethod
from typing import Any

from gptpedia.modules.entities import PageSearchResult


logger = logging.getLogger(__name__)


class PageSearchBase(ABC):
    def __init__(self, logger_object: logging.Logger = logger, **kwargs: Any) -> None:
        self.logger = logger_object

    @abstractmethod
    def search(self, query: str, **kwargs) -> PageSearchResult:
        raise NotImplementedError
