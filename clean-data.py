import numpy as np
import seaborn as sns
import pandas as pd
from helpers import get_end_year
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.linear_model import *
from sklearn.model_selection import *
from joblib import load, dump

ALL_JOINED_CSV = f"all-joined.csv"
ALL_JOINED_CHAMPS_CSV = f"all-join-with-champs.csv"
ALL_JOINED_RANKS_CSV = f"./data/all-join-ranks.csv"
ALL_JOINED_CHAMPS_AND_RANKS_CSV = f"./data/all-join-with-champs-and-ranks.csv"

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

    standings_df.to_csv(ALL_JOINED_CHAMPS_CSV, index=False)    
    return


def join_all_with_ranks():
    # join all years
    df = pd.read_csv(f"./data/1996-97-stats-ranked.csv")
    for year in range(1997, 2023):
        end_year = get_end_year(year)

        #read in datasets and make them into dataframes
        df1 = pd.read_csv(f"./data/{year}-{end_year}-stats-ranked.csv")
        df = pd.concat([df, df1])

    df.to_csv(ALL_JOINED_RANKS_CSV, index=False)

    # add in champs
    standings_df = pd.read_csv(f"{ALL_JOINED_RANKS_CSV}")
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

    standings_df.to_csv(ALL_JOINED_CHAMPS_CSV, index=False)  

    return


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
    for year in range(1996, 2023):
        end_year = get_end_year(year)
        df = pd.read_csv(f"./data/{year}-{end_year}-joined.csv")
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
            
    return


def generate_corr():
    """
    use seaborn to get collinearities to determine which stats to 
    take and leave.
    """
    # df = pd.read_csv(f"./data/all-joined.csv")
    df = pd.read_csv(f"./data/{ALL_JOINED_CHAMPS_CSV}", sep=',', thousands=',')

    #cut off old years to check data idk
    # print(df.iloc[532])
    # df = df.loc[174:, :] #20 years

    df = df.loc[532:, :]# 10 years

    # print(df)
    collinearity_matrix = df.iloc[:, 2:].corr()
    collinearity_matrix = collinearity_matrix.round(1)

    print(collinearity_matrix)

    #specify size of heatmap
    fig, ax = plt.subplots(figsize=(50, 50))

    #create seaborn heatmap
    # sns.heatmap(df)
    # sns.heatmap(collinearity_matrix, xticklabels=collinearity_matrix.columns,yticklabels=collinearity_matrix.columns,cmap="crest", annot=True)
    sns.heatmap(collinearity_matrix, xticklabels=collinearity_matrix.columns,yticklabels=collinearity_matrix.columns, annot=True)

    plt.savefig("./data/seaborn-ranks-with-year.png")
    
    return


def prune():
    """
    given the correlation matrix, we want to prune variables that have
    a correlation of 0 to winning a championship, as well as variables with
    0.5 or higher correlation to one another 
    - 0.5 is an observed value. stats like FG% and PTS, for example, have a 
    corr of 0.5 and logically are very equivalent to one another; remove them.


    - 0.5 might be a bit low, as pairs like (BLKA_RANK, FTA_RANK) are hit
        - does correctly hit stuff like +-_RANK and DREB_RANK tho (0.516)
    """
    df = pd.read_csv(f"./data/{ALL_JOINED_CHAMPS_CSV}", sep=',', thousands=',')

    #cut off old years to check data idk
    # print(df.iloc[532])
    # df = df.loc[174:, :] #20 years

    # df = df.loc[532:, :]# 10 years

    collinearity_matrix = df.iloc[:, 2:].corr()

    #find and remove == 0 with champs, >= 0.5
    ROWS, COLS = collinearity_matrix.shape
    STATS = list(collinearity_matrix.columns)

    corr = collinearity_matrix.values

    highly_collinear = defaultdict(set) # {[key:stat]: stats_that_are_highly_collinear_to_key[]}
    for r in range(ROWS):
        for c in range(r):
            if abs(corr[r][c]) >= 0.5:
                highly_collinear[STATS[r]].add(STATS[c])

    """
    map stats to index in array: best_stats
        - make a new array of [corr, stat] pairs

    sort array based on corr

    make array into a dict for faster access

    for each key in highly_collinear:
        if key is not highest in best_stats, remove key
        highest: higher order in best_stats arr relative to 
            all other stats in the dict's values for given key
    """
    best_stats = []
    for i, stat in enumerate(STATS):
        best_stats.append([corr[-1][i], stat])
    
    best_stats.sort(key=lambda x: x[0])

    best_stats_d = {}
    print(best_stats_d)

    # NEED TO MANUALLY REMOVE COLLINEARITIES; USE DOMAIN KNOWLEDGE
    for i, (corr, stat) in enumerate(best_stats):
        best_stats_d[stat] = i

    keep = []
    for k, v in highly_collinear.items():
        k_i = abs(best_stats_d[k])
        biggest = True
        for stat in v:
            if abs(best_stats_d[stat]) > k_i:
                biggest = False
                break
        
        if biggest:
            keep.append(k)
        
    print(keep)
    """
    without year: ['WIN%', 'DREB', 'NETRTG', 'OREB%', 'PIE', 'REB%', 'OFFRTG_RANK', 'TS%_RANK', 'FGA_RANK', '3PM_RANK', 'OREB_RANK']
    with year: ['WIN%', 'PTS', 'FGM', 'DREB', 'NETRTG', 'OREB%', 'PIE', 'REB%', 'OFFRTG_RANK', 'TS%_RANK', 'FGA_RANK', '3PM_RANK', 'OREB_RANK']
    with absolute value on corr and year: ['WIN%', 'PTS', 'FGM', 'DREB', 'NETRTG', 'PIE', 'REB%', 'FGA_RANK', '3PM_RANK', 'FTM_RANK', 
        'FT%_RANK', 'OREB_RANK', 'BLKA_RANK', 'PF_RANK']
    
    ['WIN%', 'PTS', 'FGM', 'FTA', 'DREB', 'NETRTG', 'PIE', 'REB%', 'FGA_RANK', '3PM_RANK', '3PA_RANK', 'FTM_RANK', 'FT%_RANK', 
        'OREB_RANK', 'BLKA_RANK', 'PF_RANK']
    """
    keep1 = ["TEAM", "YEAR", "IS_CHAMP"] + list(keep) 

    df1 = df[keep1]
    # df1 = df
    df1.reset_index(drop=True, inplace=True)
    df1.to_csv(f"./data/pruned-3.csv", index=False)
    return 

