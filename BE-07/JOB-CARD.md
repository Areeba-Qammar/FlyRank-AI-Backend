# Job Card: Enrich Scraped Records (`POST /enrich`)

## Interface
- **Input:** `{ "text": "string, scraped record content" }`
- **Output:** `{ "category": one of [tech|business|health|lifestyle|other], "summary": "one sentence", "quality_flags": ["duplicate"|"low_content"|"spam"|"ok"] }`

## Constraints
- **Must Never:** Invent a category outside the permitted list.
- **Must Never:** Return more than one sentence for the summary.
- **When Unsure:** Set `category = "other"` and include `"low_content"` in `quality_flags`.