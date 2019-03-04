# std imports
import numpy as np
import pandas as pd
import time

# selenium imports
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


def chrome_options():
    """Defines settings for chromedriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--incognito")
    return chrome_options


def get_elements_text(driver, css_selector):
    """Finds elements by ccs_selector and then extracts text to array."""
    obj = driver.find_elements_by_css_selector(
        css_selector)
    return [x.text for x in obj]



"""Scrapes played games and returns as PD"""
# start driver and wait
driver = webdriver.Chrome(options=chrome_options())

# click dropdown to show all games and not just last month
url = "https://www.betexplorer.com/handball/sweden/handbollsligan/"
timeout1 = 5
timeout2 = 1
driver.get(url)
WebDriverWait(driver, timeout1)
driver.find_element_by_css_selector('.wrap-header__list:nth-child(1) > .short .closed').click()
driver.find_element_by_css_selector('li.option.last').click()
time.sleep(5)


# extract elements text and save to array
Date = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(6)')
HomeTeam = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) a span:nth-of-type(1)')
AwayTeam = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) a span:nth-of-type(2)')
Score = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(2)')
FTHG = []
FTAG = []
for i in range(len(Score)):
    FTHG.append(Score[i][0:2])
    FTAG.append(Score[i][3:5])

Odds_1 = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(3)')
Odds_x = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(4)')
Odds_2 = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(5)')

FTR = []
for i in range(len(Score)):
    if FTHG > FTAG:
        FTR.append('Home')
    if FTHG < FTAG:
        FTR.append('Away')
    else:
        FTR.append('Draw')

# create PD from multiple arrays created above
played_games = pd.DataFrame(np.column_stack([Date, HomeTeam, AwayTeam, Score, FTHG, FTAG, Odds_1, Odds_x, Odds_2, FTR]), columns=['Date', 'HomeTeam', 'AwayTeam', 'Score', 'FTHG', 'FTAG', 'Odds_1', 'Odds_x', 'Odds_2', 'FTR'])

played_games2 = []
