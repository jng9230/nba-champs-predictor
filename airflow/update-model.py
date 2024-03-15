import datetime
import pendulum
import os

import requests
from airflow.decorators import dag, task
# from airflow.providers.postgres.hooks.postgres import PostgresHook
# from airflow.providers.postgres.operators.postgres import PostgresOperator

import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from joblib import load, dump

@dag(
    dag_id="update-model",
    schedule_interval="0 0 * * *",
    start_date=pendulum.datetime(2023, 3, 14, tz="EST"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
)
def UpdateModel():
    @task 
    def get_data():

        driver = webdriver.Chrome()
        year = datetime.date.today().year
        end_year = int(str(year)[-2:]) + 1
        if year == 1999:
            end_year = "00"
        elif end_year < 10:
            end_year = "0" + str(end_year)
        else:
            end_year = str(end_year)

        def get_trad_stats():
            url = f"https://www.nba.com/stats/teams/traditional?Season={year}-{end_year}&dir=A&sort=W"
            driver.get(url)
            time.sleep(3) 

            headers = ['GP', 'W', 'L', 'WIN%', 'MIN', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', '+/-']
            df = pd.DataFrame(columns=["TEAM", "YEAR", *headers])
            rows = driver.find_elements(By.CSS_SELECTOR, '.Crom_body__UYOcU > tr')
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
            
            return df


        def get_advanced_stats():
            url = f"https://www.nba.com/stats/teams/advanced?Season={year}-{end_year}&dir=A&sort=W"
            driver.get(url)
            time.sleep(3)
            headers = ['GP', 'W', 'L', 'MIN', 'OFFRTG', 'DEFRTG', 'NETRTG', 'AST%', 'AST/TO', 'AST_RATIO', 'OREB%', 'DREB%', 'REB%', 'TOV%', 'EFG%', 'TS%', 'PACE', 'PIE', 'POSS']

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

            return df
        

        df1 = get_trad_stats()
        df2 = get_advanced_stats()
        cols_to_use = df2.columns.difference(df1.columns)
        df3 = pd.merge(df1, df2[cols_to_use], left_index=True, right_index=True, how='outer')
        df4 = get_ranks(df3)

        return df4
    
    @task
    def update_preds(df: pd.DataFrame):
        model = load("./model-2-28-24.joblib")
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
        df1["IS_CHAMP_PRED_PROB"] = probs

        return df1
    
    # IDK IF load_data() IS USEFUL
    @task
    def load_data():
        return
    
    @task
    def update_website(data):
        return

    df = get_data()
    df1 = update_preds(df)
    print(df1)
    update_website(df1)

dag = UpdateModel()