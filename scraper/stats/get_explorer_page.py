import time
import csv
import os
import pandas as pd

# selenium imports
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

from startUrls_country import startUrls


def chrome_options():
    """Defines settings for chromedriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--incognito")
    return chrome_options


def get_elements_href(driver, css_selector):
    """Finds elements by ccs_selector and then extracts text to array."""
    obj = driver.find_elements_by_css_selector(
        css_selector)
    return [x.get_attribute("href") for x in obj]

def get_league_links(driver, url):
    driver.get(url)
    WebDriverWait(driver, 2)
    links = get_elements_href(driver, '.table-main.js-tablebanner-t a')
    return links

def get_result_links(driver, links):
    finalLinks = []
    finalNames = []
    for link in links:
        url = link+'results/'
        driver.get(url)
        WebDriverWait(driver, 1)

        try:
            finalLinks.append(driver.find_element_by_link_text(
                'Main').get_attribute("href"))
        except NoSuchElementException:
            finalLinks.append(url)
    
    return finalLinks


# start driver and wait
driver = webdriver.Chrome(options=chrome_options())

urls = startUrls
allLinks = []
for url in urls:
    links = get_league_links(driver, url)
    resultLinks = get_result_links(driver, links)
    allLinks.append(resultLinks)

# # save for later use
# df = pd.DataFrame(allLinks)
# df.to_pickle(links.pkl)


# Saves to csv in current working folder


csvfile = os.getcwd()+'/resultLinks2.csv'
with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for val in allLinks:
        writer.writerow([val])
