from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import bs4
import multiprocessing
import sys
BASE_URL = 'https://www.metacritic.com/browse/games/release-date/available/PLATFORM/metascore?page='
PLATFORM = {
    "switch": "19",
    "ps4": "25",
    "xboxone": "19",
    "pc": "63",
}

SELECTORS = {
    'user score': 'div.details.side_details div.metascore_w.game',
    'meta score': 'div.score_summary.metascore_summary div.metascore_w.game > span',
    'developer': 'li.summary_detail.publisher > span.data > a',
    'release date': 'li.summary_detail.release_data > span.data',
    'rating': 'div.section.product_details > div.details.side_details > ul > li.summary_detail.product_rating > span.data',
}


def save(data, name):
    with open(f'{name}.json', 'a+') as f:
        json.dump(data, f)


def game_info(*args):
    title, link, browser, platform = args
    browser.get(link)
    page = browser.page_source
    print(f'\t\t[EXTRACTING {title} INFO]')
    entry = {}
    game = {}
    soup = bs4.BeautifulSoup(page, 'html.parser')
    game_container = soup.select_one(
        '#main > div > div:nth-child(1) > div.left')
    if not game_container:
        with open('missed.txt', 'a+') as err:
            print(f'{title}: {link}', file=err)
        save({title: None}, platform)
        return

    for prop, selector in SELECTORS.items():
        value = game_container.select_one(selector)
        if value:
            value = value.text.strip()
        game[prop] = value

    genres = game_container.select(
        'div.section.product_details > div.details.side_details > ul > li.summary_detail.product_genre > span.data')
    if genres:
        genres = [genre.text for genre in genres]
    game['genres'] = genres
    entry[title] = game
    print(f'\t\t[{title} INFO SAVED]')
    save(entry, platform)


def platform_games(platform, pages=0, start=0):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    browser = webdriver.Chrome(options=chrome_options)
    for page in range(int(start), int(pages)):
        print(f'\t[EXTRACTING PAGE {page}]')
        url = platform.join(BASE_URL.split("PLATFORM")) + str(page)
        browser.get(url)
        links = browser.find_elements_by_css_selector(
            'table > tbody > tr > td.clamp-summary-wrap > a')
        print(f'\t[GOT {len(links)} TITLES]')
        links = [(element.text, element.get_attribute('href'))
                 for element in links]
        for title, link in links:
            game_info(title, link, browser, platform)


if __name__ == "__main__":
    for platform, pages in PLATFORM.items():
        multiprocessing.Process(target=platform_games,
                                args=(platform, pages)).start()
