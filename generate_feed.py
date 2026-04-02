from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator

OUTPUT_FILE = "reuters_filtered.xml"

def build_feed():
    fg = FeedGenerator()
    fg.title("Reuters feed test")
    fg.link(href="https://www.reuters.com/")
    fg.description("Reuters feed test")
    fg.language("en")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.reuters.com/business/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        title = page.title()

        fe = fg.add_entry()
        fe.id("https://www.reuters.com/business/")
        fe.title(title)
        fe.link(href="https://www.reuters.com/business/")
        fe.description("Business page title fetched by Playwright")

        browser.close()

    fg.rss_file(OUTPUT_FILE)

if __name__ == "__main__":
    build_feed()
    print("Wrote reuters_filtered.xml")
