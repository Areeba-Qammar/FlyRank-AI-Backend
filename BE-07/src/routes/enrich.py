import os
from fastapi import APIRouter, HTTPException
from src.llm.schema import EnrichInput, EnrichOutput, Category, QualityFlag

router = APIRouter()

@router.post("/enrich", response_model=EnrichOutput)
def enrich(payload: EnrichInput):
    if os.getenv("LLM_STUB") == "1":
        return EnrichOutput(
            category=Category.tech,
            summary="Stubbed summary for testing.",
            quality_flags=[QualityFlag.ok],
        )
    # Stage 2 will fill this in
    raise HTTPException(status_code=501, detail="Model call not implemented yet")