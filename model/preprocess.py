import numpy as np
import pandas as pd
from datetime import datetime as dt
import itertools

%matplotlib inline

loc = "data/"
raw_data_all = pd.read_csv(loc + 'results.csv', sep=";")


def parse_date(date):
    if date == '':
        return None
    else:
        return dt.strptime(date, '%d/%m/%Y').date()


raw_data_all.Date = raw_data_all.Date.apply(parse_date)

# sorts by date, oldest first
raw_data_all = raw_data_all.sort_values(by='Date')

# Splits seasons to individual DataFrames and assign them to array
season_names = raw_data_all.Season.unique()
n_seasons = raw_data_all.Season.unique().shape[0]


raw_data = []
for i in range(n_seasons):
    raw_data.append(raw_data_all.loc[raw_data_all['Season'] == season_names[i]])

# Gets all the statistics related to gameplay and assigns to variable split by season
columns_req = ['Season', 'Date', 'HomeTeam', 'AwayTeam',
               'FTHG', 'FTAG', 'FTR', 'Odds_1', 'Odds_x', 'Odds_2']

data_frames = []
for frame in range(n_seasons):
    data_frames.append(raw_data[frame][columns_req])

playing_statistics_1 = raw_data[1][columns_req]  # ERASE

# Sets variables for TEAMS, GAMES and ROUNDS


def get_rounds(playing_stat):
    GAMES = playing_stat.shape[0]
    TEAMS = playing_stat.HomeTeam.unique().shape[0]
    ROUNDS = int(GAMES * 2 / TEAMS)
    return TEAMS, ROUNDS, GAMES

# -------------- #
# GOALS SCORED AND CONCEDED AT THE END OF MATCHWEEK, ARRANGED BY TEAMS AND MATCHWEEK  ** #
# Gets the goals scored agg arranged by teams and matchweek


def get_goals_scored(playing_stat, ROUNDS):
    # Create a dictionary with team names as keys
    teams = {}
    for i in playing_stat.groupby('HomeTeam').mean().T.columns:
        teams[i] = []

    # the value corresponding to keys is a list containing the match location.
    for i in range(len(playing_stat)):
        HTGS = playing_stat.iloc[i]['FTHG']
        ATGS = playing_stat.iloc[i]['FTAG']
        teams[playing_stat.iloc[i].HomeTeam].append(HTGS)
        teams[playing_stat.iloc[i].AwayTeam].append(ATGS)

    # Create a dataframe for goals scored where rows are teams and cols are matchweek.
    GoalsScored = pd.DataFrame(data=teams, index=[i for i in range(1, ROUNDS + 1)]).T
    GoalsScored[0] = 0
    # Aggregate to get uptil that point
    for i in range(2, ROUNDS + 1):
        GoalsScored[i] = GoalsScored[i] + GoalsScored[i - 1]
    return GoalsScored


# Gets the goals conceded agg arranged by teams and matchweek
def get_goals_conceded(playing_stat, ROUNDS):
    # Create a dictionary with team names as keys
    teams = {}
    for i in playing_stat.groupby('HomeTeam').mean().T.columns:
        teams[i] = []

    # the value corresponding to keys is a list containing the match location.
    for i in range(len(playing_stat)):
        ATGC = playing_stat.iloc[i]['FTHG']
        HTGC = playing_stat.iloc[i]['FTAG']
        teams[playing_stat.iloc[i].HomeTeam].append(HTGC)
        teams[playing_stat.iloc[i].AwayTeam].append(ATGC)

    # Create a dataframe for goals scored where rows are teams and cols are matchweek.
    GoalsConceded = pd.DataFrame(data=teams, index=[i for i in range(1, ROUNDS + 1)]).T
    GoalsConceded[0] = 0
    # Aggregate to get uptil that point
    for i in range(2, ROUNDS + 1):
        GoalsConceded[i] = GoalsConceded[i] + GoalsConceded[i - 1]
    return GoalsConceded


def get_gss(playing_stat):
    TEAMS, ROUNDS, GAMES = get_rounds(playing_stat)

    GC = get_goals_conceded(playing_stat, ROUNDS)
    GS = get_goals_scored(playing_stat, ROUNDS)

    j = 0
    HTGS = []
    ATGS = []
    HTGC = []
    ATGC = []

    for i in range(GAMES):
        ht = playing_stat.iloc[i].HomeTeam
        at = playing_stat.iloc[i].AwayTeam
        HTGS.append(GS.loc[ht][j])
        ATGS.append(GS.loc[at][j])
        HTGC.append(GC.loc[ht][j])
        ATGC.append(GC.loc[at][j])

        if ((i + 1) % 10) == 0:
            j = j + 1

    playing_stat['HTGS'] = HTGS
    playing_stat['ATGS'] = ATGS
    playing_stat['HTGC'] = HTGC
    playing_stat['ATGC'] = ATGC

    return playing_stat


