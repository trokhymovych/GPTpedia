from typing import List, Optional

from pydantic import BaseModel  # type: ignore


class PageSearchResult(BaseModel):
    query: str
    n_results: int
    pages_names: Optional[List[str]]
    pages_links: Optional[List[str]]
    metadata: Optional[List[dict]]
    scores: Optional[List[float]]


class TextParseResult(BaseModel):
    page_name: Optional[str]
    sections_names: Optional[List[str]]
    sections_text: List[str]


class TextDocument(BaseModel):
    document_id: str
    document_name: Optional[str]
    document_content: str
    score: Optional[float] = None
