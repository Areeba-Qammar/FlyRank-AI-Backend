# BE-07 - Put an LLM behind your API

## What this does

`POST /enrich` takes a short piece of scraped text (a headline, a snippet, a blurb)
and returns a category, a one-sentence summary, and a list of quality flags (like
spam or low content). It replaces a step where a person would normally read each
scraped record and tag it by hand.

## Try it

```bash
curl -X POST http://127.0.0.1:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{"text": "Apple unveiled its new M5 chip today, boasting a 40% performance increase over the M4."}'
```

Response:
```json
{
  "category": "tech",
  "summary": "Apple introduced its new M5 chip today.",
  "quality_flags": ["ok"]
}
```

A request with a missing or invalid field (like `{}`) returns FastAPI's default
`422` naming the field that's wrong. It's rejected before any model call happens.

## Job card

**What it does:** Classifies and summarizes a scraped text record.

**Input:**
```json
{ "text": "string, 1-5000 characters" }
```

**Output:**
```json
{
  "category": one of [tech|business|health|lifestyle|other],
  "summary": "one sentence, max 300 characters",
  "quality_flags": array of zero or more of [duplicate|low_content|spam|ok]
}
```

**It must never:** invent a category outside the list, return more than one sentence
in `summary`, add extra fields, return raw/unstructured text to the caller.

**When unsure:** use category `other`; if the text is too short or garbled to
summarize meaningfully, include `low_content` rather than guessing.

## Provider

- **Provider:** OpenRouter (free tier)
- **Model:** `openrouter/free`
- **Env vars:**
  ```
  LLM_BASE_URL=https://openrouter.ai/api/v1
  LLM_API_KEY=<your key>
  LLM_MODEL=openrouter/free
  ```
  Switching to a different OpenAI-compatible provider (Ollama, direct OpenAI) only
  means changing these three values. Nothing else in the code needs to know which
  provider it's talking to.

## Eval results

**7/8 correct** — prompt version `enrich-v1` — Aug 29, 2026 — model `openrouter/free`

Two different cases were flagged as failures across two eval runs, both genuinely
ambiguous rather than model mistakes:
- `"Q3"` was once classified as `business` instead of the expected `other`. "Q3"
  alone can reasonably be read as a fiscal-quarter reference, so this is a fair
  call by the model, not an error.
- `"Local bakery wins award for best sourdough three years running."` was
  classified as `business` instead of the expected `lifestyle`. This one is also
  defensible: an award win involving a local business does touch on both
  categories, and the line between "lifestyle" and "local business news" is
  genuinely blurry.

Both point the same direction: `lifestyle` vs `business` and `other` vs `business`
are soft boundaries in this category set, worth tightening with a few more
examples in the prompt in a future round.

Run it yourself: `python evals/run_eval.py` (server running, `LLM_STUB` unset).

## Cost

`openrouter/free` doesn't charge per token, so every call here costs **$0**, no
matter how many requests are sent. The real constraint isn't price, it's the rate
cap: 20 requests per minute and 50 per day, and failed requests count against that
limit too.

An earlier version of this project briefly ran on the paid `openai/gpt-4o-mini`
model by mistake (a leftover `.env` value from testing), which cost a total of
$0.002 before being caught and switched back to `openrouter/free`. At GPT-4o-mini's
pricing (~$0.15 per million input tokens, $0.60 per million output tokens), 10,000
requests a day at this endpoint's typical token size would run roughly $0.75-0.80 a
day. On the actual free tier used here, that same volume costs $0, capped instead
by the daily request limit rather than by price.

## Design notes

- **Stage 2** (the raw-text prompt with no parsing) wasn't kept as its own separate
  step. Stage 3's parse, validate, and repair logic replaced it right away, so the
  prompt file and the full pipeline ended up committed together.
- **Retries:** the SDK's built-in retry behavior is turned off (`max_retries=0`).
  Retries are handled by hand in `client.py` instead: 2 attempts, with backoff and a
  bit of random jitter added, and only for timeouts, `429`, and `5xx` errors. A
  `401` (bad key) fails right away with no retry, since retrying a bad key just
  wastes quota for no reason.
- **Quarantine check:** rather than trying to trick the live free model into
  returning an invalid category on demand (which it kept avoiding, even after I
  removed a category from the schema), I tested the parse, validate, and quarantine
  path directly with a unit test that feeds it a known-bad response. That's a more
  honest way to prove the mechanism works than chasing a live failure that may
  never happen on its own.

## What I'd fix with another day

I'd tighten the prompt's category boundaries, especially between `lifestyle`,
`business`, and `other`, since two different ambiguous eval cases both drifted
toward `business`. I'd add a few more borderline examples to the prompt itself to
see if that steadies the pattern, and run the eval against a second free model to
compare scores.