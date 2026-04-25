"""
GitHub Trending Scraper
Scrapes trending repositories with pagination, detail page extraction, and error handling
"""

import time
import logging
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import config

# Track seen URLs to prevent duplicates during scraping
seen_urls = set()

# Setup Logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global data storage
scraped_data = []
driver = None


def init_driver():
    """Initialize Selenium WebDriver with Chrome options and automatic driver management"""
    global driver
    try:
        options = Options()
        if config.HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument(f"user-agent={config.get_random_user_agent()}")
        
        # Use ChromeDriverManager for automatic driver management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        logger.info(f"WebDriver initialized successfully (Headless: {config.HEADLESS})")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        raise


def parse_numeric(text):
    """
    Convert numeric string to integer (e.g., '1.2k' -> 1200)
    """
    try:
        if not text or text.strip() == "":
            return 0
            
        text = text.replace(",", "").strip()
        
        if "k" in text.lower():
            return int(float(text.lower().replace("k", "")) * 1000)
        elif "m" in text.lower():
            return int(float(text.lower().replace("m", "")) * 1000000)
        
        return int(float(text))
    except Exception as e:
        logger.debug(f"Could not parse numeric value: '{text}', error: {e}")
        return 0


def scrape_detail_page(repo_url):
    """
    Visit a repository's detail page and extract more specific information
    Requirement: Extract data from both listing pages and detail pages
    """
    detail_info = {
        "forks": 0,
        "last_updated": "Unknown",
        "license": "None",
        "description": "N/A"
    }
    
    if not repo_url or repo_url == "N/A":
        return detail_info
        
    try:
        logger.debug(f"    Navigating to detail: {repo_url}")
        driver.get(repo_url)
        time.sleep(1)  # Brief wait for detail page load
        
        # Extract Forks
        try:
            forks_elem = driver.find_element(By.XPATH, config.XPATHS["detail_forks"])
            detail_info["forks"] = parse_numeric(forks_elem.text.strip())
        except NoSuchElementException:
            pass
            
        # Extract Last Updated
        try:
            update_elem = driver.find_element(By.XPATH, config.XPATHS["detail_last_updated"])
            detail_info["last_updated"] = update_elem.get_attribute("datetime") or update_elem.text.strip()
        except NoSuchElementException:
            pass
            
        # Extract License
        try:
            license_elem = driver.find_element(By.XPATH, config.XPATHS["detail_license"])
            detail_info["license"] = license_elem.text.strip()
        except NoSuchElementException:
            pass
            
        # Extract Description (if not already extracted)
        try:
            desc_elem = driver.find_element(By.XPATH, config.XPATHS["detail_description"])
            detail_info["description"] = desc_elem.text.strip()
        except NoSuchElementException:
            pass
            
        return detail_info
        
    except Exception as e:
        logger.warning(f"    Failed to scrape detail page {repo_url}: {e}")
        return detail_info


