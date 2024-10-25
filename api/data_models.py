from typing import List
from pydantic import BaseModel


class Dataset(BaseModel):
    """Expected schema based on data/dataset_metadata.json"""

    dataset_name: str
    readable_name: str
    dataset_description: str
    category: str
    subcategories: List[str]
    columns: List[str]


class SearchQuery(BaseModel):
    """Model representing a search query"""

    query: str
