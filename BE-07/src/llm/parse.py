import json
import re
from src.llm.schema import EnrichOutput

def extract_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    return json.loads(text)

def parse_and_validate(text: str) -> EnrichOutput:
    return EnrichOutput.model_validate(extract_json(text))