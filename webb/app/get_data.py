# std imports
import numpy as np
import pandas as pd

# selenium imports
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

from keras.models import load_model
import tensorflow as tf
# loads and returns a compiled model
global model, graph
model = load_model('working_model.h5')
graph = tf.get_default_graph()


# MAIN


def main():
    # start driver and wait
    driver = webdriver.Chrome(options=chrome_options())

    # get data for h1
    url = "https://www.betexplorer.com/handball/sweden/handbollsligan/"
    h1_g = predict_games(driver, url)
    h1_g
    h1_s = get_standings(driver, url)

    # get data for d1
    url = "https://www.betexplorer.com/handball/sweden/she-women/"
    d1_g = predict_games(driver, url)
    d1_s = get_standings(driver, url)

    return (h1_g, h1_s, d1_g, d1_s)

# Functiondefinitions


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


def get_next_games(driver, url):
    """Scrapes upcomming games and return as PD."""
    # set wait time
    timeout = 2

    # get webpage
    driver.get(url)
    WebDriverWait(driver, timeout)

    # extract elements text and save to array
    home = get_elements_text(driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(2) a span:nth-of-type(1)')
    away = get_elements_text(driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(2) a span:nth-of-type(2)')
    odds_1 = get_elements_text(driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(6)')
    odds_x = get_elements_text(driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(7)')
    odds_2 = get_elements_text(driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(8)')
    date = get_elements_text(driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(9)')

    # create PD from arrays created above then split to games with and without odds
    df = pd.DataFrame(np.column_stack([home, away, odds_1, odds_x, odds_2, date]), columns=['Home', 'Away', 'Odds 1', 'Odds X', 'Odds 2', 'Date'])
    return df


def predict_games(driver, url):
    """Return a DF with all uppcoming games where games with complete features is predicted and rest is untouched"""
    # get next games
    df = get_next_games(driver, url)

    # seperate games with and without odds
    df_with_odds = df.loc[df['Odds 1'] != ' ']
    df_no_odds = df.loc[df['Odds 1'] == ' ']

    df_no_odds['Odds 1'] = 'Not'
    df_no_odds['Odds X'] = 'Yet'
    df_no_odds['Odds 2'] = 'Available'
    

    # predict games with odds
    # make features to np array
    features = np.array(df_with_odds[['Odds 1', 'Odds X', 'Odds 2']].astype(float))

    # use model to make predictions
    with graph.as_default():
        predicted = np.array(model.predict(features))

    # process predictions and odds so that "Odds Fav" and "Predicted Fav" is appendet to each game
    rows_list = []
    odds_names = ['Away', 'Draw', 'Home']
    odds_order = ['Home', 'Draw', 'Away']
    for i in range(features.shape[0]):
        odds = features[i]
        prob = predicted[i]
        dict = {'Prob 1': prob[2], 'Prob X': prob[1], 'Prob 2': prob[0],
                'Predicted': odds_names[np.argmax(prob)], 'Odds Fav': odds_order[np.argmin(odds)]}
        rows_list.append(dict)

    first_columns = ['Odds Fav', 'Predicted', 'Prob 1', 'Prob X', 'Prob 2']
    list_predicted = pd.DataFrame(rows_list, columns=first_columns)

    # concat games with predicted value
    df_predicted_games = pd.concat([df_with_odds, list_predicted], axis=1, join_axes=[df_with_odds.index])

    # round and convert predicted value to string so it will display nice when df.iterrow is used in template.html
    df_predicted_games = df_predicted_games.round({'Prob 1': 2, 'Prob X': 2, 'Prob 2': 2}).astype(str)

    # concat predicted and not predicted games to get a complete list of upcoming games
    all_games = pd.concat([df_predicted_games, df_no_odds], sort=False).fillna('')

    # change order of columns in DataFrame
    columns_order = ['Date', 'Home', 'Away', 'Odds Fav', 'Odds 1', 'Odds X', 'Odds 2', 'Predicted', 'Prob 1', 'Prob X', 'Prob 2']
    all_games = all_games[columns_order]

    return (all_games)


def get_standings(driver, url):
    """Scrapes current standings"""
    # set wait time
    timeout = 2

    # get webpage
    driver.get(url)
    WebDriverWait(driver, timeout)

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
    table = pd.DataFrame(np.column_stack([table_obj[1], table_obj[2], table_obj[3], table_obj[4], table_obj[5], table_obj[6], table_obj[7], table_obj[8], game0, game1, game2, game3, game4]), columns=['#', 'TEAM', 'MP', 'W', 'D', 'L', 'G', 'PTS', 'G-1', 'G-2', 'G-3', 'G-4', 'G-5'])

    return table


# def get_played_games(driver, url):
#     """Scrapes played games and returns as PD"""
#     # click dropdown to show all games and not just last month
#     driver.get(url)
#     WebDriverWait(driver, timeout)
#     driver.find_element_by_css_selector('.wrap-header__list:nth-child(1) > .short .closed').click()
#     driver.find_element_by_css_selector('li.option.last').click()
#
#     # extract elements text and save to array
#     home = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) a span:nth-of-type(1)')
#     away = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) a span:nth-of-type(2)')
#     score = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(2)')
#     odds_1 = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(3)')
#     odds_x = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(4)')
#     odds_2 = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(5)')
#     date = get_elements_text(driver, '.table-main.h-mb15:not(.table-main--leaguefixtures) td:nth-of-type(6)')
#
#
#     # create PD from multiple arrays created above
#     played_games = pd.DataFrame(np.column_stack([home, away, score, odds_1, odds_x, odds_2, date]), columns=['Home', 'Away', 'Score', 'Odds 1', 'Odds X', 'Odds 2', 'Date'])
#     played_games
#     return played_games
#
# played_games = get_played_games(driver, url)
# played_games

if __name__ == '__main__':
    main()
# url = "https://www.betexplorer.com/handball/sweden/handbollsligan/"
# url = "https://www.betexplorer.com/handball/sweden/she-women/"
