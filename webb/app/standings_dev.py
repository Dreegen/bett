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

# MAIN
# start driver and wait
driver = webdriver.Chrome(options=chrome_options())

# get data for h1
url = "https://www.betexplorer.com/handball/sweden/handbollsligan/"
#h1_g = predict_games(driver, url)
#h1_s = get_standings(driver, url)

# # get data for d1
# url = "https://www.betexplorer.com/handball/sweden/she-women/"
# d1_g = predict_games(driver, url)
# d1_s = get_standings(driver, url)

# # get data for h2
# url = "https://www.betexplorer.com/handball/sweden/allsvenskan/"
# h2_g = predict_games(driver, url)
# h2_s = get_standings(driver, url)

# # get data for d2
# url = "https://www.betexplorer.com/handball/sweden/allsvenskan-women/"
# d2_g = predict_games(driver, url)
# d2_s = get_standings(driver, url)



###################


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
table = pd.DataFrame(np.column_stack([table_obj[1], table_obj[2], table_obj[3], table_obj[4], table_obj[5], table_obj[6], table_obj[7],
                                        table_obj[8], game0, game1, game2, game3, game4]), columns=['#', 'TEAM', 'MP', 'W', 'D', 'L', 'G', 'PTS', 'G-1', 'G-2', 'G-3', 'G-4', 'G-5'])

df = table

