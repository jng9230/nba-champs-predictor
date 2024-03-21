import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from joblib import load, dump
def update_preds(df: pd.DataFrame):
    model = load("./models/model-2-28-24.joblib")
    COLS_FOR_MODEL = ['YEAR', 'WIN%', 'PTS', 'FGM', 'FTA', 'DREB', 'NETRTG', 'PIE', 'REB%', 'FGA_RANK', '3PM_RANK', '3PA_RANK', 'FTM_RANK', 'FT%_RANK', 'OREB_RANK', 'BLKA_RANK', 'PF_RANK']
    COLS = COLS_FOR_MODEL

    # def use_model_on_row(row):
    #     cols = row[COLS]
    #     return model.predict([cols])[0]
    # preds = df.apply(use_model_on_row, axis=1)

    def use_model_for_probs(row):
        cols = row[COLS]
        cols = cols.to_numpy()
        cols = cols.astype(float)
        return model.predict_proba([cols])[0][1]
    probs = df.apply(use_model_for_probs, axis=1)

    # df1 = df[["TEAM", *COLS, "IS_CHAMP"]]
    
    df1 = df[["TEAM", *COLS]]
    # df1["IS_CHAMP_PRED"] = preds
    print(df1)
    print(df1.shape)
    print(probs)
    print(probs.shape)
    df1["IS_CHAMP_PRED_PROB"] = probs

    return df1

# df = pd.read_csv("./data/pruned-3.csv")
# update_preds(df)

def get_trad_stats():
        driver = webdriver.Chrome()
        year, end_year = 2023, 24
        url = f"https://www.nba.com/stats/teams/traditional?Season={year}-{end_year}&dir=A&sort=W"
        print(url)
        driver.get(url)
        time.sleep(3) 

        print(driver.page_source)

        headers = ['GP', 'W', 'L', 'WIN%', 'MIN', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', '+/-']
        df = pd.DataFrame(columns=["TEAM", "YEAR", *headers])
        rows = driver.find_elements(By.CSS_SELECTOR, '.Crom_body__UYOcU > tr')

        
        print("TRAD ROWS FOUND:")
        print(rows)
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
        
        print("TRAD STATS")
        print(df.shape)
        print(df)
        return df

get_trad_stats()