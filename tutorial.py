import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import time
import os

"""
* pip install requests
* specify the year range you want to scrape:
    >>> year = range(1999,2003)
* define the url
    >>> url = "...."
    
* for each season, grab the link to each of the months in the schedule and then look through the lnks and get box scores
    get <a> tag and then href property
"""


class NBA():
    def __init__(self):
        self.seasons_url = "https://www.basketball-reference.com/leagues/NBA_{}.html"    # {year}
        self.schedule_url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html"  # {year} and {month}

        self.SEASONS = list(range(2016,2023))
        self.DATA_DIR = 'data'
        self.STANDING_DIR = os.path.join(self.DATA_DIR, "standings")
        self.SCORES_DIR = os.path.join(self.DATA_DIR, "scores")

    def initial_check(self):
        if os.path.exists(DATA_DIR) is False:
            os.makedirs(DATA_DIR)
        if os.path.exists(STANDING_DIR) is False:
            os.makedirs(STANDING_DIR)
        if os.path.exists(SCORES_DIR) is False:
            os.makedirs(SCORES_DIR)

    async def get_html(self,url, selector, sleep=5, retires=3):
        html = None
        for i in range(1, retires + 1):
            time.sleep(sleep * 1)
            try:
                async with async_playwright() as p:     # initialize playwright instance
                    browser = await p.chromium.launch()     # launch chrome browser. wait until it's launc(await)
                    page = await browser.new_page() # crate a new tab on the browser
                    await page.goto(url)    # load url in the the opened new tab
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
        html = await self.get_html(self.seasons_url, "#contents .filter")
        print(html)


x = NBA()

x.start()