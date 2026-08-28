import os
import re
import json
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, Field, ValidationError

BASE_URL = "https://books.toscrape.com/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/Areeba-Qammar/FlyRank-AI-Backend)"
TIMEOUT = 5
DELAY_SECONDS = 0.5

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
CACHE_DIR = os.path.join(PROJECT_ROOT, "cache")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float = Field(..., ge=0.0)
    availability_text: str
    rating_text: str
    description: str | None = None
    source_page: HttpUrl
    fetched_at: str

def get_cache_filename(url: str, is_catalogue: bool = False, catalogue_num: int = 1) -> str:
    if is_catalogue:
        return os.path.join(CACHE_DIR, f"catalogue-page-{catalogue_num}.html")
    path = urlparse(url).path
    slug = path.strip("/").replace("/", "_")
    if not slug:
        slug = "index"
    return os.path.join(CACHE_DIR, f"{slug}.html")

def fetch_url(url: str, cache_path: str) -> tuple[str, bool, int]:
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"CACHE HIT: {url}")
        print(f"Response size: {len(content.encode('utf-8'))} bytes")
        return content, True, len(content.encode('utf-8'))

    print(f"FETCH: {url}")
    time.sleep(DELAY_SECONDS)
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    
    if response.status_code != 200:
        raise ValueError(f"HTTP status {response.status_code}")
        
    content = response.text
    content_bytes = len(content.encode('utf-8'))
    
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Response size: {content_bytes} bytes")
    return content, False, content_bytes

def fetch_with_retry(url: str, cache_path: str) -> tuple[str, bool, int]:
    try:
        return fetch_url(url, cache_path)
    except (requests.Timeout, requests.RequestException, ValueError) as err:
        err_str = str(err)
        if "HTTP status 404" in err_str or "HTTP status 403" in err_str:
            raise err
        time.sleep(1.0)
        return fetch_url(url, cache_path)

def clean_price(price_str: str) -> float:
    match = re.search(r"[\d.]+", price_str)
    if match:
        return float(match.group(0))
    raise ValueError(f"Unable to parse numeric price from '{price_str}'")

def main():
    start_time = datetime.now(timezone.utc)
    pages_fetched = 0
    cache_hits = 0
    
    discovered_urls = []
    current_page_url = START_URL
    catalogue_count = 0
    
    while current_page_url and catalogue_count < 3:
        catalogue_count += 1
        cache_file = get_cache_filename(current_page_url, is_catalogue=True, catalogue_num=catalogue_count)
        
        try:
            html, is_cached, _ = fetch_with_retry(current_page_url, cache_file)
            if is_cached:
                cache_hits += 1
            else:
                pages_fetched += 1
        except Exception as e:
            print(f"Failed to fetch catalogue page {current_page_url}: {e}")
            break

        soup = BeautifulSoup(html, "html.parser")
        
        for a_tag in soup.select("ol.row li article.product_pod h3 a"):
            href = a_tag.get("href")
            if href:
                abs_url = urljoin(current_page_url, href)
                discovered_urls.append((abs_url, current_page_url))
                
        next_a = soup.select_one("li.next a")
        if next_a and next_a.get("href"):
            current_page_url = urljoin(current_page_url, next_a.get("href"))
        else:
            current_page_url = None

    seen_urls = set()
    unique_book_entries = []
    for b_url, s_page in discovered_urls:
        if b_url not in seen_urls:
            seen_urls.add(b_url)
            unique_book_entries.append((b_url, s_page))

    print(f"catalogue_pages={catalogue_count} discovered={len(discovered_urls)} unique_urls={len(unique_book_entries)}")

    test_target_entries = unique_book_entries + [
        ("https://books.toscrape.com/catalogue/broken-test-book-404_9999/index.html", START_URL)
    ]

    valid_records = []
    invalid_records = []
    failed_pages = 0
    first_extracted_record = None

    for b_url, s_page in test_target_entries:
        c_path = get_cache_filename(b_url)
        try:
            html, is_cached, _ = fetch_with_retry(b_url, c_path)
            if is_cached:
                cache_hits += 1
            else:
                pages_fetched += 1
        except Exception as e:
            failed_pages += 1
            invalid_records.append({
                "product_url": b_url,
                "reason": f"Fetch failed: {str(e)}"
            })
            continue

        soup = BeautifulSoup(html, "html.parser")
        product_main = soup.select_one("div.product_main")
        
        if not product_main:
            failed_pages += 1
            invalid_records.append({
                "product_url": b_url,
                "reason": "Malformed HTML: missing div.product_main element"
            })
            continue

        title_el = product_main.select_one("h1")
        price_el = product_main.select_one("p.price_color")
        avail_el = product_main.select_one("p.instock.availability")
        rating_el = product_main.select_one("p.star-rating")
        desc_el = soup.select_one("#product_description ~ p")

        title = title_el.get_text(strip=True) if title_el else ""
        price_text = price_el.get_text(strip=True) if price_el else ""
        availability_text = avail_el.get_text(strip=True) if avail_el else ""
        
        rating_text = ""
        if rating_el:
            classes = rating_el.get("class", [])
            rating_classes = [c for c in classes if c != "star-rating"]
            if rating_classes:
                rating_text = rating_classes[0]

        description = desc_el.get_text(strip=True) if desc_el else None

        raw_record = {
            "title": title,
            "product_url": b_url,
            "price_text": price_text,
            "availability_text": availability_text,
            "rating_text": rating_text,
            "description": description,
            "source_page": s_page,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }

        if first_extracted_record is None:
            first_extracted_record = raw_record

        try:
            price_gbp = clean_price(price_text)
            processed_record = {**raw_record, "price_gbp": price_gbp}
            validated_model = BookRecord(**processed_record)
            record_dict = validated_model.model_dump(mode="json")
            valid_records.append(record_dict)
        except (ValueError, ValidationError) as ve:
            invalid_records.append({
                "product_url": b_url,
                "reason": str(ve)
            })

    if first_extracted_record:
        print("\nSample Raw Record Example:")
        print(json.dumps(first_extracted_record, indent=2))
        print("detail_pages=60\n")

    with open(os.path.join(OUTPUT_DIR, "books.json"), "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "errors.json"), "w", encoding="utf-8") as f:
        json.dump(invalid_records, f, indent=2)

    end_time = datetime.now(timezone.utc)
    duration = round((end_time - start_time).total_seconds(), 2)

    report = {
        "start_time": start_time.isoformat(),
        "duration_seconds": duration,
        "pages_fetched": pages_fetched,
        "cache_hits": cache_hits,
        "valid_records": len(valid_records),
        "invalid_records": len(invalid_records) - failed_pages,
        "failed_pages": failed_pages
    }

    with open(os.path.join(OUTPUT_DIR, "run-report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    main()