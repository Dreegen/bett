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
model = load_model('model_201902182100.h5')
graph = tf.get_default_graph()


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
    homeTeam = get_elements_text(
        driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(2) a span:nth-of-type(1)')
    awayTeam = get_elements_text(
        driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(2) a span:nth-of-type(2)')
    odds_1 = get_elements_text(
        driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(6)')
    odds_x = get_elements_text(
        driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(7)')
    odds_2 = get_elements_text(
        driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(8)')
    date = get_elements_text(
        driver, '.table-main.table-main--leaguefixtures.h-mb15 td:nth-of-type(9)')

    # create PD from arrays created above then split to games with and without odds
    df = pd.DataFrame(np.column_stack([homeTeam, awayTeam, odds_1, odds_x, odds_2, date]), columns=[
                      'homeTeam', 'awayTeam', 'odds1', 'oddsX', 'odds2', 'Date'])
    return df


def get_form(df):
    # Gets the form points.
    def get_points(result):
        if result == 'W':
            return 2
        elif result == 'D':
            return 1
        else:
            return 0

    def get_form_points(string):
        sum = 0
        for letter in string:
            sum += get_points(letter)
        return sum

    df['FormPtsStr'] = df['M1'] + df['M2'] + df['M3'] + df['M4'] + df['M5']

    df['FormPts'] = df['FormPtsStr'].apply(get_form_points)

    # Identify Win/Loss Streaks if any.
    def get_3game_ws(string):
        if string[-3:] == 'WWW':
            return 1
        else:
            return 0

    def get_5game_ws(string):
        if string == 'WWWWW':
            return 1
        else:
            return 0

    def get_3game_ls(string):
        if string[-3:] == 'LLL':
            return 1
        else:
            return 0

    def get_5game_ls(string):
        if string == 'LLLLL':
            return 1
        else:
            return 0

    df['WinStreak3'] = df['FormPtsStr'].apply(get_3game_ws)
    df['WinStreak5'] = df['FormPtsStr'].apply(get_5game_ws)
    df['LossStreak3'] = df['FormPtsStr'].apply(get_3game_ls)
    df['LossStreak5'] = df['FormPtsStr'].apply(get_5game_ls)

    return df


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
    form_obj = driver.find_elements_by_css_selector(
        '.col_form span:not(.form-s)')
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
    for i in range(0, len(forms), 5):
        game0.append(forms[i])
        game1.append(forms[i + 1])
        game2.append(forms[i + 2])
        game3.append(forms[i + 3])
        game4.append(forms[i + 4])

    # create PD from arrays created above
    df = pd.DataFrame(np.column_stack([table_obj[1], table_obj[2], table_obj[3], table_obj[4], table_obj[5], table_obj[6], table_obj[7],
                                       table_obj[8], game0, game1, game2, game3, game4]), columns=['#', 'TEAM', 'MP', 'W', 'D', 'L', 'G', 'PTS', 'M1', 'M2', 'M3', 'M4', 'M5'])

    # splits score in format xx:yy to colFoo = xx, colBaz=yy
    df1 = df.G.str.split(pat=":", expand=True)
    df1.rename(columns={0: 'GS', 1: 'GC'}, inplace=True)

    # calculates goaldifference and concats to main df
    df1['GDiff'] = df1['GS'].astype(int) - df1['GC'].astype(int)
    df = pd.concat([df, df1], axis=1, sort=False)
    df.drop(columns=['#', 'G'], axis=1, inplace=True)

    df = get_form(df)
    df.set_index('TEAM', inplace=True)

    return df


def seperate_dfs(df):
    # seperate games with and without odds
    df_no_odds = df.loc[df['odds1'] == ' '].copy()
    df = df.loc[df['odds1'] != ' '].copy()
    df_no_odds['odds1'] = 'Not'
    df_no_odds['oddsX'] = 'Yet'
    df_no_odds['odds2'] = 'Available'
    return (df, df_no_odds)


def prep_features(df, standings):
    if 'HTGD' not in df:
        df = df.reindex(columns=df.columns.tolist() +
                        ['HTGD', 'ATGD', 'HTP', 'ATP', 'HTFormPts', 'ATFormPts','MW'])

    # combine standings and next games
    nMatches = df.shape[0]

    for i in range(nMatches):
        ht = df.loc[i].homeTeam
        at = df.loc[i].awayTeam

        # GoalDifference
        df.at[i, 'HTGD'] = standings.loc[ht]['GDiff']
        df.at[i, 'ATGD'] = standings.loc[at]['GDiff']

        # Points
        df.at[i, 'HTP'] = standings.loc[ht]['PTS']
        df.at[i, 'ATP'] = standings.loc[at]['PTS']

        # FormPoints
        df.at[i, 'HTFormPts'] = standings.loc[ht]['FormPts']
        df.at[i, 'ATFormPts'] = standings.loc[at]['FormPts']

        # GameWeek
        df.at[i, 'MW'] = int(standings.loc[ht]['MP'])

    # Diff in points
    df['DiffPts'] = df['HTP'] - df['ATP']

    # Diff in goaldifference
    df['DiffGD'] = df['HTGD'] - df['ATGD']

    # Diff in form points
    df['DiffFormPts'] = df['HTFormPts'] - df['ATFormPts']

    # Scale DiffPts , DiffFormPts, HTGD, ATGD by Matchweek.
    cols = ['DiffPts', 'DiffFormPts', 'DiffGD']

    for col in cols:
        df[col] = df[col] / df.MW

    return df


def predict_games(driver, url):
    standings = get_standings(driver, url)
    df = get_next_games(driver, url)
    df_with_odds, df_no_odds = seperate_dfs(df)
    df = prep_features(df_with_odds, standings)

    # select features and make np array
    featuresList = ['odds1', 'oddsX', 'odds2',
                    'DiffFormPts', 'DiffPts', 'DiffGD']
    features = np.array(df[featuresList].astype(float))

    # use model to make predictions
    with graph.as_default():
        predicted = model.predict(features)

    # process predictions and odds so that "Odds Fav" and "Predicted Fav" is appendet to each game
    rows_list = []
    odds_names = ['Away', 'Draw', 'Home']
    odds_order = ['Home', 'Draw', 'Away']
    for i in range(features.shape[0]):
        odds = features[i]
        prob = predicted[i]
        dict = {'prob1': prob[2], 'probX': prob[1], 'prob2': prob[0],
                'predicted': odds_names[np.argmax(prob)], 'oddsFav': odds_order[np.argmin(odds[0:3])]}
        rows_list.append(dict)

    first_columns = ['oddsFav', 'predicted', 'prob1', 'probX', 'prob2']
    list_predicted = pd.DataFrame(rows_list, columns=first_columns)

    # concat games with predicted value
    df_predicted_games = pd.concat(
        [df_with_odds, list_predicted], axis=1, join_axes=[df_with_odds.index])

    # round and convert predicted value to string so it will display nice when df.iterrow is used in template.html
    df_predicted_games = df_predicted_games.round(
        {'prob1': 2, 'probX': 2, 'prob2': 2}).astype(str)

    # concat predicted and not predicted games to get a complete list of upcoming games
    all_games = pd.concat(
        [df_predicted_games, df_no_odds], sort=False).fillna('')

    # change order of columns in DataFrame
    columns_order = ['Date', 'homeTeam', 'awayTeam', 'oddsFav',
                     'odds1', 'oddsX', 'odds2', 'predicted', 'prob1', 'probX', 'prob2']
    all_games = all_games[columns_order]

    return all_games


def predict_leauge(url):
    driver = webdriver.Chrome(options=chrome_options())
    df = predict_games(driver, url)
    return(df)


def main():
    h1 = predict_leauge(
        "https://www.betexplorer.com/handball/sweden/handbollsligan/")
    d1 = predict_leauge(
        "https://www.betexplorer.com/handball/sweden/she-women/")
    h2 = predict_leauge(
        "https://www.betexplorer.com/handball/sweden/allsvenskan/")
    d2 = predict_leauge(
        "https://www.betexplorer.com/handball/sweden/allsvenskan-women/")

    return (h1, d1, h2, d2)


if __name__ == '__main__':
    main()
