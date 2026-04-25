# GitHub Trending Scraper

## Overview
A Selenium-based Python scraper designed to extract data from GitHub's trending repositories. It handles dynamic content, simulates pagination via time-range filters, and performs deep-page extraction for comprehensive repository details.

## Features
- Dynamic Content: Uses Selenium to render JavaScript-heavy pages.
- Multi-Page Support: Iterates through daily, weekly, and monthly trending filters.
- Deep Extraction: Scrapes both listing pages and individual repository detail pages.
- Data Normalization: Converts numeric strings (e.g., "1.2k") into integers.
- Robustness: Implements a 3-attempt retry logic and comprehensive logging.

## Tech Stack
- Language: Python 3.8+
- Automation: Selenium WebDriver
- Data Management: Pandas
- Driver Management: Webdriver-manager (Automatic)

## Data Fields Extracted
- title: Repository name (owner/repo)
- seller: Repository owner
- stars: Total stargazers (normalized)
- forks: Total forks (normalized)
- language: Primary programming language
- last_updated: Timestamp of last commit
- url: Direct link to repository
- description: Project summary

## Setup and Installation

1. Install Dependencies:
```bash
pip install selenium pandas webdriver-manager
```

2. Configuration:
Modify `config.py` to adjust scraping delays, max pages, or XPATH selectors.

3. Run Scraper:
```bash
python main.py
```

## Project Structure
- main.py: Core scraping logic and pagination handling.
- config.py: Centralized configuration and selectors.
- github_trending.csv: Final extracted dataset.
- scraper.log: Detailed execution tracking.
- WRITEUP.md: Technical approach and challenges.

## Error Handling
The scraper uses explicit waits and try-except blocks to handle missing elements or network timeouts. If a page fails to load, it will retry up to 3 times before moving to the next item to ensure data continuity.