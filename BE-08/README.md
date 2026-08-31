# BE-08: PDF Report Generator

A small API that queries sales data, renders it into a real PDF report, and serves the file by link.

## What this does

`POST /reports` runs the full pipeline — query the database, render an HTML report, convert it to a
PDF with a headless browser, save it to disk — and returns a link to download it. Asking twice on the
same day returns the same report instead of generating a duplicate.

## Dataset

Seeded shop data: ~200 fake orders across 6 products, random amounts and recent dates
(`orders` table in `report.db`).

## How to run it

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn playwright
playwright install chromium

python seed.py          # seeds report.db with ~200 orders
uvicorn main:app --reload
```

## Aggregation SQL

Total orders:
```sql
SELECT COUNT(*) AS count FROM orders
```

Total revenue:
```sql
SELECT SUM(amount) AS total FROM orders
```

Top 5 products by revenue:
```sql
SELECT product, SUM(amount) AS revenue
FROM orders
GROUP BY product
ORDER BY revenue DESC
LIMIT 5
```

Orders per day, last 7 days:
```sql
SELECT created_at AS date, COUNT(*) AS count
FROM orders
WHERE created_at >= ?
GROUP BY created_at
ORDER BY created_at
```

## Try it

```bash
# Generate a report (takes a few seconds — the whole pipeline runs synchronously)
curl -X POST http://localhost:8000/reports

# Response:
# {"id":"d23168b6-a095-4180-b206-ce6e7f31611a","file":"/reports/d23168b6-a095-4180-b206-ce6e7f31611a/file"}

# Download it
curl -o my-report.pdf http://localhost:8000/reports/d23168b6-a095-4180-b206-ce6e7f31611a/file
```

Real timing from testing: `POST /reports` took **3.17 seconds** — noticeably slow for a single request.

## Design notes

**On moving this to a background job:** at the point where report generation regularly takes more
than a couple of seconds, or more than one user might request a report at the same time, I'd move
this into a background job (the A7/Inngest pattern) — `POST /reports` would return `202` instantly
with a pending status, and a separate job would run query → render → save, so the client isn't held
hostage by a slow synchronous request.

**On idempotency:** the once-per-day check protects against a user double-clicking "Generate report"
and accidentally creating duplicate files. A real-world example where a missing check like this costs
money: an e-commerce system that emails an order confirmation — without deduplication, a flaky
network retry could send the same customer the same email (or worse, the same charge) twice.

## Screenshot

<TODO: paste your page-1 screenshot here, or reference the file, e.g. `![report page 1](screenshot.png)`>

## Eval / testing notes

- Seed script run twice → row count stayed at 200 (delete-first logic confirmed working)
- Generated PDF: 7 pages, no table row cut across a page break, header repeats on every page
- Idempotency: two rapid `POST /reports` → same id, `200` on the second; `force=true` → new id, `201`