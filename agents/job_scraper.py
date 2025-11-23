# agents/job_scraper.py
"""Job Scraper Agent

This agent uses Playwright to fetch job listings from public job boards such as LinkedIn and Indeed.
It extracts basic fields: title, company, location, description, and posting URL.
The implementation below provides a minimal asynchronous stub that can be expanded later.
"""

import asyncio
from typing import List, Dict

from playwright.async_api import async_playwright


class JobScraper:
    """Scrape job postings from supported job boards.

    Supported boards (as of now):
        - "linkedin"
        - "indeed"
    """

    def __init__(self, max_pages: int = 1, results_per_page: int = 25, timeout: int = 30000):
        self.max_pages = max_pages
        self.results_per_page = results_per_page
        self.timeout = timeout

    async def _scrape_linkedin(self, query: str) -> List[Dict[str, str]]:
        """Scrape LinkedIn job search results for a given query.

        Returns a list of dictionaries with keys:
            title, company, location, description, url
        """
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # Construct LinkedIn job search URL
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location=Worldwide"
            await page.goto(search_url, timeout=self.timeout)
            await page.wait_for_load_state("networkidle")
            # Simple pagination loop (limited by max_pages)
            for page_num in range(1, self.max_pages + 1):
                job_cards = await page.query_selector_all("section[data-job-id]")
                for card in job_cards:
                    title_el = await card.query_selector("h3")
                    company_el = await card.query_selector("h4")
                    location_el = await card.query_selector("span.job-result-card__location")
                    link_el = await card.query_selector("a.result-card__full-card-link")
                    if not (title_el and company_el and location_el and link_el):
                        continue
                    title = (await title_el.inner_text()).strip()
                    company = (await company_el.inner_text()).strip()
                    location = (await location_el.inner_text()).strip()
                    url = await link_el.get_attribute("href")
                    # For description we would need to navigate to the job page – omitted for brevity
                    description = ""
                    results.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": description,
                        "url": url,
                    })
                # Attempt to go to next page if pagination exists
                next_button = await page.query_selector("button[aria-label='Next']")
                if next_button:
                    await next_button.click()
                    await page.wait_for_load_state("networkidle")
                else:
                    break
            await browser.close()
        return results

    async def _scrape_indeed(self, query: str) -> List[Dict[str, str]]:
        """Scrape Indeed job search results for a given query.

        Returns a list of dictionaries with keys:
            title, company, location, description, url
        """
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            search_url = f"https://www.indeed.com/jobs?q={query}&l=Worldwide"
            await page.goto(search_url, timeout=self.timeout)
            await page.wait_for_load_state("networkidle")
            for page_num in range(1, self.max_pages + 1):
                job_cards = await page.query_selector_all("div.jobsearch-SerpJobCard")
                for card in job_cards:
                    title_el = await card.query_selector("h2.title a")
                    company_el = await card.query_selector("span.company")
                    location_el = await card.query_selector("div.location, span.location")
                    if not (title_el and company_el and location_el):
                        continue
                    title = (await title_el.get_attribute("title")).strip()
                    company = (await company_el.inner_text()).strip()
                    location = (await location_el.inner_text()).strip()
                    url = f"https://www.indeed.com" + (await title_el.get_attribute("href"))
                    description = ""
                    results.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": description,
                        "url": url,
                    })
                next_button = await page.query_selector("a[aria-label='Next']")
                if next_button:
                    await next_button.click()
                    await page.wait_for_load_state("networkidle")
                else:
                    break
            await browser.close()
        return results

    async def scrape(self, board: str, query: str) -> List[Dict[str, str]]:
        """Public entry point to scrape a given job board.

        Parameters
        ----------
        board: str
            Name of the job board ("linkedin" or "indeed").
        query: str
            Search query, e.g., "senior software engineer".
        """
        board = board.lower()
        if board == "linkedin":
            return await self._scrape_linkedin(query)
        elif board == "indeed":
            return await self._scrape_indeed(query)
        else:
            raise ValueError(f"Unsupported job board: {board}")

# Example usage (for manual testing)
# if __name__ == "__main__":
#     scraper = JobScraper(max_pages=2)
#     results = asyncio.run(scraper.scrape("linkedin", "software engineer"))
#     for r in results:
#         print(r)
