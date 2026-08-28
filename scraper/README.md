## Target Classification

**Target:** [Books to Scrape](https://books.toscrape.com)

**Why this site:** Books to Scrape describes itself as "a fictional bookstore that desperately wants to be scraped... a safe place for beginners learning web scraping." It's a sandbox built specifically for this purpose, not a live production site.

**Scope:** the first 3 catalogue pages only (60 unique books).

**Data collected:** title, price, availability, star rating, and description for each book — plus the source page URL and fetch timestamp for provenance.

**robots.txt check:** requested `https://books.toscrape.com/robots.txt` — got `404 Not Found`. No robots file found. A missing file is not permission on its own; permission here comes from the site's own "built to be scraped" description above.

I will not reuse this code on another site without checking its rules and terms first.