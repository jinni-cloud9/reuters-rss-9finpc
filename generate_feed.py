from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

SOURCE_PAGES = [
    "https://www.reuters.com/tags/mergers-acquisitions/",
    "https://www.reuters.com/business/",
    "https://www.reuters.com/markets/",
]

KEYWORDS = [
    "merger", "acquisition", "buyout", "take-private", "take private", "m&a",
    "restructuring", "chapter 11", "bankruptcy", "distressed",
    "liability management", "debt exchange",
    "private credit", "direct lending", "private debt", "private lender", "non-bank lender",
]

OUTPUT_FILE = "reuters_filtered.xml"





def matches_keywords(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in KEYWORDS)





def is_reuters_article_url(url: str) -> bool:
    if not url.startswith("https://www.reuters.com/"):
        return False
    banned = [
        "/world/",
        "/business/",
        "/markets/",
        "/legal/",
        "/sustainability/",
        "/graphics/",
        "/pictures/",
        "/authors/",
        "/tags/",
    ]
    return "/article/" in url or "/companies/" in url or (
        url.count("/") >= 4 and not any(url.rstrip("/").endswith(x.rstrip("/")) for x in banned)
    )





def extract_links_from_listing(page):
    anchors = page.locator("a").evaluate_all(
        """els => els.map(a => a.href).filter(Boolean)"""
    )
    out = []
    seen = set()
    for href in anchors:
        href = href.split("?")[0]
        if href in seen:
            continue
        if is_reuters_article_url(href):
            seen.add(href)
            out.append(href)
    return out





def fetch_article_metadata(browser, url):
    page = browser.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        title = page.title() or url

        desc = ""
        meta = page.locator('meta[name="description"]').first
        if meta.count() > 0:
            desc = meta.get_attribute("content") or ""

        return {
            "url": url,
            "title": title.strip(),
            "description": desc.strip(),
        }
    except Exception as e:
        print(f"Failed article {url}: {e}")
        return None
    finally:
        page.close()





def build_feed():
    fg = FeedGenerator()
    fg.title("Reuters: M&A, Restructuring, Private Credit")
    fg.link(href="https://www.reuters.com/")
    fg.description("Filtered Reuters feed for M&A, restructuring, and private credit")
    fg.language("en")

    now = datetime.now(timezone.utc)
    seen_articles = set()
    matched_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for source_url in SOURCE_PAGES:
                print(f"Opening source page: {source_url}")
                page = browser.new_page()
                try:
                    page.goto(source_url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(5000)

                    links = extract_links_from_listing(page)
                    print(f"Found {len(links)} candidate links on {source_url}")

                    for url in links[:40]:
                        if url in seen_articles:
                            continue

                        item = fetch_article_metadata(browser, url)
                        if not item:
                            continue

                        blob = f"{item['title']} {item['description']}"
[12:47 PM]if not matches_keywords(blob):
                            continue

                        print(f"Matched: {item['title']}")

                        fe = fg.add_entry()
                        fe.id(item["url"])
                        fe.title(item["title"])
                        fe.link(href=item["url"])
                        fe.description(item["description"] or item["title"])
                        fe.pubDate(now)

                        seen_articles.add(item["url"])
                        matched_count += 1
                finally:
                    page.close()
        finally:
            browser.close()

    print(f"Total matched articles: {matched_count}")
    fg.rss_file(OUTPUT_FILE)





if __name__ == "__main__":
    build_feed()
    print(f"Wrote {OUTPUT_FILE}")
