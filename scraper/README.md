## How to run it

From inside `scraper/`:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

This fetches the first 3 catalogue pages, visits all 60 book pages, and writes `output/books.json`, `output/errors.json`, and `output/run-report.json`. Running it again reads from `cache/` instead of hitting the site a second time.

## Record schema

Each book in `books.json`:

- `title` — string
- `product_url` — the book's own page, also used as its unique ID
- `price_text` — price as shown on the page, e.g. `£51.77`
- `price_gbp` — the same price as a number, e.g. `51.77`
- `availability_text` — stock status as shown on the page
- `rating_text` — star rating word (One through Five)
- `description` — book description, or `null` if there isn't one
- `source_page` — which catalogue page it was found on
- `fetched_at` — when it was collected

## How it stays polite

- Every request sends a `User-Agent` naming this project and linking to the repo
- Requests time out after 5 seconds
- 0.5 second wait between real requests
- Every page is cached after the first fetch, so development doesn't keep hitting the site
- A timeout or server error gets retried once. A 404 or 403 never gets retried.

## Sample run

```json
{
  "start_time": "2026-08-29T11:26:57.091848+00:00",
  "duration_seconds": 162.74,
  "pages_fetched": 63,
  "cache_hits": 0,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}
```

`failed_pages: 1` is expected — the script includes one made-up book URL on purpose, to prove a broken page doesn't take down the run.

## Why no browser was needed

All the book data is already in the HTML the server sends back — nothing here is loaded in with JavaScript. A plain HTTP request gets everything a headless browser would, without the extra time and memory.

## Ethics note

This only ran against Books to Scrape, a site built specifically for scraping practice. For a real project, I'd check for an official API first, never try to get around a login or paywall, and only collect what's actually needed.

## Limitation

The extraction depends on the page's current HTML (`div.product_main`, `#product_description`). If the site's layout changed, the selectors would need updating — there's no fallback right now, a missing field just becomes `null` or fails validation.