# Apply to each dataset
playing_statistics_1 = get_gss(playing_statistics_1)  # ERASE

for frame in range(n_seasons):
    data_frames[frame] = get_gss(data_frames[frame])

# GET RESPECTIVE POINTS:


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


def get_matchres(playing_stat, ROUNDS):
    # Create a dictionary with team names as keys
    teams = {}
    for i in playing_stat.groupby('HomeTeam').mean().T.columns:
        teams[i] = []

    # the value corresponding to keys is a list containing the match result
    for i in range(len(playing_stat)):
        if playing_stat.iloc[i].FTR == 'H':
            teams[playing_stat.iloc[i].HomeTeam].append('W')
            teams[playing_stat.iloc[i].AwayTeam].append('L')
        elif playing_stat.iloc[i].FTR == 'A':
            teams[playing_stat.iloc[i].AwayTeam].append('W')
            teams[playing_stat.iloc[i].HomeTeam].append('L')
        else:
            teams[playing_stat.iloc[i].AwayTeam].append('D')
            teams[playing_stat.iloc[i].HomeTeam].append('D')

    return pd.DataFrame(data=teams, index=[i for i in range(1, ROUNDS + 1)]).T


def get_agg_points(playing_stat):
    TEAMS, ROUNDS, GAMES = get_rounds(playing_stat)

    matchres = get_matchres(playing_stat, ROUNDS)
    cum_pts = get_cuml_points(matchres, ROUNDS, TEAMS)
    HTP = []
    ATP = []
    j = 0
    for i in range(GAMES):
        ht = playing_stat.iloc[i].HomeTeam
        at = playing_stat.iloc[i].AwayTeam
        HTP.append(cum_pts.loc[ht][j])
        ATP.append(cum_pts.loc[at][j])

        if ((i + 1) % 10) == 0:
            j = j + 1

    playing_stat['HTP'] = HTP
    playing_stat['ATP'] = ATP
    return playing_stat


# Apply to each dataset
for frame in range(n_seasons):
    data_frames[frame] = get_agg_points(data_frames[frame])

playing_statistics_1 = get_agg_points(playing_statistics_1)  # ERASE

# GET TEAM FORM:


def get_form(playing_stat, ROUNDS, num):
    form = get_matchres(playing_stat, ROUNDS)
    form_final = form.copy()
    for i in range(num, ROUNDS+1):
        form_final[i] = ''
        j = 0
        while j < num:
            form_final[i] += form[i-j]
            j += 1
    return form_final


def add_form(playing_stat, GAMES, ROUNDS, num):
    form = get_form(playing_stat, ROUNDS, num)
    h = ['M' for i in range(num * 10)]  # since form is not available for n MW (n*10)
    a = ['M' for i in range(num * 10)]

    j = num
    for i in range((num*10), GAMES):
        ht = playing_stat.iloc[i].HomeTeam
        at = playing_stat.iloc[i].AwayTeam

        past = form.loc[ht][j]               # get past n results
        h.append(past[num-1])                    # 0 index is most recent

        past = form.loc[at][j]               # get past n results.
        a.append(past[num-1])                   # 0 index is most recent

        if ((i + 1) % 10) == 0:
            j = j + 1

    playing_stat['HM' + str(num)] = h
    playing_stat['AM' + str(num)] = a

    return playing_stat


def add_form_df(playing_stat):
    TEAMS, ROUNDS, GAMES = get_rounds(playing_stat)
    playing_stat = add_form(playing_stat, GAMES, ROUNDS, 1)
    playing_stat = add_form(playing_stat, GAMES, ROUNDS, 2)
    playing_stat = add_form(playing_stat, GAMES, ROUNDS, 3)
    playing_stat = add_form(playing_stat, GAMES, ROUNDS, 4)
    playing_stat = add_form(playing_stat, GAMES, ROUNDS, 5)
    return playing_stat


# Apply to each dataset
for frame in range(n_seasons):
    data_frames[frame] = add_form_df(data_frames[frame])

playing_statistics_1 = add_form_df(playing_statistics_1)  # ERASE

