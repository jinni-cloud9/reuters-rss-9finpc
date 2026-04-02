from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator

OUTPUT_FILE = "reuters_filtered.xml"

def build_feed():
    fg = FeedGenerator()
    fg.title("Reuters test feed")
    fg.link(href="https://www.reuters.com/")
    fg.description("Test Reuters feed")
    fg.language("en")

    fe = fg.add_entry()
    fe.id("https://www.reuters.com/")
    fe.title("Test item")
    fe.link(href="https://www.reuters.com/")
    fe.description("This is a test item")
    fg.rss_file(OUTPUT_FILE)

if __name__ == "__main__":
    build_feed()
    print("Wrote reuters_filtered.xml")
