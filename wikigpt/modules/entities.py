from typing import Optional

from pydantic import BaseModel  # type: ignore


class PageSearchResult(BaseModel):
    query: str
    n_results: int
    pages_names: Optional[list[str]]
    pages_links: Optional[list[str]]
    metadata: Optional[list[dict]]
    scores: Optional[list[float]]
