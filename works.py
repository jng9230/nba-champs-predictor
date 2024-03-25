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


def fix_standings():
    driver = webdriver.Chrome()
    year = 2023
    end_year = get_end_year(year)
    url = f"https://www.nba.com/stats/teams/traditional?Season={year}-{end_year}&dir=A&sort=W"

    #nav to URL and get data
    driver.get(url)
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

        temp_df['YEAR'] = year
        
        df = pd.concat([df, temp_df])

    print("TRAD")
    print(df.head())
    print(df.shape)
    # df.to_csv(f"{year}-{end_year}-standings.csv", index=False)  

    driver.quit()
    return df

def fix_advanced():
    "https://www.nba.com/stats/teams/advanced?dir=A&sort=W"
    driver = webdriver.Chrome()

    year = 2023
    end_year = get_end_year(year)

    url = f"https://www.nba.com/stats/teams/advanced?Season={year}-{end_year}&dir=A&sort=W"

    #nav to URL and get data
    driver.get(url)
    headers = ['GP', 'W', 'L', 'MIN', 'OFFRTG', 'DEFRTG', 'NETRTG', 'AST%', 'AST/TO', 'AST_RATIO', 'OREB%', 'DREB%', 'REB%', 'TOV%', 'EFG%', 'TS%', 'PACE', 'PIE', 'POSS']
    time.sleep(5)

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

    print("ADVANCED")
    print(df.head())
    print(df.shape)
    # df.to_csv(f"{year}-{end_year}-standings-advanced.csv", index=False)  

    driver.quit()
    return df


def join(df1, df2):
    year = 2023
    end_year = get_end_year(year)

    #read in datasets and make them into dataframes
    # df1 = pd.read_csv(f"./{year}-{end_year}-standings.csv")
    # df2 = pd.read_csv(f"./{year}-{end_year}-standings-advanced.csv")
    
    #join frames
    cols_to_use = df2.columns.difference(df1.columns)
    # print(cols_to_use)
    # print(cols_to_use.array)
    # print(cols_to_use.values)
    cols_to_use = cols_to_use.values
    # print(cols_to_use)
    # print(list(cols_to_use))
    cols_to_use = list(cols_to_use)
    cols_to_use.append("TEAM")
    # fuck = ["TEAM"] + cols_to_use
    # df1.drop(columns=["GP", "W", "L"]) # dropping duplicate GP? 
    # df3 = pd.merge(df1, df2[cols_to_use], left_index=True, right_index=True, how='outer')
    df3 = pd.merge(df1, df2[cols_to_use], left_on="TEAM", right_on="TEAM", how="outer")
    
    #make new csv 
    # df3.to_csv(f"{year}-{end_year}-joined.csv", index=False)  

    print(df3.head())
    print(df3.shape)

    return df3


def get_relative_data():
    """
    ranks the teams based on their stats relative to one another for each year
    - inspired by the lack of meaningful correlation between stats over a 20 year span, 
    arising from the fact that players and regulations vary from era to era 
    - rather than comparing, e.g., raw 3P%, we should compare how much better their 3P% is 
    relative to the league for that year 
    - e.g.: warriors' 2017 ORTG may be leading the league in 2017, but will make them 
    very middle of the road in 2023
    """

    # removed certain stats like MIN, GP, POSS
    trad_stats = ['WIN%', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', '+/-']
    advanced_stats = ['W', 'L', 'OFFRTG', 'DEFRTG', 'NETRTG', 'AST%', 'AST/TO', 'AST_RATIO', 'OREB%', 'DREB%', 'REB%', 'TOV%', 'EFG%', 'TS%', 'PACE', 'PIE']
    all_stats = trad_stats + advanced_stats
    
    # get and sort all stats by year
    # for year in range(1996, 2023):
    year = 2023
    end_year = get_end_year(year)
    df = pd.read_csv(f"./{year}-{end_year}-joined.csv")
    teams = list(df["TEAM"])
    for stat in all_stats:
    # for stat in ["W", "L"]:
        arr = []
        for team in teams:
            series = df.loc[(df["TEAM"] == team)][stat]
            arr.append([float(series.iloc[0]), team])
    
        arr.sort(key=lambda x: x[0], reverse=True)

        # rank each team
        d = {}
        for i, (_, team) in enumerate(arr):
            d[team] = i + 1
        
        temp_df = df.loc[:, ["TEAM"]]
        def get_rank(x):
            return d[x[0]]
        thing = temp_df.apply(get_rank, axis=1)
        # print(stat, year)
        # print(thing)
        df[f"{stat}_RANK"] = thing

    df.to_csv(f"./data/{year}-{end_year}-stats-ranked.csv")



if __name__ == "__main__":
    df1 = fix_standings()
    df2 = fix_advanced()
    df3 = join(df1, df2)
    df4 = get_relative_data()