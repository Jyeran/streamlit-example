import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
import numpy as np

def getScores(test = False):
    URL = "https://www.espn.com/golf/leaderboard/_/tour/lpga"
    eventPage = requests.get(URL)
    eventSoup = soup(eventPage.content, "html.parser") 
    eventSoup = eventSoup.find(id="fittPageContainer")
    
    event = eventSoup.find("h1", class_="headline headline__h1 Leaderboard__Event__Title")
    event = event.text
    
    #-----------------------#
    
    URL = "https://www.espn.com/golf/leaderboard/_/tour/lpga"
    page = requests.get(URL)
    
    golf = soup(page.content, "html.parser")
    
    results = golf.find(id="fittPageContainer")
    
    golfers = results.find_all("tr", class_="PlayerRow__Overview Table__TR Table__even")
    
    golfScores = {}
    golfCutWD  = {}
    preTournament = False
    
    for g in golfers:
        info = g.find_all("td", class_="Table__TD")
        #print(info[0].text, info[1].text)
        
        try:
            indexTest = info[3].text
        except:
            preTournament = True
            
        if not preTournament:
            try:
                int(info[2].text)
                name = 3
            except:
                name = 2
            
            if name == 2 and info[2].text != "-" and info[2].text != "CUT":
                position = info[1].text
                name = info[2].text
                score  = info[3].text
                thru = info[5].text
                #print("block1")
            else:
                position = info[1].text
                name = info[3].text
                score  = info[4].text
                thru = info[6].text
                #print("block2")
                
        
            #print(info[1].text)
            #print(info[2].text)
            #print(info[3].text)
            #print(info[4].text)
            #print(info[5].text)
            #print(info[6].text)
            #print("---------------------------")
                #return 1, 2, 3
            
            if score == 'CUT' or score == 'WD' or score == '-':
                golfCutWD[name] = score
            else:
                if score == 'E':
                    score = 0
                    
                #print(name,score, info[0].text,info[1].text)
                score = int(score)
                golfScores[name] = [score, thru]
                
        else:
            name = info[0].text
            thru = info[1].text
            score = 0
            golfScores[name] = [score, thru]
            
    golferScores = pd.DataFrame(golfScores.values(), index=golfScores.keys()).reset_index()
    golferScores.columns = ['Player','Score','Thru']
    
    if test:
        
        tester = {}
        tester['1'] = info[1].text
        tester['2'] = info[2].text
        tester['3'] = info[3].text
        tester['4'] = info[4].text
        tester['5'] = info[5].text
        tester['6'] = info[6].text
            
        tester = pd.DataFrame(tester.values(), index=tester.keys()).reset_index()
            
        return tester
    
    
    return golferScores, event, golfCutWD

    
def getLeaderboard(golferScores, path = r"./RawGolferPicks.csv", cutValue = 10):    
    #path = r"./RawGolferPicks.csv"
    #path = r"/Users/rhea/Documents/golfPool/HackApp/RawGolferPicks.csv"
    picks = pd.read_csv(path)
    picksRaw = pd.read_csv(path)

    picks = pd.melt(picks, id_vars=['Entry'])
    picks.columns = ['Entry','Group','Player']
    picks['Player'] = picks['Player'].str.strip()

    golferScores, event, cutWD = getScores()
    playerThru = golferScores.copy(deep=True)
    #golferScores = golferScores.drop(['Thru'], axis = 1)
    picks = pd.merge(picks, golferScores, on='Player', how ='left')

    picks['Rank'] = picks.groupby('Entry')['Score'].rank('first',ascending=True)

    filt = (picks['Rank'] <= 4) #& (picks['Score'] <= 10)
    topPicks = picks[filt]
    
    picks['Score'] = picks['Score'].fillna(20)

    scores = topPicks.groupby('Entry').agg({'Score':'sum'})

    picksWide = picks.pivot_table(index='Entry',columns=['Group'],values='Score', aggfunc='sum').reset_index()
    picksThru = picks.pivot_table(index='Entry',columns=['Group'],values='Thru', aggfunc='sum').reset_index()
    picksWide = picksWide.round(decimals=0)
    #picksWide.columns = ['_'.join(col) for col in picksWide.columns.values]

    cols = []
    for col in picksWide.columns.values:
        cols.append(col + ": Score")   
    picksWide.columns = cols

    cols = []
    for col in picksThru.columns.values:
        cols.append(col + ": Thru")   
    picksThru.columns = cols

    cols = []
    for col in picksRaw.columns.values:
        cols.append(col + ": Player")   
    picksRaw.columns = cols

    picksWide.columns = ['Entry', 'A Score', 'B Score', 'C Score', 'D Score', 'E Score', 'F Score']
    picksWide = picksWide.rename(columns={'Entry: Score':'Entry'})
    picksRaw = picksRaw.rename(columns={'Entry: Player':'Entry'})
    picksThru = picksThru.rename(columns={'Entry: Thru':'Entry'})

    picksWide = pd.merge(picksWide, scores, on = ['Entry'], how='left')
    picksWide = pd.merge(picksWide, picksRaw, on = ['Entry'], how = 'left')
    picksWide = pd.merge(picksWide, picksThru, on = ['Entry'], how = 'left')

    picksWide['Group A: Player'] = picksWide['Group A: Player'] + " (" + picksWide['Group A: Thru'].astype(str) + ")"
    picksWide['Group B: Player'] = picksWide['Group B: Player'] + " (" + picksWide['Group B: Thru'].astype(str) + ")"
    picksWide['Group C: Player'] = picksWide['Group C: Player'] + " (" + picksWide['Group C: Thru'].astype(str) + ")"
    picksWide['Group D: Player'] = picksWide['Group D: Player'] + " (" + picksWide['Group D: Thru'].astype(str) + ")"
    picksWide['Group E: Player'] = picksWide['Group E: Player'] + " (" + picksWide['Group E: Thru'].astype(str) + ")"
    picksWide['Group F: Player'] = picksWide['Group F: Player'] + " (" + picksWide['Group F: Thru'].astype(str) + ")"


    cols = ['Entry', 'Score',
            'Group A: Player', 'A Score',
            'Group B: Player', 'B Score',
            'Group C: Player', 'C Score',
            'Group D: Player', 'D Score',
            'Group E: Player', 'E Score',
            'Group F: Player', 'F Score']

    picksWide = picksWide[cols]
    
    picksWide = picksWide.sort_values(by='Score', ascending=True)
    
    picksWide['Score'] = picksWide['Score'].fillna(0)
    
    return picksWide

