import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from openai import APITimeoutError
from src.llm.schema import EnrichInput, EnrichOutput, Category, QualityFlag
from src.llm.client import call_model
from src.llm.parse import parse_and_validate

router = APIRouter()

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "enrich-v1.md"
PROMPT_VERSION = "enrich-v1"
QUARANTINE_LOG = Path("logs/quarantine.jsonl")

def load_prompt() -> str:
    return PROMPT_PATH.read_text()

def log_cost(usage: dict, repaired: bool):
    print(json.dumps({"event": "llm_call", "prompt_version": PROMPT_VERSION, "repaired": repaired, **usage}))

def quarantine(input_text: str, raw_output: str, error: str):
    QUARANTINE_LOG.parent.mkdir(exist_ok=True)
    with open(QUARANTINE_LOG, "a") as f:
        f.write(json.dumps({"input": input_text, "raw_output": raw_output, "error": error, "prompt_version": PROMPT_VERSION}) + "\n")

@router.post("/enrich", response_model=EnrichOutput)
def enrich(payload: EnrichInput):
    if os.getenv("LLM_STUB") == "1":
        return EnrichOutput(category=Category.tech, summary="Stubbed summary for testing.", quality_flags=[QualityFlag.ok])

    if os.getenv("LLM_ENABLED", "true").lower() == "false":
        return EnrichOutput(category=Category.other, summary="AI enrichment is currently disabled.", quality_flags=[QualityFlag.low_content])

    system_prompt = load_prompt()
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": payload.text}]

    try:
        raw_text, usage = call_model(messages)
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Model call timed out")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Model call failed: {e}")

    try:
        result = parse_and_validate(raw_text)
        log_cost(usage, repaired=False)
        return result
    except Exception as first_error:
        repair_messages = messages + [
            {"role": "assistant", "content": raw_text},
            {"role": "user", "content": f"Your previous answer was rejected for this reason: {first_error}. Return only corrected JSON matching the schema."},
        ]
        try:
            raw_text2, usage2 = call_model(repair_messages)
            result = parse_and_validate(raw_text2)
            log_cost(usage2, repaired=True)
            return result
        except Exception as second_error:
            quarantine(payload.text, raw_text, str(second_error))
            raise HTTPException(status_code=422, detail="Model output could not be validated after repair")