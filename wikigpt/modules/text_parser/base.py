import logging
from abc import ABC, abstractmethod
from typing import Any

from wikigpt.modules.entities import TextParseResult

logger = logging.getLogger(__name__)


class TextParserBase(ABC):
    def __init__(self, logger_object: logging.Logger = logger, **kwargs: Any) -> None:
        self.logger = logger_object

    @abstractmethod
    def parse_page_content(self, content: str, **kwargs) -> TextParseResult:
        """
        Method that is used to parse the content of the page for further usage.
        """
        raise NotImplementedError

    def get_page_content(self, page_link: str) -> str:
        """
        Method that implements the logic of getting the content of the page.
        """
        raise NotImplementedError
