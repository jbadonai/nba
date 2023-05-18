import os
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as playwrightTimeout
import time

# important!
# playwright install (run in command prompt. which configures all playwright web browser)

SEASONS = list(range(2016,2023))
DATA_DIR = 'data'
STANDING_DIR = os.path.join(DATA_DIR, "standings")
SCORES_DIR = os.path.join(DATA_DIR, "scores")


async def get_html(url, selector, sleep=5, retires=3):
    html = None
    for i in range(1 , retires + 1):
        time.sleep(sleep * 1)
        try:
            async  with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await  browser.new_page()
                await  page.goto(url)
                print(await page.title())
                html = await page.inner_html(selector)
        except playwrightTimeout:
            print(f"Timeout Error on {url}")
            continue
        else:
            break
    return html


async def scrape_season(season):
    url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html"
    html = await get_html(url, "#content .filter")  # id - content and in that div look for class filter

    soup = BeautifulSoup(html)
    links = soup.findAll("a")
    href = [l["href"] for l in links]
    standings_pages = [f"https://basketball-reference.com{l}" for l in href]
    for url in standings_pages:
        save_path = os.path.join(STANDING_DIR, url.split("/")[-1])

        if os.path.exists(save_path):
            # if we've already scape this, dont do it again just continue.
            continue

        html = await get_html(url, "#all_schedule")
        with open(save_path, "w+") as f:
            f.write(html)

for season in SEASONS:
    await scrape_season(season)


async def scrape_game(standings_file):
    # standings_files = os.listdir(STANDING_DIR)
    # standings_file = os.path.join(STANDING_DIR, standings_files[0])
    with open(standings_file, 'r') as f:
        html = f.read()

    soup = BeautifulSoup(html)
    links = soup.findAll("a")
    hrefs = [l.get('href') for l in links]
    box_scores = [l for l in hrefs if l and "boxscore" and ".html" in l]
    box_scores = [f"https://www.basketball-reference.com{l}" for l in box_scores]

    for url in box_scores:
        save_path = os.path.join(SCORES_DIR, url.split("/")[-1])
        if os.path.exists(save_path):
            continue

        html = await get_html(url, "#content")
        if not html:
            continue

        with open(save_path, "w+") as f:
            f.write(html)


standings_files = os.listdir(STANDING_DIR)
standings_files = [s for s in standings_files if ".html" in s]
for f in standings_files:
    filepath = os.path.join(STANDING_DIR, f)

    await scrape_game(filepath)