# REARRANGING COLUMNS
cols = ['Season', 'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HTGS', 'ATGS', 'HTGC', 'ATGC', 'HTP', 'ATP', 'HM1', 'HM2', 'HM3',
        'HM4', 'HM5', 'AM1', 'AM2', 'AM3', 'AM4', 'AM5', 'Odds_1', 'Odds_x', 'Odds_2']

# Apply to each dataset
for frame in range(n_seasons):
    data_frames[frame] = data_frames[frame][cols]

playing_statistics_1 = playing_statistics_1[cols]  # ERASE

# Get matchweek


def get_mw(playing_stat):
    TEAMS, ROUNDS, GAMES = get_rounds(playing_stat)

    j = 1
    MatchWeek = []
    for i in range(GAMES):
        MatchWeek.append(j)
        if ((i + 1) % 10) == 0:
            j = j + 1
    playing_stat['MW'] = MatchWeek
    return playing_stat


# apply to all DataFrames
playing_statistics_1 = get_mw(playing_statistics_1)  # ERASE

for frame in range(n_seasons):
    data_frames[frame] = get_mw(data_frames[frame])

# CONCATENATE DATAFRAMES
playing_stat = pd.concat(data_frames, ignore_index=True)

# SOME PREPROCESS
# Gets the form points.


def get_form_points(string):
    sum = 0
    for letter in string:
        sum += get_points(letter)
    return sum


playing_stat['HTFormPtsStr'] = playing_stat['HM1'] + playing_stat['HM2'] + \
    playing_stat['HM3'] + playing_stat['HM4'] + playing_stat['HM5']
playing_stat['ATFormPtsStr'] = playing_stat['AM1'] + playing_stat['AM2'] + \
    playing_stat['AM3'] + playing_stat['AM4'] + playing_stat['AM5']

playing_stat['HTFormPts'] = playing_stat['HTFormPtsStr'].apply(get_form_points)
playing_stat['ATFormPts'] = playing_stat['ATFormPtsStr'].apply(get_form_points)

# Identify Win/Loss Streaks if any.


def get_3game_ws(string):
    if string[-3:] == 'WWW':
        return 1
    else:
        return 0


def get_5game_ws(string):
    if string == 'WWWWW':
        return 1
    else:
        return 0


def get_3game_ls(string):
    if string[-3:] == 'LLL':
        return 1
    else:
        return 0


def get_5game_ls(string):
    if string == 'LLLLL':
        return 1
    else:
        return 0


playing_stat['HTWinStreak3'] = playing_stat['HTFormPtsStr'].apply(get_3game_ws)
playing_stat['HTWinStreak5'] = playing_stat['HTFormPtsStr'].apply(get_5game_ws)
playing_stat['HTLossStreak3'] = playing_stat['HTFormPtsStr'].apply(get_3game_ls)
playing_stat['HTLossStreak5'] = playing_stat['HTFormPtsStr'].apply(get_5game_ls)

playing_stat['ATWinStreak3'] = playing_stat['ATFormPtsStr'].apply(get_3game_ws)
playing_stat['ATWinStreak5'] = playing_stat['ATFormPtsStr'].apply(get_5game_ws)
playing_stat['ATLossStreak3'] = playing_stat['ATFormPtsStr'].apply(get_3game_ls)
playing_stat['ATLossStreak5'] = playing_stat['ATFormPtsStr'].apply(get_5game_ls)

playing_stat.keys()

# Get Goal Difference
playing_stat['HTGD'] = playing_stat['HTGS'] - playing_stat['HTGC']
playing_stat['ATGD'] = playing_stat['ATGS'] - playing_stat['ATGC']

# Diff in points
playing_stat['DiffPts'] = playing_stat['HTP'] - playing_stat['ATP']
playing_stat['DiffFormPts'] = playing_stat['HTFormPts'] - playing_stat['ATFormPts']

#  Diff in last year positions
# playing_stat['DiffLP'] = playing_stat['HomeTeamLP'] - playing_stat['AwayTeamLP']


# Scale DiffPts , DiffFormPts, HTGD, ATGD by Matchweek.
cols = ['HTGD', 'ATGD', 'DiffPts', 'HTP', 'ATP']
playing_stat.MW = playing_stat.MW.astype(float)

for col in cols:
    playing_stat[col] = playing_stat[col] / playing_stat.MW

# SAVE TO CSV
playing_stat.to_csv(loc + "final_dataset.csv")
