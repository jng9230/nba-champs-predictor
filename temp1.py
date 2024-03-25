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
import datetime
def get_data():
    options = webdriver.ChromeOptions()
    
    # fixes some timeout stuff 
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage')

    year = datetime.date.today().year - 1 # NBA seasons start in curr_year - 1

    end_year = int(str(year)[-2:]) + 1
    if year == 1999:
        end_year = "00"
    elif end_year < 10:
        end_year = "0" + str(end_year)
    else:
        end_year = str(end_year)

    def get_trad_stats():
        url = f"https://www.nba.com/stats/teams/traditional?Season={year}-{end_year}&dir=A&sort=W"
        print(url)
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(10)
        # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.Crom_body__UYOcU > tr')))

        headers = ['GP', 'W', 'L', 'WIN%', 'MIN', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', '+/-']
        df = pd.DataFrame(columns=["TEAM", "YEAR", *headers])
        rows = driver.find_elements(By.CSS_SELECTOR, '.Crom_body__UYOcU > tr')
        
        print("TRAD ROWS FOUND:")
        print(len(rows))
        for r in rows:
            team = r.find_element(By.CSS_SELECTOR, ".StatsTeamsTraditionalTable_teamLogoSpan__1HRTS").text
            cols = r.find_elements(By.CSS_SELECTOR, "td")
            stats = []
            for c in cols[2:]: # ignore the team name and other first cols
                stats.append(c.text)

            data = [[team, *stats]]
            temp_df = pd.DataFrame(data, columns=["TEAM", *headers]) 
            
            temp_df['YEAR'] = year
            
            df = pd.concat([df, temp_df])
        
        driver.quit()
        print("TRAD STATS")
        print(df.shape)
        print(df)
        return df

    def get_advanced_stats():
        url = f"https://www.nba.com/stats/teams/advanced?Season={year}-{end_year}&dir=A&sort=W"
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(10)
        headers = ['GP', 'W', 'L', 'MIN', 'OFFRTG', 'DEFRTG', 'NETRTG', 'AST%', 'AST/TO', 'AST_RATIO', 'OREB%', 'DREB%', 'REB%', 'TOV%', 'EFG%', 'TS%', 'PACE', 'PIE', 'POSS']

        df = pd.DataFrame(columns=["TEAM", "YEAR", *headers])
        rows = driver.find_elements(By.CSS_SELECTOR, '.Crom_body__UYOcU > tr')
        print("ADVANCED ROWS FOUND:")
        print(len(rows))
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

        print("ADVANCED STATS")
        print(df.shape)
        print(df)
        driver.quit()
        return df
    
    def get_ranks(df):
        trad_stats = ['WIN%', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', '+/-']
        advanced_stats = ['W', 'L', 'OFFRTG', 'DEFRTG', 'NETRTG', 'AST%', 'AST/TO', 'AST_RATIO', 'OREB%', 'DREB%', 'REB%', 'TOV%', 'EFG%', 'TS%', 'PACE', 'PIE']
        all_stats = trad_stats + advanced_stats

        teams = list(df["TEAM"])
        for stat in all_stats:
            arr = []
            for team in teams:
                series = df.loc[(df["TEAM"] == team)][stat]
                arr.append([float(series.iloc[0]), team])

            # sort to get ranks
            arr.sort(key=lambda x: x[0], reverse=True)
            d = {}
            for i, (_, team) in enumerate(arr):
                d[team] = i + 1
            
            temp_df = df.loc[:, ["TEAM"]]
            def get_rank(x):
                return d[x[0]]
            thing = temp_df.apply(get_rank, axis=1)
            df[f"{stat}_RANK"] = thing

        print("DF WITH RANKS")
        print(df.shape)
        print(df)

        return df


    df1 = get_trad_stats()
    df2 = get_advanced_stats()
    cols_to_use = df2.columns.difference(df1.columns)
    cols_to_use = list(cols_to_use.values) # convert from Series to array
    cols_to_use.append("TEAM") # join on TEAM later

    print(cols_to_use)
    df3 = pd.merge(df1, df2[cols_to_use], left_on="TEAM", right_on="TEAM", how="outer")

    print("MERGED TRAD AND ADVANCED:")
    print(df3.shape)
    print(df3)
    df4 = get_ranks(df3)

    return df4

if __name__ == "__main__":
    # get_standings()
    # get_advanced_standings()
    # do_something()
    get_data()