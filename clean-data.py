import numpy as np
import seaborn as sns
import pandas as pd

import regex as re
import requests

from helpers import get_end_year

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

    df.to_csv(f"all-joined.csv", index=False)
    return

def prune():
    """
    use seaborn to get collinearities to determine which stats to 
    take and leave.
    """
    df = pd.read_csv(f"./data/all-joined.csv")

    collinearity_matrix = df.iloc[:, 2:].corr()
    sns.heatmap(collinearity_matrix, xticklabels=collinearity_matrix.columns,yticklabels=collinearity_matrix.columns,cmap="crest", annot=True)

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
    join_all_standings()
    # prune()