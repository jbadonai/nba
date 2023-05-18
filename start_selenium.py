import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


class NBA():
    def __init__(self):
        self.seasons_url = "https://www.basketball-reference.com/leagues/NBA_{}.html"    # {year}
        # self.schedule_url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html"  # {year} and {month}
        self.schedule_url = "https://www.basketball-reference.com/leagues/NBA_{}_games.html"  # {year} and {month}

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

    def get_html(self, url, selector, sleep=5, retries=3):
        html = None
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        service = Service('chromedriver.exe')  # Specify the path to the chromedriver executable

        for i in range(1, retries + 1):
            time.sleep(sleep * 1)
            try:
                driver = webdriver.Chrome(service=service, options=options)
                driver.set_page_load_timeout(5)
                try:
                    driver.get(url)
                except Exception as e:
                    if str(e).__contains__("timeout"):
                        pass
                    else:
                        raise Exception

                print(driver.title)
                element = driver.find_element(By.CSS_SELECTOR, selector)
                html = element.get_attribute('innerHTML')
                driver.quit()
            except Exception as e:
                print(f"Error: {str(e)}")
                continue
            else:
                break
        return html

    def scrape_season(self, season):    # season is year eg 2016, 2017, ...
        url = self.schedule_url.format(season)
        html = self.get_html(url, "#content .filter")
        soup = BeautifulSoup(html)
        links = soup.find_all("a")
        hrefs = [link['href'] for link in links]
        standings_pages = [f"https://www.basketball-reference.com{href}" for href in hrefs]
        total_standings_pages = len(standings_pages)
        counter = 0
        for url in standings_pages:
            counter += 1
            print(f"\rScraping Season [ {season} ] - standings [ {counter}/{total_standings_pages} ]", end="")
            save_path = os.path.join(self.STANDING_DIR, url.split("/")[-1])
            if os.path.exists(save_path):
                continue

            html = self.get_html(url, "#all_schedule")
            with open(save_path, 'w+' ) as f:
                f.write(html)

    def scrape_all_seasons(self):
        for season in self.SEASONS:
            self.scrape_season(season)

        print('SEASONS SCRAPING COMPLETED!')

    def scrape_game(self, standing_file):
        with open(standing_file, 'r') as f:
            html = f.read()
        soup = BeautifulSoup(html)
        links = soup.find_all("a")
        hrefs = [link.get('href') for link in links]
        box_score = [l for l in hrefs if l and "boxscores" in l and ".html" in l]
        box_score = [f"https://www.basketball-reference.com{l}" for l in box_score]
        for url in box_score:
            save_path = os.path.join(self.SCORES_DIR, url.split('/')[-1])
            if os.path.exists(save_path):
                continue

            html = self.get_html(url, "#content")
            if not html:
                continue

            with open(save_path, 'w+') as f:
                f.write(html)

    def scrape_all_games(self):
        standing_files = os.listdir(self.STANDING_DIR)
        standing_files = [s for s in standing_files if ".html" in s]
        for file in standing_files:
            file_path = os.path.join(self.STANDING_DIR,file)
            self.scrape_game(file_path)

        print('GAME SCRAPING COMPLETED!')


    def start(self):
        self.initial_check()
        # part 1 scraping standings (all seasons) - DONE
        # self.scrape_all_seasons()

        # part 2 scraping box scores
        self.scrape_all_games()




x = NBA()
x.start()
