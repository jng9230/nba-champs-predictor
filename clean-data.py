import numpy as np
import seaborn as sns
import pandas as pd

import regex as re
import requests

from helpers import get_end_year
import matplotlib.pyplot as plt

ALL_JOINED_CSV = f"all-joined.csv"

def join_standings():
    for year in range(1996, 2023):
        end_year = get_end_year(year)

        #read in datasets and make them into dataframes
        df1 = pd.read_csv(f"./data/{year}-{end_year}-standings.csv")
        df2 = pd.read_csv(f"./data/{year}-{end_year}-standings-advanced.csv")
        
        #join frames
        cols_to_use = df2.columns.difference(df1.columns)
        df3 = pd.merge(df1, df2[cols_to_use], left_index=True, right_index=True, how='outer')
        
        #make new csv 
        df3.to_csv(f"{year}-{end_year}-joined.csv", index=False)  

    return

def join_97_98():
    # for year in range(1996, 2023):
    year = 1998
    end_year = get_end_year(year)

    #read in datasets and make them into dataframes
    df1 = pd.read_csv(f"./data/{year}-{end_year}-standings.csv")
    df2 = pd.read_csv(f"./data/{year}-{end_year}-standings-advanced.csv")
    
    #join frames
    cols_to_use = df2.columns.difference(df1.columns)
    df3 = pd.merge(df1, df2[cols_to_use], left_index=True, right_index=True, how='outer')
    
    #make new csv 
    df3.to_csv(f"{year}-{end_year}-joined.csv", index=False)  

    return

def join_champs():
    """
    
    - read in champs datasets
    - parse into dict {[key: string year]: team_name}
    -> no need to join champs by year with standings
    """
    return


def join_all_standings():
    """
    join all standings datasets into one large csv
    """
    df = pd.read_csv(f"./data/1996-97-joined.csv")
    for year in range(1997, 2023):
        end_year = get_end_year(year)

        #read in datasets and make them into dataframes
        df1 = pd.read_csv(f"./data/{year}-{end_year}-joined.csv")
        df = pd.concat([df, df1])

    df.to_csv(ALL_JOINED_CSV, index=False)
    return


def join_all_standings_with_champs():
    """
    add an additional column of either 0/1, 1 meaning that that team 
    won the championship that year
    """
    standings_df = pd.read_csv(f"./data/{ALL_JOINED_CSV}")
    champs_df = pd.read_csv(f"./data/champs-by-year.csv")
    champs_d = {}
    for index, row in champs_df.iterrows():
        year = row["YEAR"]
        team = row["TEAM"]
        champs_d[year] = team 

    temp_df = standings_df.loc[:, ["TEAM", "YEAR"]]
    def is_champ(x):
        team, year = x[0], x[1]

        return int(champs_d[year + 1] == team) #nba champ in year == season starting in year - 1
     
    champs_col = temp_df.apply(is_champ, axis=1)
    standings_df["IS_CHAMP"] = champs_col

    standings_df.to_csv(f"all-join-with-champs.csv", index=False)    
    return


def prune():
    """
    use seaborn to get collinearities to determine which stats to 
    take and leave.
    """
    # df = pd.read_csv(f"./data/all-joined.csv")
    df = pd.read_csv('./data/all-joined.csv', sep=',', thousands=',')
    # df["POSS"] = df["POSS"].apply(pd.to_numeric) #convert POSS from str to int
    # print(df)
    collinearity_matrix = df.iloc[:, 3:].corr()
    collinearity_matrix = collinearity_matrix.round(1)

    print(collinearity_matrix)

    #specify size of heatmap
    fig, ax = plt.subplots(figsize=(20, 20))

    #create seaborn heatmap
    # sns.heatmap(df)
    # sns.heatmap(collinearity_matrix, xticklabels=collinearity_matrix.columns,yticklabels=collinearity_matrix.columns,cmap="crest", annot=True)
    sns.heatmap(collinearity_matrix, xticklabels=collinearity_matrix.columns,yticklabels=collinearity_matrix.columns, annot=True)

    plt.savefig("seaborn-plot-2.png")
    
    return


def run_lr():
    """
    run the logistic regression
    """

    """
    can't just do years chronologically b/c game changes over time 
    - split the years another way
    - test: [2022, 2016, 2010, 2004, 1998]
    # - vali: [2021, 2015, 2011, 2005]
    # - train: everything else
    
    CROSS VALIDATION
    """


    return

if __name__ == "__main__":
    # join_97_98()
    # join_standings()
    # join_all_standings()
    # prune()
    join_all_standings_with_champs()