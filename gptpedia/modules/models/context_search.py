import logging
import re

from typing import Any, List

from gptpedia.modules.entities import TextDocument
from gptpedia.modules.page_search.wiki_extended import PageSearchWikiExtended
from gptpedia.modules.text_parser.wiki_parser import WikiParser
from gptpedia.modules.text_search.vector import TextSearchVector


logger = logging.getLogger(__name__)


class ContextPipeline:
    def __init__(self, logger_object: logging.Logger = logger, **kwargs: Any) -> None:
        self.logger = logger_object
        self.logger.info("Begin initialization")
        self.page_searcher = PageSearchWikiExtended(logger, **kwargs)
        self.page_parser = WikiParser(logger, **kwargs)
        self.text_searcher = TextSearchVector(logger, **kwargs)
        self.logger.info("Initialization completed")

    def generate_contex(self, question: str, **kwargs) -> str:
        """
        Method that implements question answering pipeline with Wikipedia model
        """
        # Step 1: Looking for Wikipedia pages:
        serp = self.page_searcher.search(question)
        self.logger.debug(f"Pages names found: {serp.pages_names}")

        # Step 2: Parse Wikipedia pages:
        content_found = []
        for pages_name in serp.pages_names:
            try:
                self.logger.debug(f"Parsing page {pages_name}")
                wikitext = self.page_parser.get_page_content(pages_name)
                content_found.append(self.page_parser.parse_page_content(wikitext, page_name=pages_name))
            except Exception as e:
                self.logger.debug(f"Passing page {pages_name}, {e}")

        # Step 3: Find the sections that are more likely include the answer
        documents_to_index = []
        index_ = 0
        for page_documents in content_found:
            for i, (content, section_name) in enumerate(
                    zip(page_documents.sections_text, page_documents.sections_names)
            ):
                for j, sentence in enumerate(self.split_sentences(content)):
                    documents_to_index.append(
                        TextDocument(document_id=index_, document_content=sentence, document_name=section_name)
                    )
                    index_ += 1

        self.text_searcher.index(documents_to_index)
        search_results = self.text_searcher.search(question, n_results=15)

        return self.process_search_results(search_results)

    @staticmethod
    def process_search_results(search_results: List) -> str:
        """
        Method to process search results and construct a context
        """
        search_results_joined = "/n/n".join([sr.document_content for sr in search_results])
        q1 = "(===).*w*(===)"
        q2 = "(==).*w*(==)"
        search_results_joined = search_results_joined.replace("/n", "")
        search_results_joined = re.sub(q1, '', search_results_joined)
        search_results_joined = re.sub(q2, '', search_results_joined)
        return search_results_joined

    @staticmethod
    def split_sentences(section: str) -> List[str]:
        return section.split(".")
