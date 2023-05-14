import logging

from typing import Any, List

from tqdm import tqdm
from transformers import pipeline

from gptpedia.modules.constants import DEFAULT_QNA_MODEL, QA_MIN_SCORE
from gptpedia.modules.entities import TextDocument
from gptpedia.modules.page_search.wiki_extended import PageSearchWikiExtended
from gptpedia.modules.text_parser.wiki_parser import WikiParser
from gptpedia.modules.text_search.vector import TextSearchVector
from gptpedia.modules.utils import text_processing_base


logger = logging.getLogger(__name__)


class QNAPipeline:
    def __init__(self, logger_object: logging.Logger = logger, **kwargs: Any) -> None:
        self.logger = logger_object
        self.logger.info("Begin initialization")
        self.page_searcher = PageSearchWikiExtended(logger, **kwargs)
        self.page_parser = WikiParser(logger, **kwargs)
        self.text_searcher = TextSearchVector(logger, **kwargs)

        qna_model_name = kwargs.get("qna_model_name", DEFAULT_QNA_MODEL)
        self.qna_model = pipeline('question-answering', model=qna_model_name, tokenizer=qna_model_name)
        self.logger.info("Initialization completed")

    def question_answer(self, question: str, **kwargs) -> List:
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
        for page_documents in content_found:
            for i, (content, section_name) in enumerate(
                    zip(page_documents.sections_text, page_documents.sections_names)
            ):
                documents_to_index.append(
                    TextDocument(document_id=i, document_content=content, document_name=section_name)
                )
        self.text_searcher.index(documents_to_index)
        search_results = self.text_searcher.search(question, n_results=20)
        self.logger.info(f"Section names found: {[d.document_name for d in search_results]}")

        # Step 4:
        answers = []
        for search_result in tqdm(search_results):
            qa_input = {
                'question': question,
                'context': text_processing_base(search_result.document_content),
            }
            qna_result = self.qna_model(qa_input)
            if qna_result["score"] > QA_MIN_SCORE:
                answers.append((qna_result["answer"], qna_result["score"]))
        return sorted(answers, key=lambda x: -x[1])
