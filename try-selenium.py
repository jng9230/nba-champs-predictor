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

for year in range(1996, 2023):
    #generate URL
    # url = "https://www.nba.com/stats/teams/traditional?Season=1996-97&dir=A&sort=W_PCT"
    end_year = int(str(year)[-2:]) + 1
    if year == 1999:
        end_year = "00"
    elif end_year < 10:
        end_year = "0" + str(end_year)
    else:
        end_year = str(end_year)

    url = f"https://www.nba.com/stats/teams/traditional?Season={year}-{end_year}&dir=A&sort=W"

    #nav to URL and get data
    driver.get(url)
    headers_ele = driver.find_elements(By.CSS_SELECTOR, '.Crom_headers__mzI_m > th')
    headers = []
    for e in headers_ele[2:]: #first two are empty/team name stuff
        text = e.text

        if text == "":
            break

        headers.append(e.text)

    #shove data into new dataframe
    df = pd.DataFrame(columns=["TEAM", "YEAR", *headers])
    rows = driver.find_elements(By.CSS_SELECTOR, '.Crom_body__UYOcU > tr')
    for r in rows:
        team = r.find_element(By.CSS_SELECTOR, ".StatsTeamsTraditionalTable_teamLogoSpan__1HRTS").text
        cols = r.find_elements(By.CSS_SELECTOR, "td")
        stats = []
        for c in cols[2:]:
            stats.append(c.text)

        data = [[team, *stats]]
        temp_df = pd.DataFrame(data, columns=["TEAM", *headers]) 
        
        temp_df['YEAR'] = year
        
        df = pd.concat([df, temp_df])

    df.to_csv(f"{year}-{end_year}-standings.csv", index=False)  

driver.quit()


