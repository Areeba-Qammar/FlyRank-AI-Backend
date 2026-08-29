import os
import time
import random
from dotenv import load_dotenv
from openai import OpenAI, APITimeoutError, APIStatusError

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.environ["LLM_API_KEY"],
            timeout=30.0,
            max_retries=0,
        )
    return _client

RETRYABLE_STATUS = {429, 500, 502, 503, 504}

def call_model(messages: list, max_retries: int = 2):
    client = get_client()
    model = os.environ["LLM_MODEL"]
    attempt = 0
    start = time.monotonic()
    
    while True:
        try:
            res = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
            )
            usage = res.usage
            log = {
                "model": model,
                "input_tokens": getattr(usage, "prompt_tokens", None),
                "output_tokens": getattr(usage, "completion_tokens", None),
                "duration_ms": int((time.monotonic() - start) * 1000),
                "attempt": attempt,
            }
            return res.choices[0].message.content, log
        except APITimeoutError:
            if attempt >= max_retries:
                raise
        except APIStatusError as e:
            if e.status_code not in RETRYABLE_STATUS or attempt >= max_retries:
                raise
        attempt += 1
        time.sleep((2 ** attempt) + random.uniform(0, 1))