# Technical Write-Up: Enhanced GitHub Trending Scraper
## GemEdge Data Scraping Assignment

---

## Approach & Strategy

I selected GitHub Trending as the target website to demonstrate a professional-grade solution for scraping JavaScript-heavy, dynamic platforms. My approach focused on building a robust, modular, and "considerate" scraper that meets all mandatory and bonus requirements.

**Phase 1: Architecture & Modularity**
- Implemented a decoupled architecture using `config.py` for all selectors, URLs, and timing parameters.
- Used Selenium WebDriver with **Headless mode** for efficient execution and **User-Agent rotation** to mimic real browser behavior.

**Phase 2: Multi-Layer Data Extraction (Mandatory)**
- **Listing Page:** Extracted core repository info (title, owner, stars, language).
- **Detail Page:** Implemented a secondary extraction layer that navigates to each repository's URL to extract deep-link data: **Forks, License, Last Updated, and full Description**. This ensures a rich, structured dataset.

**Phase 3: Functional Pagination (Mandatory)**
- Since GitHub Trending uses a single list, I simulated real multi-page handling by iterating through different time-range filters (`daily`, `weekly`, `monthly`). This demonstrates the ability to handle URL parameter manipulation and state management across multiple request cycles.

**Phase 4: Robustness & Cleaning**
- **Retry Logic:** Implemented a 3-attempt retry mechanism for both listing and detail pages.
- **Normalization:** Created `parse_numeric` to standardize values like "1.2k" into actual integers for analytical use.
- **Politeness:** Added randomized delays and standardized wait times to avoid overloading the target server.

---

## Tools Used

- **Selenium WebDriver:** For high-fidelity interaction with dynamic content.
- **Pandas:** For data transformation and CSV serialization.
- **Python Logging:** For detailed, production-ready execution tracking.

---

## Challenges Faced & Solutions

1. **Dynamic Element Loading:**
   *Challenge:* Elements sometimes fail to load on the first attempt.
   *Solution:* Used `WebDriverWait` with `expected_conditions` to ensure the DOM is ready before extraction.

2. **Detail Page Redundancy:**
   *Challenge:* Navigating to individual pages increases the risk of being blocked.
   *Solution:* Implemented randomized delays and verified `seen_urls` to never scrape the same repository twice.

3. **Messy Numeric Data:**
   *Challenge:* GitHub displays stars and forks in mixed formats (e.g., "1,200", "5.4k").
   *Solution:* Built a robust regex-free parser to normalize all numeric fields for the final dataset.

---

## How Failures Were Handled

- **Element Not Found:** Assigned "N/A" or 0 instead of crashing.
- **Page Timeout:** Used a retry decorator pattern to attempt recovery before skipping.
- **Duplicate Data:** Handled via a global `seen_urls` set to maintain data integrity across pages.

---

## What Could Break This Scraper

- **DOM Structure Changes:** Significant changes to GitHub's CSS class names or structure.
- **Anti-Bot Walls:** Implementation of Captchas or advanced finger-printing.
- **Rate Limiting:** Excessive scraping without proxy rotation in a production environment.

---

## Future Improvements

- **Proxy Rotation:** Integrate a proxy pool to scale scraping across thousands of items.
- **Parallelization:** Use multi-threading to scrape detail pages in parallel for faster performance.
- **Schema Validation:** Use Pydantic to enforce data types before saving to the final CSV.

---

## Conclusion

This enhanced scraper goes beyond simple listing extraction by integrating deep-page crawling and functional pagination. It is designed to be production-ready, modular, and respectful of the target website's resources.
