from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class Category(str, Enum):
    tech = "tech"
    business = "business"
    health = "health"
    lifestyle = "lifestyle"
    other = "other"

class QualityFlag(str, Enum):
    duplicate = "duplicate"
    low_content = "low_content"
    spam = "spam"
    ok = "ok"

class EnrichOutput(BaseModel):
    category: Category
    summary: str = Field(..., max_length=300)
    quality_flags: List[QualityFlag]

class EnrichInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)