def scrape_page(page_url, page_num):
    """
    Scrape a single trending page
    Extracts repository information from listing page
    Collects all data first to avoid stale element issues
    """
    try:
        logger.info(f"Scraping page {page_num}: {page_url}")
        driver.get(page_url)
        
        # Wait for JS to render
        time.sleep(config.PAGE_LOAD_DELAY)
        
        # Wait for repos to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, config.XPATHS["repos_container"]))
            )
        except TimeoutException:
            logger.error(f"Timeout waiting for repos on page {page_num}")
            return 0
        
        repos = driver.find_elements(By.XPATH, config.XPATHS["repos_container"])
        logger.info(f"Found {len(repos)} repositories on page {page_num}")
        
        # Step 1: Extract all data from listing page FIRST (avoid stale element references)
        repos_data = []
        for idx, repo in enumerate(repos):
            try:
                repo_info = {}
                
                # Extract title (owner/repo name)
                try:
                    title_element = repo.find_element(By.XPATH, config.XPATHS["title"])
                    repo_info["title"] = title_element.text.strip()
                except NoSuchElementException:
                    continue  # Skip if no title
                
                # Extract repository link
                try:
                    link_element = repo.find_element(By.XPATH, config.XPATHS["link"])
                    repo_url = link_element.get_attribute("href")
                    if repo_url and not repo_url.startswith("http"):
                        repo_url = "https://github.com" + repo_url
                    repo_info["url"] = repo_url or "N/A"
                except NoSuchElementException:
                    repo_info["url"] = "N/A"
                
                # Extract seller (owner)
                repo_info["seller"] = repo_info["title"].split("/")[0].strip() if "/" in repo_info["title"] else "Unknown"
                
                # Extract language (category)
                try:
                    repo_info["language"] = repo.find_element(By.XPATH, config.XPATHS["language"]).text.strip()
                except NoSuchElementException:
                    repo_info["language"] = "Unknown"
                
                # Extract stars
                try:
                    stars_element = repo.find_element(By.XPATH, config.XPATHS["stars"])
                    repo_info["stars"] = parse_numeric(stars_element.text.strip())
                except NoSuchElementException:
                    repo_info["stars"] = 0
                
                # Prevent duplicate repositories (same URL)
                if repo_info["url"] in seen_urls:
                    logger.debug(f"Skipping duplicate: {repo_info['title']}")
                    continue
                
                seen_urls.add(repo_info["url"])
                repos_data.append(repo_info)
            
            except Exception as e:
                logger.warning(f"Error extracting repo {idx} on page {page_num}: {e}")
                continue
        
        # Step 2: Visit Detail Pages for EACH repo
        repos_scraped = 0
        for repo_info in repos_data:
            try:
                # Visit detail page
                detail_data = scrape_detail_page(repo_info["url"])
                repo_info.update(detail_data)
                
                # Add to final data
                scraped_data.append(repo_info)
                
                repos_scraped += 1
                logger.info(f"  ✓ Fully Scraped: {repo_info.get('title', 'Unknown')}")
                time.sleep(config.REPO_SCRAPE_DELAY)
            
            except Exception as e:
                logger.error(f"Error processing detail for {repo_info.get('title', 'Unknown')}: {e}")
                # Still add basic info if detail fails
                scraped_data.append(repo_info)
                repos_scraped += 1
                continue
        
        return repos_scraped
    
    except Exception as e:
        logger.error(f"Error scraping page {page_num}: {e}")
        return 0


def scrape_with_pagination():
    """
    Main scraping function with pagination support
    Handles multiple pages with retry logic
    """
    try:
        total_repos = 0
        
        for idx, time_filter in enumerate(config.TIME_FILTERS):
            page_num = idx + 1
            retries = 0
            while retries < config.MAX_RETRIES:
                try:
                    # Construct page URL using real time filters as "pages"
                    page_url = f"{config.BASE_URL}?since={time_filter}"
                    
                    repos_count = scrape_page(page_url, page_num)
                    total_repos += repos_count
                    
                    break  # Success, move to next page
                
                except Exception as e:
                    retries += 1
                    logger.warning(f"Retry {retries}/{config.MAX_RETRIES} for page {page_num}: {e}")
                    if retries < config.MAX_RETRIES:
                        time.sleep(config.RETRY_DELAY)
                    else:
                        logger.error(f"Failed to scrape page {page_num} after {config.MAX_RETRIES} retries")
            
            # Wait between page requests
            if page_num < config.MAX_PAGES:
                time.sleep(config.PAGINATION_DELAY)
        
        logger.info(f"Scraping completed! Total repositories scraped: {total_repos}")
        return total_repos
    
    except Exception as e:
        logger.error(f"Critical error during pagination: {e}")
        return 0


def save_data(filename=None):
    """
    Save scraped data to CSV file
    Handles data cleaning and formatting
    """
    try:
        if not filename:
            filename = config.OUTPUT_FILE
        
        if not scraped_data:
            logger.warning("No data to save!")
            return False
        
        df = pd.DataFrame(scraped_data)
        
        # Remove duplicates (defensive: also handled during scraping)
        df = df.drop_duplicates(subset=["url"], keep="first")
        
        # Ensure required columns exist
        for field in config.REQUIRED_FIELDS:
            if field not in df.columns:
                df[field] = "N/A"
        
        # Reorder columns
        df = df[config.REQUIRED_FIELDS]
        
        # Save to CSV
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        logger.info(f"Data saved to {filename} ({len(df)} rows)")
        
        # Print summary
        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        print(f"Total repositories: {len(df)}")
        print(f"Average stars: {df['stars'].mean():.0f}" if 'stars' in df.columns else "N/A")
        print(f"Top language: {df['language'].mode().values[0] if len(df) > 0 and 'language' in df.columns else 'N/A'}")
        print(f"Output file: {filename}")
        print("="*60 + "\n")
        
        return True
    
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False


def main():
    """Main execution function"""
    logger.info("="*60)
    logger.info("GitHub Trending Repository Scraper Started")
    logger.info("="*60)
    
    try:
        # Initialize driver
        init_driver()
        
        # Scrape with pagination
        scrape_with_pagination()
        
        # Save data
        save_data()
        
        logger.info("Scraping process completed successfully!")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriver closed")


if __name__ == "__main__":
    main()