"""Batch example — scrape multiple URLs in parallel."""

from dawg_baas import Scraper

urls = [
    "https://example.com",
    "https://httpbin.org/html",
    "https://jsonplaceholder.typicode.com",
]

with Scraper(api_key="your_api_key_here") as scraper:
    job = scraper.batch(urls, format="text", concurrency=3)
    print(f"Batch started: {job.job_id} ({len(urls)} URLs)")

    job.wait()

    print(f"\nCompleted in {job.elapsed_ms}ms:")
    for page in job.pages:
        if page.error:
            print(f"  FAIL {page.url}: {page.error}")
        else:
            title = page.metadata.get("title", "")
            print(f"  OK   {page.url} — {title} ({len(page.content)} chars)")
