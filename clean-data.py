import numpy as np
import seaborn as sns
import pandas as pd

import regex as re
import requests
from bs4 import BeautifulSoup


def join():
    #read in datasets and make them into dataframes
    # year = "1996"
    # end_year = "97"
    for year in range(1996, 2023):
        end_year = int(str(year)[-2:]) + 1
        if year == 1999:
            end_year = "00"
        elif end_year < 10:
            end_year = "0" + str(end_year)
        else:
            end_year = str(end_year)

        df1 = pd.read_csv(f"./data/{year}-{end_year}-standings.csv")
        df2 = pd.read_csv(f"./data/{year}-{end_year}-standings-advanced.csv")
        
        #join frames
        cols_to_use = df2.columns.difference(df1.columns)
        df3 = pd.merge(df1, df2[cols_to_use], left_index=True, right_index=True, how='outer')
        
        #make new csv 
        df3.to_csv(f"{year}-{end_year}-joined.csv", index=False)  

    return


def prune():
    """
    use seaborn to get collinearities to determine which stats to 
    take and leave.
    """
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
    join()