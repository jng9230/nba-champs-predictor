import numpy as np
import seaborn as sns
import pandas as pd

import regex as re
import requests
from bs4 import BeautifulSoup
import time 
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys

from selenium import webdriver
from selenium.webdriver.common.by import By

from helpers import get_end_year

def get_standings():
    driver = webdriver.Chrome()

    # for year in range(1996, 2023):
    year = 2023
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
    time.sleep(3)
    
    # headers_ele = driver.find_elements(By.CSS_SELECTOR, '.Crom_headers__mzI_m > th')
    headers = ['GP', 'W', 'L', 'WIN%', 'MIN', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', '+/-']

    #shove data into new dataframe
    df = pd.DataFrame(columns=["TEAM", "YEAR", *headers])
    rows = driver.find_elements(By.CSS_SELECTOR, '.Crom_body__UYOcU > tr')
    print(rows)
    print(len(rows))
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

    # df.to_csv(f"{year}-{end_year}-standings.csv", index=False)  

    driver.quit()


def get_advanced_standings():
    """
    get the advanced stats for each year
    """
    driver = webdriver.Chrome()

    for year in range(1996, 2023):
        #generate URL
        # url = "https://www.nba.com/stats/teams/traditional?Season=1996-97&dir=A&sort=W_PCT"
        # https://www.nba.com/stats/teams/advanced?Season=1996-97
        end_year = get_end_year(year)

        # url = f"https://www.nba.com/stats/teams/advanced?Season={year}-{end_year}"
        url = f"https://www.nba.com/stats/teams/advanced?Season={year}-{end_year}&dir=A&sort=W"
    
        #nav to URL and get data
        driver.get(url)
        time.sleep(3)
        headers = ['GP', 'W', 'L', 'MIN', 'OFFRTG', 'DEFRTG', 'NETRTG', 'AST%', 'AST/TO', 'AST_RATIO', 'OREB%', 'DREB%', 'REB%', 'TOV%', 'EFG%', 'TS%', 'PACE', 'PIE', 'POSS']

        #shove data into new dataframe
        df = pd.DataFrame(columns=["TEAM", "YEAR", *headers])
        rows = driver.find_elements(By.CSS_SELECTOR, '.Crom_body__UYOcU > tr')
        for r in rows:
            team = r.find_element(By.CSS_SELECTOR, ".Crom_primary__EajZu").text
            cols = r.find_elements(By.CSS_SELECTOR, "td")
            stats = []
            for c in cols[2:]:
                stats.append(c.text)

            data = [[team, *stats]]
            temp_df = pd.DataFrame(data, columns=["TEAM", *headers]) 
            
            temp_df['YEAR'] = year
            
            df = pd.concat([df, temp_df])

        df.to_csv(f"{year}-{end_year}-standings-advanced.csv", index=False)  

    driver.quit()


def get_champs():
    driver = webdriver.Chrome()

    url = f"https://www.basketball-reference.com/playoffs/"

    driver.get(url)

    df = pd.DataFrame(columns=["YEAR", "TEAM"])
    rows = driver.find_elements(By.CSS_SELECTOR, "#champions_index tbody > tr")
    print(len(rows))
    for r in rows:
        #skip the border rows
        if r.get_attribute("class") == "thead":
            continue 

        team = r.find_element(By.CSS_SELECTOR, "td[data-stat='champion']").text
        print(team)
        year = r.find_element(By.CSS_SELECTOR, "th").text
        print(year)

        data = [[team]]
        temp_df = pd.DataFrame(data, columns=["TEAM"]) 
        
        temp_df['YEAR'] = year
        
        df = pd.concat([df, temp_df])
        # except:
        #     continue

    df.to_csv(f"champs-by-year.csv", index=False) 

    driver.quit()

def fix_standings():
    driver = webdriver.Chrome()

    # for year in range(1996, 2023):
    year = 1998
    #generate URL
    # url = "https://www.nba.com/stats/teams/traditional?Season=1996-97&dir=A&sort=W_PCT"
    end_year = get_end_year(year)

    # url = f"https://www.nba.com/stats/teams/traditional?Season={year}-{end_year}&dir=A&sort=W"
    url = "https://www.nba.com/stats/teams/traditional?Season=1998-99&dir=A&sort=W"

    #nav to URL and get data
    driver.get(url)
    headers_ele = driver.find_elements(By.CSS_SELECTOR, '.Crom_headers__mzI_m > th')
    # headers = []
    # for e in headers_ele[2:]: #first two are empty/team name stuff
    #     text = e.text

    #     if text == "":
    #         break

    #     headers.append(e.text)
    # print(headers)
    headers = ['GP', 'W', 'L', 'WIN%', 'MIN', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', '+/-']

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
        print(temp_df)

        temp_df['YEAR'] = year
        
        df = pd.concat([df, temp_df])

    df.to_csv(f"{year}-{end_year}-standings.csv", index=False)  

    driver.quit()

def fix_advanced():
    "https://www.nba.com/stats/teams/advanced?dir=A&sort=W"
    driver = webdriver.Chrome()

    year = 1998
    #generate URL
    # url = "https://www.nba.com/stats/teams/traditional?Season=1996-97&dir=A&sort=W_PCT"
    # https://www.nba.com/stats/teams/advanced?Season=1996-97
    end_year = get_end_year(year)

    # url = f"https://www.nba.com/stats/teams/advanced?Season=1997-98&dir=A&sort=W"
    url = "https://www.nba.com/stats/teams/advanced?Season=1998-99&dir=A&sort=W"

    #nav to URL and get data
    driver.get(url)
    headers = ['GP', 'W', 'L', 'MIN', 'OFFRTG', 'DEFRTG', 'NETRTG', 'AST%', 'AST/TO', 'AST_RATIO', 'OREB%', 'DREB%', 'REB%', 'TOV%', 'EFG%', 'TS%', 'PACE', 'PIE', 'POSS']

    #shove data into new dataframe
    df = pd.DataFrame(columns=["TEAM", "YEAR", *headers])
    rows = driver.find_elements(By.CSS_SELECTOR, '.Crom_body__UYOcU > tr')
    for r in rows:
        team = r.find_element(By.CSS_SELECTOR, ".Crom_primary__EajZu").text
        cols = r.find_elements(By.CSS_SELECTOR, "td")
        stats = []
        for c in cols[2:]:
            stats.append(c.text)

        data = [[team, *stats]]
        temp_df = pd.DataFrame(data, columns=["TEAM", *headers]) 
        
        temp_df['YEAR'] = year
        
        df = pd.concat([df, temp_df])

    df.to_csv(f"{year}-{end_year}-standings-advanced.csv", index=False)  

    driver.quit()


def do_something():
    print("HELLO WORLD")
    return

if __name__ == "__main__":
    get_standings()
    # get_advanced_standings()
    # do_something()