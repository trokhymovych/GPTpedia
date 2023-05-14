import logging

from typing import Any

import mwparserfromhell as mw
import requests

from mwedittypes.utils import wikitext_to_plaintext

from gptpedia.modules.constants import ENWIKI_URL
from gptpedia.modules.entities import TextParseResult
from gptpedia.modules.text_parser.base import TextParserBase


logger = logging.getLogger(__name__)


class WikiParser(TextParserBase):
    def __init__(self, logger_object: logging.Logger = logger, **kwargs: Any) -> None:
        super().__init__(logger_object, **kwargs)
        self.logger = logger_object

    def parse_page_content(self, content: str, **kwargs) -> TextParseResult:
        """
        Method that is used to parse the content of the page for further usage.
        """
        # todo: Update sections parsing logic: consider nested sections

        page_name = kwargs.get("page_name", None)
        section_headings, sections_texts = self._parse_sections(content)
        return TextParseResult(
            page_name=page_name,
            sections_names=section_headings,
            sections_text=sections_texts
        )

    def get_page_content(self, page_link: str, wiki_url: str = ENWIKI_URL) -> str:
        """
        Method that implements the logic of getting the content of the page.
        """
        page_name = page_link.split("/")[-1]
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main",
            "rvlimit": 1,
            "titles": page_name,
            "format": "json",
            "formatversion": "2",
        }
        headers = {"User-Agent": "WikiGPT/1.0"}
        req = requests.get(wiki_url, headers=headers, params=params)
        res = req.json()
        revision = res["query"]["pages"][0]["revisions"][0]
        text = revision["slots"]["main"]["content"]
        return text

    def _parse_sections(self, text):
        """
        Method that recursively parse the wikipedia page to the sections.
        """
        if text == "":
            return [], []

        mw_page = mw.parse(text)
        sections = mw_page.get_sections()
        titles = mw_page.filter_headings()

        if len(titles) <= 1:
            return ["Introduction" if len(titles) == 0 else titles[0]], \
                [wikitext_to_plaintext(" ".join([str(s) for s in sections]))]

        titles = []
        texts = []
        for section in sections:
            if section == text:
                continue
            titles_local, texts_local = self._parse_sections(section)
            titles += titles_local
            texts += texts_local

        # dropping duplicates:
        unique_titles = list(set([str(t) for t in titles]))
        unique_texts = []
        for t in unique_titles:
            text_id = titles.index(t)
            unique_texts.append(texts[text_id])

        return unique_titles, unique_texts
