from pydantic import BaseModel
from typing import List

class KnownWordsList(BaseModel):
    words: List[str]
