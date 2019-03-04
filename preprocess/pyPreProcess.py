# %% Start

import pandas as pd
import json
import psycopg2

def connectToSql():
    """Connects to SQL DB via settings in config.json"""
    # Open config file
    with open('./config/config.json') as f:
       config = json.load(f)

    # Get connection params as a string
    postgres_config_string = "host=%s dbname=%s user=%s password=%s" % (config.get(
        'host'), config.get('database'), config.get('user'), config.get('passw'))

    # Connect to db 
    # If a connect cannot be made an exception will be raised here
    con = psycopg2.connect(postgres_config_string)
    
    return con

# Connect to DB and save query as a dataframe
con = connectToSql()
query_1 = open('./sql/1_query.sql', 'r')
df = pd.read_sql(query_1.read(), con=con)

# rename SQL columns
df.rename(index=str, columns={'home_team':'homeTeam', 'guest_team':'awayTeam', 'home_score':'homeScore', 'guest_score':'awayScore', 'odds_1':'odds1', 'odds_x':'oddsX', 'odds_2':'odds2','explore_id':'exploreId'}, inplace=True)

# drop exploeID since it's not used to train the model
df.drop(columns=['exploreId'], inplace = True)

# # Season cleaning
# Dataset includes 'Seasons' that actually are cups, and when teams play unequal number of the features get messed up. Therefore does this function check that all teams play equal number games and drops the seasons that do not match the criteria

