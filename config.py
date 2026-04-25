import random

BASE_URL = "https://github.com/trending"
OUTPUT_FILE = "github_trending.csv"

MAX_PAGES = 3
TIME_FILTERS = ["daily", "weekly", "monthly"]

PAGE_LOAD_DELAY = 2
REPO_SCRAPE_DELAY = 1.0  # Increased for politeness
PAGINATION_DELAY = 3

MAX_RETRIES = 3
RETRY_DELAY = 2

LOG_LEVEL = "INFO"
LOG_FILE = "scraper.log"

REQUIRED_FIELDS = [
    "title",
    "seller",
    "stars",
    "forks",
    "language",
    "last_updated",
    "license",
    "url",
    "description"
]

XPATHS = {
    "repos_container": '//article[@class="Box-row"]',
    "title": './/h2',
    "link": './/h2/a',
    "language": './/span[@itemprop="programmingLanguage"]',
    "stars": './/a[contains(@href,"stargazers")]',
    
    # Detail Page XPaths (Direct IDs are often most stable)
    "detail_description": '//div[@id="repo-content-pjax-container"]//p[contains(@class, "f4")]',
    "detail_forks": '//*[@id="repo-network-counter"]',
    "detail_watchers": '//*[@id="repo-notifications-counter"]',
    "detail_last_updated": '//relative-time',
    "detail_license": '//div[contains(@class, "BorderGrid-cell")]//a[contains(@href, "license") or contains(., "license")]'
}

# Browser Settings
HEADLESS = True
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)