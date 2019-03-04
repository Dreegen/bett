import os
import numpy as np
import pandas as pd
from datetime import datetime as dt


# imports file to use to Pandas DF
csvFileName = 'results.csv'
csvLoc = os.getcwd() + '/model/data/'
csvSep = ';'
df = pd.read_csv(csvLoc + csvFileName, sep=csvSep)


columnNames = [
'Season', 
'Date', 
'HomeTeam', 
'AwayTeam', 
'Score', 
'FTHG', 
'FTAG', 
'Odds_1', 
'Odds_x', 
'Odds_2', 
'Explore_id', 
'FTR', 
]
