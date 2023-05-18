import os
import time
import asyncio
from playwright.async_api import async_playwright
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup


class NBA():
    def __init__(self):
        self.seasons_url = "https://www.basketball-reference.com/leagues/NBA_{}.html"    # {year}
        self.schedule_url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html"  # {year} and {month}

        self.SEASONS = list(range(2016,2023))
        self.DATA_DIR = 'data'
        self.STANDING_DIR = os.path.join(self.DATA_DIR, "standings")
        self.SCORES_DIR = os.path.join(self.DATA_DIR, "scores")

    def initial_check(self):
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)
        if not os.path.exists(self.STANDING_DIR):
            os.makedirs(self.STANDING_DIR)
        if not os.path.exists(self.SCORES_DIR):
            os.makedirs(self.SCORES_DIR)

    async def get_html(self, url, selector, sleep=5, retries=3):
        html = None
        for i in range(1, retries + 1):
            time.sleep(sleep * 1)
            try:
                async with async_playwright() as p:     # initialize playwright instance
                    browser = await p.chromium.launch()     # launch chrome browser. wait until it's launched (await)
                    page = await browser.new_page() # create a new tab on the browser
                    await page.goto(url)    # load url in the opened new tab
                    print(await page.title())
                    html = await page.inner_html(selector)  # not grabbing all html but just a section by selector
            except PlaywrightTimeout:
                print(f"Timeout Error on {url}")
                continue
            else:
                break
        return html

    async def start(self):
        self.initial_check()
        url = self.seasons_url.format(2016)
        html = await self.get_html(url, "#content .filter")
        print('html')
        print(html)
        soup = BeautifulSoup(html)
        links = soup.find_all("a")
        hrefs = [link['href'] for link in links]
        for ref in hrefs:
            print(ref)

async def main():
    x = NBA()
    await x.start()

asyncio.run(main())
