# std imports
import numpy as np
import pandas as pd

# selenium imports
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


def main(url):
    # set wait time
    timeout = 2

    # start driver and wait
    driver = webdriver.Chrome(options=chrome_options())
    driver.get(url)
    WebDriverWait(driver, timeout)

    # get data
    # next_games = get_next_games(driver)
    standings = get_standings(driver)

    # print data #ERASE = USED FOR DEBUGG
    # print(next_games)
    return standings


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


def get_next_games(driver):
    """Scrapes upcomming games and return as PD."""
    # extract elements text and save to array
    teams = get_elements_text(driver, '.table-main.table-main--leaguefixtures.hli-mb15 td:nth-of-type(2)')
    odds_1 = get_elements_text(driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(6)')
    odds_x = get_elements_text(driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(7)')
    odds_2 = get_elements_text(driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(8)')
    date = get_elements_text(driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(9)')

    # create PD from arrays created above
    next_games = pd.DataFrame(np.column_stack([teams, odds_1, odds_x, odds_2, date]),
                              columns=['Teams', 'Odds 1', 'Odds X', 'Odds 2', 'Date'])
    return next_games


def get_standings(driver):
    """Scrapes current standings"""

    # get column headers for table
    headers = get_elements_text(driver, '.stats-table.stats-main.table-1 th')

    # extract table rows and columns (team form excluded), save to multidim array
    table_obj = []
    for i in range(len(headers)):
        content = driver.find_elements_by_css_selector(
            '.stats-table.stats-main.table-1 tbody td:nth-of-type(' + str(i) + ')')
        table_obj.append([x.text for x in content])

    # extract team form and save to array
    form_obj = driver.find_elements_by_css_selector('.col_form span:not(.form-s)')
    forms = [x.get_attribute("class") for x in form_obj]

    # convert attribute text to normal langue (w for win, d for draw, l for loss)
    for i in range(len(forms)):
        if "form-w" in forms[i]:
            forms[i] = "W"
        if "form-d" in forms[i]:
            forms[i] = "D"
        if "form-l" in forms[i]:
            forms[i] = "L"

    # convert table_obj to list to prepare for pd-frame
    game0, game1, game2, game3, game4 = [], [], [], [], []
    for i in range(len(table_obj[1])):
        game0.append(forms[i])
        game1.append(forms[i + 1])
        game2.append(forms[i + 2])
        game3.append(forms[i + 3])
        game4.append(forms[i + 4])
        i = i + 4

    # create PD from arrays created above
    table = pd.DataFrame(np.column_stack([table_obj[1], table_obj[2], table_obj[3], table_obj[4], table_obj[5], table_obj[6], table_obj[7], table_obj[8], game0, game1, game2, game3, game4]), columns=['#', 'TEAM', 'MP', 'W', 'D', 'L', 'G', 'PTS', 'game0', 'game1', 'game2', 'game3', 'game4'])

    return table


# def get_played_games(driver, url):
#     """Scrapes played games and returns as PD"""
#     # click dropdown to show all games and not just last month
#     driver.get(url)
#     driver.find_element_by_css_selector('.wrap-header__list:nth-child(1) > .short .closed').click()
#     driver.find_element_by_css_selector('li.option.last').click()

#     # extract elements text and save to array
#     home = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) a span:nth-of-type(1)')
#     away = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) a span:nth-of-type(2)')
#     score = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(2)')
#     odds_1 = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(3)')
#     odds_x = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(4)')
#     odds_2 = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(5)')
#     date = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(6)')

#     # create PD from multiple arrays created above
#     played_games = pd.DataFrame(np.column_stack([home, away, score, odds_1, odds_x, odds_2, date]), columns=['Home', 'Away', 'Score', 'Odds 1', 'Odds X', 'Odds 2', 'Date'])

#     return played_games


if __name__ == '__main__':
    main(url)
