import numpy as np
import seaborn as sns
import pandas as pd

import regex as re
import requests
from bs4 import BeautifulSoup

# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys

from selenium import webdriver
from selenium.webdriver.common.by import By


driver = webdriver.Chrome()
# df = pd.DataFrame(columns=["TEAM", "YEAR", "GP", "W", "L"])

url = "https://www.nba.com/stats/teams/traditional?Season=1996-97&dir=A&sort=W_PCT"
driver.get(url)

# for year in range(1996, 2023):
    
# .Crom_body__UYOcU

# print(wrapper.text)
# print(wrapper)
# print(len(wrapper))
headers_ele = driver.find_elements(By.CSS_SELECTOR, '.Crom_headers__mzI_m > th')
headers = []
for e in headers_ele[2:]: #first two are empty/team name stuff
    text = e.text

    if text == "":
        break

    headers.append(e.text)

df = pd.DataFrame(columns=["TEAM", "YEAR", *headers])

rows = driver.find_elements(By.CSS_SELECTOR, '.Crom_body__UYOcU > tr')
for r in rows:
    team = r.find_element(By.CSS_SELECTOR, ".StatsTeamsTraditionalTable_teamLogoSpan__1HRTS").text
    cols = r.find_elements(By.CSS_SELECTOR, "td")
    stats = []
    for c in cols[2:]:
        stats.append(c.text)

    # data_tuples = list(zip(players_list[1:],salaries_list[1:])) # list of each players name and salary paired together
    data = [[team, *stats]]
    print(data)
    temp_df = pd.DataFrame(data, columns=["TEAM", *headers]) # creates dataframe of each tuple in list
    
    year = "1996"
    temp_df['YEAR'] = year
    
    df = pd.concat([df, temp_df])


print(df)

driver.quit()