def drop_NotStdSeasons(df):
    seasonNames = df.season.unique()
    nSeasons = df.season.unique().shape[0]

    for i in range(nSeasons):
        melted_data = pd.melt(df[df.season == seasonNames[i]], value_vars=['homeTeam', 'awayTeam'], value_name='team')
        nGames = (melted_data.groupby(by=['team'])).count()
        useSeason = nGames['variable'].nunique()
    
        if useSeason == 1 and df[df.season == seasonNames[i]].shape[0] != 1:
            df.loc[df['season'] == seasonNames[i], 'useSeason'] = True
        
        else:
            df.loc[df['season'] == seasonNames[i], 'useSeason'] = False
            
        if 1 in nGames.values:
            df.loc[df['season'] == seasonNames[i], 'useSeason'] = False 
        
        
    df.drop(df.index[df['useSeason'] == False], inplace = True)
    df.drop(columns=['useSeason'], inplace = True)
    
    # sort and redefine index
    df.sort_values(by = ['season', 'date'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    seasonNames = df.season.unique()
    nSeasons = df.season.unique().shape[0]
    df.set_index(['season'], append=True,drop=True, inplace=True)
    return (seasonNames, nSeasons)

seasonNames, nSeasons = drop_NotStdSeasons(df)
 
def get_rounds(df):
    GAMES = df.shape[0]
    TEAMS = df.homeTeam.unique().shape[0]
    ROUNDS = int(GAMES * 2 / TEAMS)
    return ROUNDS

def get_games(df):
    GAMES = df.shape[0]
    return GAMES

def get_teams(df):
    TEAMS = df.homeTeam.unique().shape[0]
    return TEAMS

#%% [markdown]
# ## Get aggregated goals for team/round

#%%
def get_goalsScored(frame, ROUNDS):
    # create a dictionary with team names as keys
    teams = {}
    for i in frame.groupby('homeTeam').mean().T.columns:
        teams[i] = []
        
    # the value corresponding to keys is a list containing the match location.
    for i in range(len(frame)):
        HTGS = frame.iloc[i]['homeScore']
        ATGS = frame.iloc[i]['awayScore']
        teams[frame.iloc[i].homeTeam].append(HTGS)
        teams[frame.iloc[i].awayTeam].append(ATGS)
    
    # Create a dataframe for goals scored where rows are teams and cols are matchweek.
    goalsScored = pd.DataFrame(data=teams, index=[i for i in range(1, ROUNDS+1)]).T
    goalsScored[0] = 0

    # Aggregate to get uptil that point
    for i in range(2, ROUNDS+1):
        goalsScored[i] = goalsScored[i] + goalsScored[i - 1]
    
    return goalsScored

# Gets the goals conceded agg arranged by teams and matchweek
def get_goalsConceded(frame, ROUNDS):
    # Create a dictionary with team names as keys
    teams = {}
    for i in frame.groupby('homeTeam').mean().T.columns:
        teams[i] = []

    # the value corresponding to keys is a list containing the match location.
    for i in range(len(frame)):
        ATGC = frame.iloc[i]['homeScore']
        HTGC = frame.iloc[i]['awayScore']
        teams[frame.iloc[i].homeTeam].append(HTGC)
        teams[frame.iloc[i].awayTeam].append(ATGC)

    # Create a dataframe for goals scored where rows are teams and cols are matchweek.
    goalsConceded = pd.DataFrame(data=teams, index=[i for i in range(1, ROUNDS+1)]).T
    goalsConceded[0] = 0
    # Aggregate to get uptil that point
    for i in range(2, ROUNDS+1):
        goalsConceded[i] = goalsConceded[i] + goalsConceded[i - 1]
    return goalsConceded

def get_aggGoals(df):
    iHTGS = df.columns.get_loc('HTGS')
    iATGS = df.columns.get_loc('ATGS')
    iHTGC = df.columns.get_loc('HTGC')
    iATGC = df.columns.get_loc('ATGC')
    
    iteration = []
    
    for season in range(len(seasonNames)):
        try:
            ROUNDS = get_rounds(df.loc[(slice(None), seasonNames[season]),:])

            # Gets the goals scored/conceded aggregated and arranged by teams and matchweek
            goalsScored = get_goalsScored(df.loc[(slice(None),seasonNames[season]),:], ROUNDS)
            goalsConceded = get_goalsConceded(df.loc[(slice(None),seasonNames[season]),:], ROUNDS)

            # Gets integerindex of games for current season to be used later for value insertion in games cell
            gamesIndex = list(df.loc[(slice(None),seasonNames[season]),:].index.values)
            gamesIndex = [i[0] for i in gamesIndex]

            # Inserts agg scored/conceded uppuntil current game
            j = 0
            for i in range(len(gamesIndex)):
                ht = df.iloc[int(gamesIndex[i])].homeTeam
                at = df.iloc[int(gamesIndex[i])].awayTeam
                df.iat[int(gamesIndex[i]),int(iHTGS)] = goalsScored.loc[ht][j]
                df.iat[int(gamesIndex[i]),int(iATGS)] = goalsScored.loc[at][j]
                df.iat[int(gamesIndex[i]),int(iHTGC)] = goalsConceded.loc[ht][j]
                df.iat[int(gamesIndex[i]),int(iATGC)] = goalsConceded.loc[at][j]

                if ((i + 1) % 10) == 0:
                            j = j + 1
        except:
            iteration.append(season)
            pass 
        
    return (df, iteration)

if 'HTGS' not in df:
    df = df.reindex(columns = df.columns.tolist() + ['HTGS','ATGS', 'HTGC', 'ATGC'])
df, iteration = get_aggGoals(df)

#%% [markdown]
# #### a few (11) seasons don't work and should therefore be droped, they are in list 'notUsedSeasons'
# 
# **Cup or playoff-series**
# 'A1 2009/2010',
# 'Trophee des Champions 2014',
# 'Trophee des Champions 2015',
# 'Trophee des Champions 2016',
# 'Trophee des Champions 2017',
# 'Trophee des Champions 2018'
# 
# **Unknow, buggcheck remains**
# '1. Division Women 2010/2011',
#  '1. Division Women 2011/2012',
#  '1. Division Women 2012/2013',
#  '1. Division Women 2013/2014',
#  '2. Bundesliga 2015/2016',

#%%
notUsedSeasons = []
for season in iteration:
    notUsedSeasons.append(seasonNames[season])


#%%
df1 = df.copy()

#%% [markdown]
# # Get points

#%%
#RELOAD dataFrame
df = df1.copy()


#%%
def get_points(result):
    if result == 'W':
        return 2
    elif result == 'D':
        return 1
    else:
        return 0

def get_cuml_points(matchres, ROUNDS, TEAMS):
    matchres_points = matchres.applymap(get_points)
    for i in range(2, ROUNDS + 1):
        matchres_points[i] = matchres_points[i] + matchres_points[i-1]

    matchres_points.insert(column=0, loc=0, value=[0*i for i in range(TEAMS)])
    return matchres_points
    
def get_matchres(frame, ROUNDS):
    # Create a dictionary with team names as keys
    teams = {}
    for i in frame.groupby('homeTeam').mean().T.columns:
        teams[i] = []

    # the value corresponding to keys is a list containing the match result
    for i in range(len(frame)):
        if frame.iloc[i].ftr == 'Home':
            teams[frame.iloc[i].homeTeam].append('W')
            teams[frame.iloc[i].awayTeam].append('L')
        elif frame.iloc[i].ftr == 'Away':
            teams[frame.iloc[i].awayTeam].append('W')
            teams[frame.iloc[i].homeTeam].append('L')
        else:
            teams[frame.iloc[i].awayTeam].append('D')
            teams[frame.iloc[i].homeTeam].append('D')

    return pd.DataFrame(data=teams, index=[i for i in range(1, ROUNDS + 1)]).T


#%%
def get_aggPoints(df):        
    iHTP = df.columns.get_loc('HTP')
    iATP = df.columns.get_loc('ATP')
    
    iteration1 = []
    
    for season in range(len(seasonNames)):
        try:
            ROUNDS = get_rounds(df.loc[(slice(None), seasonNames[season]),:])
            TEAMS = get_teams(df.loc[(slice(None), seasonNames[season]),:])
            GAMES = get_games(df.loc[(slice(None), seasonNames[season]),:])

            matchres = get_matchres(df.loc[(slice(None), seasonNames[season]),:], ROUNDS)
            cum_pts = get_cuml_points(matchres, ROUNDS, TEAMS)

            # Gets integerindex of games for current season to be used later for value insertion in games cell
            gamesIndex = list(df.loc[(slice(None),seasonNames[season]),:].index.values)
            gamesIndex = [i[0] for i in gamesIndex]

            j = 0
            for i in range(len(gamesIndex)):
                ht = df.iloc[int(gamesIndex[i])].homeTeam
                at = df.iloc[int(gamesIndex[i])].awayTeam
                df.iat[int(gamesIndex[i]),int(iHTP)] = cum_pts.loc[ht][j]
                df.iat[int(gamesIndex[i]),int(iATP)] = cum_pts.loc[at][j]

                if ((i + 1) % 10) == 0:
                    j = j + 1
        except:
            iteration1.append(season)
            pass 
        
    return (df, iteration1)

if 'HTP' not in df:
    df = df.reindex(columns = df.columns.tolist() + ['HTP','ATP'])
df, iteration1 = get_aggPoints(df)


#%%
iteration1

#%% [markdown]
# ## Get Form

#%%
df1 = df.copy()


#%%
# DEV to REALOAD
df = df1.copy()


#%%
def get_form(df, ROUNDS, num):
    form = get_matchres(df, ROUNDS)
    form_final = form.copy()
    for i in range(num, ROUNDS+1):
        form_final[i] = ''
        j = 0
        while j < num:
            form_final[i] += form[i-j]
            j += 1
    return form_final


#%%
def add_form(df, GAMES, ROUNDS, num):
    form = get_form(df, ROUNDS, num)
    
    # HOW TO REPLACE?!?!?!
    h = ['M' for i in range(num * 10)]  # since form is not available for n MW (n*10)
    a = ['M' for i in range(num * 10)]
    
    iHTn = df.columns.get_loc('HM' + str(num))
    iATn = df.columns.get_loc('AM' + str(num))
    
    # Gets integerindex of games for current season to be used later for value insertion in games cell
    gamesIndex = list(df.loc[(slice(None),seasonNames[season]),:].index.values)
    gamesIndex = [i[0] for i in gamesIndex]    

    j = num
    for i in range((num*10), GAMES):
        ht = df.iloc[i].homeTeam
        at = df.iloc[i].awayTeam
        
        past = form.loc[ht][j]
        df.iat[int(gamesIndex[i]),int(iHTn)] = past[num-1]
        
        past = form.loc[at][j]
        df.iat[int(gamesIndex[i]),int(iATn)] = past[num-1]

        if ((i + 1) % 10) == 0:
            j = j + 1
            
    return df


#%%
def add_form_df(playing_stat):
    playing_stat = add_form(playing_stat, GAMES, ROUNDS, 1)
    playing_stat = add_form(playing_stat, GAMES, ROUNDS, 2)
    playing_stat = add_form(playing_stat, GAMES, ROUNDS, 3)
    playing_stat = add_form(playing_stat, GAMES, ROUNDS, 4)
    playing_stat = add_form(playing_stat, GAMES, ROUNDS, 5)
    return playing_stat


# Apply to each dataset
for frame in range(n_seasons):
    data_frames[frame] = add_form_df(data_frames[frame])


#%%
season = 0
df = df.loc[(slice(None), seasonNames[season]),:]
ROUNDS = get_rounds(df.loc[(slice(None), seasonNames[season]),:])
GAMES = get_games(df.loc[(slice(None), seasonNames[season]),:])
num = 3

if 'HM' + str(num) not in df:
    df = df.reindex(columns = df.columns.tolist() + ['HM' + str(num),'AM' + str(num)])


#%%
form = get_matchres(df, ROUNDS)
form_final = form.copy()
for i in range(num, ROUNDS+1):
    form_final[i] = ''
    j = 0
    while j < num:
        form_final[i] += form[i-j]
        j += 1
form_final

iHTn = df.columns.get_loc('HM' + str(num))
iATn = df.columns.get_loc('AM' + str(num))
iHTn
iATn

# Gets integerindex of games for current season to be used later for value insertion in games cell
gamesIndex = list(df.loc[(slice(None),seasonNames[season]),:].index.values)
gamesIndex = [i[0] for i in gamesIndex] 

j = num
test = []
for i in range(len(gamesIndex)):
    ht = df.iloc[int(gamesIndex[i])].homeTeam
    at = df.iloc[int(gamesIndex[i])].awayTeam
    test.append(ht+" vs "+at)
    
    


#%%
j = 0
for i in range(len(gamesIndex)):
    ht = df.iloc[int(gamesIndex[i])].homeTeam
    at = df.iloc[int(gamesIndex[i])].awayTeam
    df.iat[int(gamesIndex[i]),int(iHTP)] = cum_pts.loc[ht][j]
    df.iat[int(gamesIndex[i]),int(iATP)] = cum_pts.loc[at][j]

    if ((i + 1) % 10) == 0:
        j = j + 1
       
j = num
for i in range((num*10), GAMES):
    ht = df.iloc[i].homeTeam
    at = df.iloc[i].awayTeam

    past = form.loc[ht][j]
    df.iat[int(gamesIndex[i]),int(iHTn)] = past[num-1]

    past = form.loc[at][j]
    df.iat[int(gamesIndex[i]),int(iATn)] = past[num-1]

    if ((i + 1) % 10) == 0:
        j = j + 1

return df


#%%
df.loc[(slice(None),seasonNames[season]),:]


#%%



