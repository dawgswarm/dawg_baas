"""Crawl example — recursively scrape a website."""

from dawg_baas import Scraper

with Scraper(api_key="your_api_key_here") as scraper:
    # Start crawl — returns immediately
    job = scraper.crawl(
        "https://example.com",
        max_depth=2,
        max_pages=20,
        format="markdown",
        main_content=True,
    )
    print(f"Crawl started: {job.job_id}")

    # Wait for completion (polls every 2 seconds)
    job.wait()

    print(f"Status: {job.status}")
    print(f"Pages: {job.progress.get('completed')}/{job.progress.get('total')}")
    print(f"Time: {job.elapsed_ms}ms")

    for page in job.pages:
        title = page.metadata.get("title", "no title")
        print(f"  {page.url} — {title} ({len(page.content)} chars)")
