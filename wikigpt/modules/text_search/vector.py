import logging
import time
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer, util

from wikigpt.modules.constants import (DEFAULT_EMBEDDINGS_MODEL,
                                       DEFAULT_NUMBER_OF_TEXT_SEARCH_RESULTS)
from wikigpt.modules.entities import TextDocument
from wikigpt.modules.text_search.base import TextSearchBase

logger = logging.getLogger(__name__)


class TextSearchVector(TextSearchBase):
    def __init__(self, logger_object: logging.Logger = logger, **kwargs: Any) -> None:
        super().__init__(logger_object, **kwargs)
        model_name = kwargs.get("model_name", DEFAULT_EMBEDDINGS_MODEL)
        self.encoder = SentenceTransformer(model_name)

    def index(self, documents: list[TextDocument], **kwargs):
        """
        Method that implements indexing of the content
        """
        self.documents = documents
        passages_texts = [self._text_processing(document.document_content) for document in documents]
        passages_names = [self._text_processing(document.document_name) for document in documents]
        self.corpus_embeddings = self.encoder.encode(
            passages_texts,
            convert_to_tensor=True,
            show_progress_bar=True
        )
        self.names_embeddings = self.encoder.encode(
            passages_names,
            convert_to_tensor=True,
            show_progress_bar=True
        )

    def search(self, query: str, **kwargs) -> list[TextDocument]:
        """
        Method to search within documents:
        # todo: define the key phrases improves the general model performance.
        # todo: filter the most frequent phrases, as they downgrade the search for vectors
        """
        start_time = time.time()
        n_results = kwargs.get("n_results", DEFAULT_NUMBER_OF_TEXT_SEARCH_RESULTS)
        question_embedding = self.encoder.encode(query, convert_to_tensor=True)
        hits_corpus = util.semantic_search(question_embedding, self.corpus_embeddings, top_k=n_results)[0]
        hits_names = util.semantic_search(question_embedding, self.names_embeddings, top_k=n_results)[0]
        corpus_scores_dict = {d["corpus_id"]: d["score"] for d in hits_corpus}
        names_scores_dict = {d["corpus_id"]: d["score"] for d in hits_names}
        found_documents = []
        for i, document in enumerate(self.documents):
            if (i in corpus_scores_dict) or (i in names_scores_dict):
                document.score = corpus_scores_dict.get(i, 0) + names_scores_dict.get(i, 0)
                found_documents.append(document)

        # Limiting amount of documents:
        found_documents_scores = [d.score for d in found_documents]
        selected_ids = np.argsort(found_documents_scores)[::-1]
        found_documents_filtered = [found_documents[i] for i in selected_ids]
        end_time = time.time()
        self.logger.info(f"Search time: {end_time - start_time}")
        return found_documents_filtered

    @staticmethod
    def _text_processing(text: str) -> str:
        """
        Method for internal basic text processing before vectorisation.
        """
        text = text.replace("===", " ")
        text = text.replace("==", " ")
        text = text.replace("\n", " ")
        return text
