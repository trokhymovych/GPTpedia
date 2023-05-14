import logging

from abc import ABC, abstractmethod
from typing import Any, List

from gptpedia.modules.entities import PageSearchResult, TextDocument


logger = logging.getLogger(__name__)


class TextSearchBase(ABC):
    def __init__(self, logger_object: logging.Logger = logger, **kwargs: Any) -> None:
        self.logger = logger_object

    @abstractmethod
    def index(self, documents: List[TextDocument], **kwargs):
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, **kwargs) -> PageSearchResult:
        raise NotImplementedError
