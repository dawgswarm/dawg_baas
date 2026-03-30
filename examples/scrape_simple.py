"""Simple scrape example — extract page content as markdown."""

from dawg_baas import Scraper

scraper = Scraper(api_key="your_api_key_here")

# Scrape a page and get clean markdown
result = scraper.scrape("https://example.com", format="markdown")

print(f"Title: {result.metadata.get('title')}")
print(f"Words: {result.metadata.get('word_count')}")
print(f"Content:\n{result.content}")

# With main_content=True to strip navigation, footers, ads
result = scraper.scrape(
    "https://news.ycombinator.com",
    format="text",
    main_content=True,
)
print(f"\nHN content ({result.elapsed_ms}ms):\n{result.content[:500]}")

scraper.close()
