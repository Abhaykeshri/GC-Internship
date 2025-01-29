import asyncio
import time
import pandas as pd
from playwright.async_api import async_playwright


class CustomGoogleScraper:
    def __init__(self, query: str, scrolls: int = 3, headless: bool = True):
        """
        Initializes the CustomGoogleScraper with search query, number of scrolls, and headless option.
        """
        self.query = query
        self.scrolls = scrolls
        self.headless = headless
        self.results = []

        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=self.headless)
            self.page = await self.browser.new_page()

    async def load_results(self):
        """
        Loads Google search results page and scrolls down to load more results.
        """
        await self.page.goto(f"https://www.google.com/search?q={self.query}")
        print("[INFO]: Google search page loaded.")

        for i in range(self.scrolls):
            await self.page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)"
            )
            time.sleep(3)  # Allow results to load
            print(f"[INFO]: Completed scroll {i + 1}/{self.scrolls}.")

    async def scrape_results(self):
        """
        Scrapes the search results from the loaded page.
        """
        elements = await self.page.query_selector_all("div.MjjYud")
        print(f"[INFO]: Found {len(elements)} results to scrape.")

        for element in elements:
            try:
                title = await element.query_selector("h3")
                title = await title.text_content() if title else "No Title"
                url = await element.query_selector("a")
                url = await url.get_attribute("href") if url else "No URL"
                description = await element.query_selector("div.VwiC3b")
                description = await description.text_content(
                ) if description else "No Description"
                self.results.append({
                    "Title": title,
                    "URL": url,
                    "Description": description
                })
            except Exception as e:
                print(f"[WARNING]: Skipping an element due to error: {e}")

    async def save_results(self, file_name: str = "google_results.csv"):
        """
        Saves the scraped results to a CSV file.
        """
        if not self.results:
            print("[INFO]: No results to save.")
            return

        df = pd.DataFrame(self.results)
        df.to_csv(file_name, index=False)
        print(f"[INFO]: Results successfully saved to {file_name}.")

    async def close(self):
        """
        Closes the browser.
        """
        await self.browser.close()

    async def run(self):
        """
        Runs the scraper.
        """
        try:
            await self.load_results()
            await self.scrape_results()
            await self.save_results()
        except Exception as e:
            print(f"[ERROR]: An unexpected error occurred: {e}")
        finally:
            await self.close()


if __name__ == "__main__":
    print("[INFO]: Welcome to the Custom Google Scraper!")
    user_query = input("Enter your search query: ")
    user_scrolls = int(
        input("How many scrolls do you want to perform? (Recommended: 3): "))

    print(
        "\n[INFO]: Starting the scraper. Please ensure responsible usage of this tool.\n"
    )

    scraper = CustomGoogleScraper(query=user_query,
                                  scrolls=user_scrolls,
                                  headless=False)
    asyncio.run(scraper.run())

    print("\n[INFO]: Task completed. Results saved successfully.")