def read_config():
    path = r'./admin.csv'
    config = pd.read_csv(path)
    cols = ['setting','value']
    config = config[cols]
    config = config.set_index('setting')
    return config

def write_config(config):
    config['setting'] = config.index
    cols = ['setting','value']
    config = config[cols]
    path = r"./admin.csv"
    config.to_csv(path, index = False)
    
def read_groups():
    #path = r"/Users/rhea/Documents/golfPool/HackApp/groups.csv"
    path = r'./groups.csv'
    groups = pd.read_csv(path)
    
    letters = ['A','B','C','D','E','F']
    groupLists = []
    
    for letter in letters:
        col = "Group " + letter
        group = groups[col].str.strip().to_list()
        group.insert(0,"")
        groupLists.append(group)
    
    return groupLists

"""
#
path = r"./RawGolferPicks.csv"
path = r"/Users/rhea/Documents/golfPool/HackApp/RawGolferPicks.csv"
picks = pd.read_csv(path)
picksRaw = pd.read_csv(path)

picks = pd.melt(picks, id_vars=['Entry'])
picks.columns = ['Entry','Group','Player']
picks['Player'] = picks['Player'].str.strip()

golferScores, event, cutWD = getScores()
playerThru = golferScores.copy(deep=True)
#golferScores = golferScores.drop(['Thru'], axis = 1)
picks = pd.merge(picks, golferScores, on='Player', how ='left')

picks['Rank'] = picks.groupby('Entry')['Score'].rank('first',ascending=True)

filt = (picks['Rank'] <= 4) & (picks['Score'] <= 25)
topPicks = picks[filt]

picks['Score'] = picks['Score'].fillna("CUT")

scores = topPicks.groupby('Entry').agg({'Score':'sum'})


picksWide = picks.pivot_table(index='Entry',columns=['Group'],values='Score', aggfunc='sum').reset_index()
picksThru = picks.pivot_table(index='Entry',columns=['Group'],values='Thru', aggfunc='sum').reset_index()
picksWide = picksWide.round(decimals=0)
#picksWide.columns = ['_'.join(col) for col in picksWide.columns.values]

cols = []
for col in picksWide.columns.values:
    cols.append(col + ": Score")   
picksWide.columns = cols

cols = []
for col in picksThru.columns.values:
    cols.append(col + ": Thru")   
picksThru.columns = cols

cols = []
for col in picksRaw.columns.values:
    cols.append(col + ": Player")   
picksRaw.columns = cols

picksWide.columns = ['Entry', 'A Score', 'B Score', 'C Score', 'D Score', 'E Score', 'F Score']
picksWide = picksWide.rename(columns={'Entry: Score':'Entry'})
picksRaw = picksRaw.rename(columns={'Entry: Player':'Entry'})
picksThru = picksThru.rename(columns={'Entry: Thru':'Entry'})

picksWide = pd.merge(picksWide, scores, on = ['Entry'], how='left')
picksWide = pd.merge(picksWide, picksRaw, on = ['Entry'], how = 'left')
picksWide = pd.merge(picksWide, picksThru, on = ['Entry'], how = 'left')

picksWide['Group A: Player'] = picksWide['Group A: Player'] + " (" + picksWide['Group A: Thru'] + ")"
picksWide['Group B: Player'] = picksWide['Group B: Player'] + " (" + picksWide['Group B: Thru'] + ")"
picksWide['Group C: Player'] = picksWide['Group C: Player'] + " (" + picksWide['Group C: Thru'] + ")"
picksWide['Group D: Player'] = picksWide['Group D: Player'] + " (" + picksWide['Group D: Thru'] + ")"
picksWide['Group E: Player'] = picksWide['Group E: Player'] + " (" + picksWide['Group E: Thru'] + ")"
picksWide['Group F: Player'] = picksWide['Group F: Player'] + " (" + picksWide['Group F: Thru'] + ")"

cols = ['Entry', 'Score',
        'Group A: Player', 'A Score',
        'Group B: Player', 'B Score',
        'Group C: Player', 'C Score',
        'Group D: Player', 'D Score',
        'Group E: Player', 'E Score',
        'Group F: Player', 'F Score']

picksWide = picksWide[cols]

picksWide = picksWide.sort_values(by='Score', ascending=True)

picksWide['Score'] = picksWide['Score'].fillna(0)"""
"""
path = r"/Users/rhea/Documents/golfPool/RawGolferPicks.csv"
picks = pd.read_csv(path)

path = r"/Users/rhea/Documents/golfPool/RawGolferPicks.csv"
picksRaw = pd.read_csv(path)

picks = pd.melt(picks, id_vars=['Entry'])
picks.columns = ['Entry','Group','Player']

golferScores = getScores()
picks = pd.merge(picks, golferScores, on='Player', how ='left')

picks['Rank'] = picks.groupby('Entry')['Score'].rank('first',ascending=True)

filt = picks['Rank'] <= 4
topPicks = picks[filt]

scores = topPicks.groupby('Entry').agg({'Score':'sum'})

picksWide = picks.pivot_table(index='Entry',columns=['Group'],values='Score', aggfunc='sum').reset_index()

#picksWide.columns = ['_'.join(col) for col in picksWide.columns.values]

cols = []
for col in picksWide.columns.values:
    cols.append(col + ": Score")   
picksWide.columns = cols

cols = []
for col in picksRaw.columns.values:
    cols.append(col + ": Player")   
picksRaw.columns = cols

picksWide = picksWide.rename(columns={'Entry: Score':'Entry'})
picksRaw = picksRaw.rename(columns={'Entry: Player':'Entry'})

picksWide = pd.merge(picksWide, scores, on = ['Entry'], how='inner')
picksWide = pd.merge(picksWide, picksRaw, on = ['Entry'], how = 'left')

cols = ['Entry', 'Score',
        'Group A: Player', 'Group A: Score',
        'Group B: Player', 'Group B: Score',
        'Group C: Player', 'Group C: Score',
        'Group D: Player', 'Group D: Score',
        'Group E: Player', 'Group E: Score',
        'Group F: Player', 'Group F: Score']

picksWide = picksWide[cols]

"""







