import logging

from typing import Any, List

from flair.data import Sentence
from flair.models import SequenceTagger

from gptpedia.modules.constants import DEFAULT_SEARCH_SCORE
from gptpedia.modules.entities import PageSearchResult
from gptpedia.modules.page_search.wiki import PageSearchWiki


logger = logging.getLogger(__name__)


class PageSearchWikiExtended(PageSearchWiki):

    def __init__(self, logger_object: logging.Logger = logger, **kwargs: Any):
        super().__init__(logger_object, **kwargs)
        self.tagger = SequenceTagger.load('ner-fast')

    def search(self, query: str, **kwargs) -> PageSearchResult:
        """
        Method that implements search using named entities parsing
        # todo: consider search each named entity separately
        """
        named_entities = self._get_entities(query)
        search_results = super().search(query, **kwargs)
        if len(' '.join(named_entities)) > 3:
            ne_search_results = super().search(' '.join(named_entities), **kwargs)
            results_mixed = self._mix_results(search_results, ne_search_results)
            return results_mixed
        else:
            return search_results

    @staticmethod
    def _mix_results(result_left: PageSearchResult, result_right: PageSearchResult) -> PageSearchResult:
        """
        Mix results from all sources
        # todo: consider results resorting
        """
        for ne_title, ne_metadata in zip(result_right.pages_names, result_right.metadata):
            if ne_title in result_left.pages_names:
                page_name_id = result_left.pages_names.index(ne_title)
                result_left.scores[page_name_id] += DEFAULT_SEARCH_SCORE
            else:
                result_left.pages_names.append(ne_title)
                result_left.metadata.append(ne_metadata)
                result_left.scores.append(DEFAULT_SEARCH_SCORE)
        return result_left

    def _get_entities(self, text: str) -> List[str]:
        """
        Get the list of named entities for given text.
        :param text: str, text used for NER extraction
        :return list of str (entities found in text)
        """
        sentence = Sentence(text)
        self.tagger.predict(sentence)
        entities = []
        for entity in sentence.get_spans('ner'):
            entities.append(entity.text)
        return entities
