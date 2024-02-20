import numpy as np
import seaborn as sns
import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.linear_model import LinearRegression

import regex as re
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# meat_url = 'https://www.nba.com/stats/teams/traditional?Season=1996-97&dir=A&sort=W'
# temp_rq = requests.get(meat_url)
# if temp_rq.status_code != 200:
#   print("something went wrong:", temp_rq.status_code, temp_rq.reason)

# with open("data/temp_rq.html", "w",encoding='utf-7') as writer: 
#   writer.write(temp_rq.text)

# with open("data/temp_rq.html", "r") as reader:
#   meat_source = reader.read()

# meat_soup = BeautifulSoup(meat_source, "html.parser")
# table = meat_soup.find("table", {"class": "wikitable"})
# meat_dict = {"Country": [], "kg meat/person":[]}
# for row in table.findAll("tr")[1:]: 
#     meat_dict['Country'].append(row.find("a").text)
    
#     #try to find most recent year with data, and set to -99.9 otherwise
#     vals = row.findAll("td")
#     val_final = -99.9
#     for val in vals[-2::-1]: #iterate backwards for most recent; skip 2019 b/c of pandemic
#         try:
#             val_final = float(val.text)
#         except:
#             continue 
#         break
#     meat_dict['kg meat/person'].append(val_final)
    
# meat_df = pd.DataFrame.from_dict(data=meat_dict)