"""

playerScores, event, cut = getScores()

path = r"/Users/rhea/Documents/golfPool/HackApp/RawGolferPicks.csv"
leaderboard = getLeaderboard(playerScores, path)

path = r'/Users/rhea/Documents/golfPool/HackApp/admin.csv'
config = pd.read_csv(path)
config['setting'] = ['entryLock','tournamentDay','cutValue']
config = config[['setting','value']]
config = config.set_index('setting')
config.loc['entryLock']['value']
config = config.reset_index()
config.to_csv(path)

rankIndex = range(1,len(leaderboard)+1)
leaderboard.index = rankIndex

leaderboard['Score to Beat'] = 0

count = 1
i = 0
for index, row in leaderboard.iterrows():

    gA = row['A Score']
    gB = row['B Score']
    gC = row['C Score']
    gD = row['D Score']
    gE = row['E Score']
    gF = row['F Score']
    
    scoreList = [gA, gB, gC, gD, gE, gF]
    scoreList = sorted(scoreList)
    print(scoreList, scoreList[3])
    leaderboard.iloc[i,-1] = scoreList[3]
    
    count+=1
    i += 1

leaderboard['Group A'] = np.where(leaderboard['A Score'] <= leaderboard['Score to Beat'],
                                  leaderboard['Group A: Player'] + ": " + leaderboard['A Score'].astype(str),
                                  "~~" + leaderboard['Group A: Player'] + ": " + leaderboard['A Score'].astype(str) + "~~")

leaderboard['Group B'] = np.where(leaderboard['B Score'] <= leaderboard['Score to Beat'],
                                  leaderboard['Group B: Player'] + ": " + leaderboard['B Score'].astype(str),
                                  "~~" + leaderboard['Group B: Player'] + ": " + leaderboard['B Score'].astype(str) + "~~")

leaderboard['Group C'] = np.where(leaderboard['C Score'] <= leaderboard['Score to Beat'],
                                  leaderboard['Group C: Player'] + ": " + leaderboard['C Score'].astype(str),
                                  "~~" + leaderboard['Group C: Player'] + ": " + leaderboard['C Score'].astype(str) + "~~")

leaderboard['Group D'] = np.where(leaderboard['D Score'] <= leaderboard['Score to Beat'],
                                  leaderboard['Group D: Player'] + ": " + leaderboard['D Score'].astype(str),
                                  "~~" + leaderboard['Group D: Player'] + ": " + leaderboard['D Score'].astype(str) + "~~")

leaderboard['Group E'] = np.where(leaderboard['E Score'] <= leaderboard['Score to Beat'],
                                  leaderboard['Group E: Player'] + ": " + leaderboard['E Score'].astype(str),
                                  "~~" + leaderboard['Group E: Player'] + ": " + leaderboard['E Score'].astype(str) + "~~")

leaderboard['Group F'] = np.where(leaderboard['F Score'] <= leaderboard['Score to Beat'],
                                  leaderboard['Group F: Player'] + ": " + leaderboard['F Score'].astype(str),
                                  "~~" + leaderboard['Group F: Player'] + ": " + leaderboard['F Score'].astype(str) + "~~")                                  

leaderboard2 = []
leaderboard3 = []
cutVal = 2

for index, row in leaderboard.iterrows():
    a, b, c, d, e, f = row['A Score'], row['B Score'], row['C Score'], row['D Score'], row['E Score'], row['F Score']

    #a, b, c, d, e, f = -4, -5, -6, -1, -1, 0
    scores = [a,b,c,d,e,f]
    scoreLabels = ['A Score','B Score','C Score','D Score','E Score','F Score']
    scoreLetter = ['A','B','C','D','E','F']
    # combine scores and labels into a list of tuples
    
    scoreTuples = list(zip(scores, scoreLabels, scoreLetter))
    
    # sort the list of tuples based on the score value (in ascending order)
    sortedTuples = sorted(scoreTuples)
    
    # unpack the sorted tuples into two separate lists
    sortedScores = []
    sortedLabels = []
    sortedLetters = []
    for score, label, letter in sortedTuples:
        sortedScores.append(score)
        sortedLabels.append(label)
        sortedLetters.append(letter)
        
    for i in range(0,6):
        score = sortedScores[i]
        label = sortedLabels[i]
        letter = sortedLetters[i]
        field = "Group " + letter
        player = "Group " + letter + ": Player"
        
        if i <= 3:
            row[field] = row[player] + ": " + str(row[label])
        else:
            row[field] = "~~" + row[player] + ": " + str(row[label]) + "~~"
        
    
    if 3 > 2:
        cols = ['Entry', 'Score', 'Group A','Group B','Group C','Group D', 'Group E','Group F']
        playersMadeCut = (row['Group A: Player'] not in cut.keys()) + \
                            (row['Group B: Player'] not in cut.keys()) +\
                            (row['Group C: Player'] not in cut.keys()) +\
                            (row['Group D: Player'] not in cut.keys()) +\
                            (row['Group E: Player'] not in cut.keys()) +\
                            (row['Group F: Player'] not in cut.keys())#(a <= cutVal) + (b <= cutVal) + (c <= cutVal) + (d <= cutVal) + (e <= cutVal) + (f <= cutVal)
        print(row['Group A: Player'], playersMadeCut)
        if playersMadeCut < 4:
            for col in cols:
                if "~" not in str(row[col]):
                    row[col] = "~~" + str(row[col]) + "~~"
      
    leaderboard2.append(row.tolist())
        
leaderboard2DF = pd.DataFrame(leaderboard2)
leaderboard2DF.columns = leaderboard.columns
leaderboard = leaderboard2DF


            

    


leaderboard['Group B'] = leaderboard['Group B: Player'] + ": " + leaderboard['B Score'].astype(str)
leaderboard['Group C'] = leaderboard['Group C: Player'] + ": " + leaderboard['C Score'].astype(str)
leaderboard['Group D'] = leaderboard['Group D: Player'] + ": " + leaderboard['D Score'].astype(str)
leaderboard['Group E'] = leaderboard['Group E: Player'] + ": " + leaderboard['E Score'].astype(str)
leaderboard['Group F'] = leaderboard['Group F: Player'] + ": " + leaderboard['F Score'].astype(str)


"""










