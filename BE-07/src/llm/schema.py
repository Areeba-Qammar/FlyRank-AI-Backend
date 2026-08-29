from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class Category(str, Enum):
    TECH = "tech"
    BUSINESS = "business"
    HEALTH = "health"
    LIFESTYLE = "lifestyle"
    OTHER = "other"

class QualityFlag(str, Enum):
    DUPLICATE = "duplicate"
    LOW_CONTENT = "low_content"
    SPAM = "spam"
    OK = "ok"

class EnrichOutput(BaseModel):
    category: Category
    summary: str = Field(..., max_length=300)
    quality_flags: List[QualityFlag]

class EnrichInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)