COLS_FOR_MODEL = ['YEAR', 'WIN%', 'PTS', 'FGM', 'FTA', 'DREB', 'NETRTG', 'PIE', 'REB%', 'FGA_RANK', '3PM_RANK', '3PA_RANK', 'FTM_RANK', 'FT%_RANK', 'OREB_RANK', 'BLKA_RANK', 'PF_RANK']
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
    # df = pd.read_csv("./data/pruned.csv")
    # df = pd.read_csv("./data/all-join-ranks.csv")
    df = pd.read_csv("./data/pruned-3.csv")
    COLS = list(df.columns)
    # print("COLS before: ")
    # print(COLS)
    COLS.remove("TEAM")
    COLS.remove("IS_CHAMP")
    # COLS.remove("YEAR")
    # COLS.remove("Unnamed: 0")
    # COLS.remove("GP")
    # print("COLS after: ")
    # print(COLS)
    # X = df[['YEAR', 'WIN%', 'DREB', 'NETRTG', 'OREB%', 'PIE', 'REB%', 'OFFRTG_RANK', 'TS%_RANK', 'FGA_RANK', '3PM_RANK', 'OREB_RANK']]
    X = df[COLS]
    #['WIN%', 'PTS', 'FGM', 'DREB', 'NETRTG', 'OREB%', 'PIE', 'REB%', 'OFFRTG_RANK', 'TS%_RANK', 'FGA_RANK', '3PM_RANK', 'OREB_RANK']
    y = df["IS_CHAMP"]

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=8)

    # remove feature names
    x_train, x_test, y_train, y_test = x_train.values, x_test.values, y_train.values, y_test.values

    model = LogisticRegression().fit(x_train,y_train)
    train_predictions = model.predict(x_train)
    test_predictions = model.predict(x_test)
    train_predictions = model.predict(x_train)

    test_predictions = model.predict(x_test)
    print(test_predictions)
    train_residuals = y_train - train_predictions
    test_residuals = y_test - test_predictions
    train_rmse = np.sqrt(np.mean(train_residuals**2))
    test_rmse = np.sqrt(np.mean(test_residuals**2))
    print("Train RMSE:",f'{train_rmse:.2f}',"\nTest RMSE:",f'{test_rmse:.2f}')
    print("Train R Squared",f'{model.score(x_train,y_train):.2f}',"\nTest R Squared",f'{model.score(x_test,y_test):.2f}')
    
    score = model.score(x_test, y_test)
    print(score)

    print(model.coef_)

    dump(model, "./models/model-2-28-24.joblib")
    return

def predict():
    model = load("./model-2-28-24.joblib")
    df = pd.read_csv("./data/pruned-3.csv")
    COLS = COLS_FOR_MODEL

    # want: print team, year, actual, pred
    # make above into another dataframe?
    def use_model_on_row(row):
        cols = row[COLS]
        return model.predict([cols])[0]
    
    preds = df.apply(use_model_on_row, axis=1)

    def use_model_for_probs(row):
        cols = row[COLS]
        cols = cols.to_numpy()
        cols = cols.astype(float)
        # print(model.predict_proba([cols]))
        # model.predict([cols])[0]
        # model.predict_proba([cols])
        # print(model.predict_proba([cols])[0][1])
        return model.predict_proba([cols])[0][1]
    probs = df.apply(use_model_for_probs, axis=1)

    # print(preds)
    # print(df)
    df1 = df[["TEAM", *COLS, "IS_CHAMP"]]
    df1["IS_CHAMP_PRED"] = preds
    df1["IS_CHAMP_PRED_PROB"] = probs
    df1.to_csv("./data/preds.csv")
    # print(model.predict(df.loc[0, :]))
    # temp = df.iloc[0,:]
    # temp = temp[COLS]

    # print(model.predict((temp.to_numpy()).reshape(-1, 1)))
    # print(model.predict((temp.to_numpy()).reshape(-1, 1)))
    # print(temp)
    # print(temp.to_numpy())
    # temp1 = temp.to_numpy()
    # print(model.predict(temp1.reshape(-1, 1)))
    # print(model.predict([temp]))
    return
if __name__ == "__main__":
    # get_relative_data()
    # join_all_with_ranks()
    # prune()
    # generate_corr()
    # run_lr()
    predict()