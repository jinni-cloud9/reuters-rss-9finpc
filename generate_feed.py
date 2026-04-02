from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator

OUTPUT_FILE = "reuters_filtered.xml"

def build_feed():
    fg = FeedGenerator()
    fg.title("Reuters link test")
    fg.link(href="https://www.reuters.com/")
    fg.description("Reuters link test")
    fg.language("en")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.reuters.com/business/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        links = page.locator("a").evaluate_all(
            """els => els.map(a => a.href).filter(Boolean)"""
        )

        count = 0
        seen = set()

        for href in links:
            href = href.split("?")[0]
            if not href.startswith("https://www.reuters.com/"):
                continue
            if href in seen:
                continue
            seen.add(href)

            fe = fg.add_entry()
            fe.id(href)
            fe.title(href)
            fe.link(href=href)
            fe.description("Discovered Reuters link")
            count += 1

            if count >= 10:
                break

        browser.close()

    fg.rss_file(OUTPUT_FILE)

if __name__ == "__main__":
    build_feed()
    print("Wrote reuters_filtered.xml")
