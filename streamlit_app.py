import streamlit as st
#from streamlit_datalist import stDatalist
import pandas as pd
import itertools
import golfScores
import numpy as np
import re

st.set_page_config(layout="wide")
path = r"./RawGolferPicks.csv"
picks = pd.read_csv(path)

st.image("logo.png")
st.title("Hack Golf Pools")

leaderTab, entryTab, admin = st.tabs(['Leaderboard', 'Entry', 'Admin'])

with leaderTab:
    config = golfScores.read_config()
    entryLock, tournamentDay, cutVal = config.loc['entryLock']['value'], config.loc['tournamentDay']['value'], config.loc['cutValue']['value']
    
    if entryLock == 1:
        playerScores, eventTitle, cutWD = golfScores.getScores()
        leaderboard = golfScores.getLeaderboard(playerScores)
        
        rankIndex = range(1,len(leaderboard)+1)
        leaderboard['Rank'] = leaderboard['Score'].rank(method='min').astype(int)#rankIndex
        
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
        for index, row in leaderboard.iterrows():
            a, b, c, d, e, f = int(row['A Score']), row['B Score'], row['C Score'], row['D Score'], row['E Score'], row['F Score']
    
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
                score = int(sortedScores[i])
                label = sortedLabels[i]
                letter = sortedLetters[i]
                field = "Group " + letter
                player = "Group " + letter + ": Player"
                cut = False
                
                if re.sub(r" \([^)]*\)", "", row[player]) in cutWD.keys():
                    cut = True
                
                if i <= 3:
                    print(player)
                    if cut:
                        row[field] = row[player] + ": " + "CUT"
                    else:
                        row[field] = row[player] + ": " + str(int(row[label]))
                else:
                    if cut:
                        row[field] = "~" + row[player] + ": " + "CUT"
                    else:
                        row[field] = "~" + row[player] + ": " + str(int(row[label]))
                
            
            #if 3 > 2:
            cols = ['Entry', 'Score', 'Group A','Group B','Group C','Group D', 'Group E','Group F']
            playersMadeCut = (re.sub(r" \([^)]*\)", "", row['Group A: Player']) not in cutWD.keys()) + \
                                (re.sub(r" \([^)]*\)", "", row['Group B: Player']) not in cutWD.keys()) +\
                                (re.sub(r" \([^)]*\)", "", row['Group C: Player']) not in cutWD.keys()) +\
                                (re.sub(r" \([^)]*\)", "", row['Group D: Player']) not in cutWD.keys()) +\
                                (re.sub(r" \([^)]*\)", "", row['Group E: Player']) not in cutWD.keys()) +\
                                (re.sub(r" \([^)]*\)", "", row['Group F: Player']) not in cutWD.keys())#(a <= cutVal) + (b <= cutVal) + (c <= cutVal) + (d <= cutVal) + (e <= cutVal) + (f <= cutVal)
                    
            
            #print(row['Entry'], playersMadeCut)
            if playersMadeCut < 4:
                for col in cols:
                    if "~" not in str(row[col]):
                        if col == 'Score':
                            row[col] = str(int(row[col]))
                        else:
                            row[col] = "~" + str(row[col])
              
            leaderboard2.append(row.tolist())
                
        leaderboard2DF = pd.DataFrame(leaderboard2)
        leaderboard2DF.columns = leaderboard.columns
        leaderboard = leaderboard2DF
        
        cols = ['Rank', 'Entry', 'Score', 'Group A','Group B','Group C','Group D', 'Group E','Group F']
        markdownLeader = leaderboard[cols]
        markdownLeader['Score'] = np.where(markdownLeader['Entry'].str.contains("~"), "~"+markdownLeader['Score'].astype(int).astype(str)+"~",markdownLeader['Score'].astype(int).astype(str))
        
        ranks = markdownLeader['Rank'].unique().tolist()
        # convert dataframe to markdown table string
        def color_coding(row):
            hexList = ['#807fff','#7fbfff','#7fffff','#7eff80','#beff7f','#feff7f',   '#9b6b71','#c04e5c','#e4334a']
            
            rowRank = ranks.index(row['Rank'])
            if rowRank < len(hexList):
                out = ['background-color:' + str(hexList[rowRank])] * len(row)
            else:
                out = ['background-color:' + str(hexList[-1])] * len(row)
            
            
            if (rowRank % 2) == 0:
               out = ['background-color:' + str('#2a475e')] * len(row)
               
               for c in cols:
                   if "~" in str(row[c]):
                       out[cols.index(c)] += ';color:#425b7f'
            else:
               out = ['background-color:' + str('#1f4f2d')] * len(row)
               for c in cols:
                   if "~" in str(row[c]):
                       out[cols.index(c)] += ';color:#367f47'
            
                    
            
            return out#['background-color:#2a4858'] * len(row) if "Jon Rahm" in row['Group A'] else ['background-color:green'] * len(row)
    
        # Apply the formatting using the color_coding function
        container_style = '''
        width: 100%;
        height: 300;
        overflow-y: auto;
        '''
        styled_df = markdownLeader.style.apply(color_coding, axis=1)
    
        st.write(styled_df, unsafe_allow_html=True, style=container_style)
        
        # Set the style of the Player column to right-align the text
        playerScores.index = playerScores['Score'].rank(method='min').astype(int)#rankIndex
        #styled_df = playerScores.style.set_properties(**{'text-align': 'right'}, subset=['Player'])
        
        # Convert the styled data frame to an HTML table and remove the index column
        #html = styled_df.to_html(index=False)
        
        # Display the HTML table using st.write()
        st.write(playerScores)
        
    else:
        st.write("Leaderboard Hidden Until Tournament Start")
    

with entryTab:
    config = golfScores.read_config()
    entryLock, tournamentDay, cutVal = config.loc['entryLock']['value'], config.loc['tournamentDay']['value'], config.loc['cutValue']['value']
    playerScores, eventTitle, cutWD = golfScores.getScores()
    golfers = playerScores['Player'].unique()
    
    st.subheader("Instructions")
    instructionExpander = st.expander("Expand/Collapse", expanded = False)
    with instructionExpander:
        instructionString = "##### Entry:\n1. Use the form below to submit your entry.\n2. Choose one (1) player from each group, or “write-in” a player of your choice that is NOT listed below. \n3. You must have four (4) players make the cut to be eligible. \n ------------------------------------------- \n##### Payout:\n1. The winner takes all minus 2nd and 3rd:\n2. 2nd Place gets \$100.00\n3. 3rd Place gets \$25.00. \n ------------------------------------------- \n##### Tiebreakers:\n1. Final winning score in relation to par (Example -11 format), closest to the winning score wins; if any entries have the same closest winning score, then we’ll move to tiebreaker 2 \n2. Pick the winner (winner MUST BE one of your “Group” picks), closest on the final scoreboard to the winner of the Masters. \n3. If after tiebreakers 1 and 2 there is still no winner, then all entries that match the \#1 and \#2 tiebreaker will share the top prize of Winner takes all minus \$100 for 2nd place and \$25 for 3rd Place.\n4. Note. 2nd and 3rd Place will be determined after the winner or winners is determined. \n ------------------------------------------- \n##### Buy-In:\n1. \$25 Entry fee\n2. Have your entry and payment submitted no later than 9pm CST Wednesday before tournament begins.\n3. Payment is accepted via Venmo to MGMELENDEZ, see our Contact Us page for more information."
        st.write(instructionString, unsafe_allow_html=True)
    
    st.subheader("Entry")
    if entryLock == 0:
        optionsA, optionsB, optionsC, optionsD, optionsE, optionsF = golfScores.read_groups()
        
        allOptionsRaw = list(itertools.chain(optionsA, optionsB, optionsC, optionsD, optionsE, optionsF))
        allOptions = []
        for option in allOptionsRaw:
            if option != "" and option != "Write In...":
                allOptions.append(option)
        
        with st.form("entryForm"):
            entryName = st.text_input("Enter Entry Name", key="entryName")
            
            expanderA = st.expander("Group A", expanded = True)
            with expanderA:
                col1, col2 = st.columns(2)
                groupA = col1.selectbox("Group A Selection", options=optionsA, key = 'selectA')
                groupA_write = col2.multiselect('Optional Write In', golfers, max_selections=1, key="writeGA")
                
                
            expanderB = st.expander("Group B", expanded = True)
            with expanderB:
                col1, col2 = st.columns(2)
                groupB = col1.selectbox("Group B Selection", options=optionsB, key = 'selectB')
                groupB_write = col2.multiselect('Optional Write In', golfers, max_selections=1, key="writeGB")
                
            expanderC = st.expander("Group C", expanded = True)
            with expanderC:
                col1, col2 = st.columns(2)
                groupC = col1.selectbox("Group C Selection", options=optionsC, key = 'selectC')
                groupC_write = col2.multiselect('Optional Write In', golfers, max_selections=1, key="writeGC")
                
            expanderD = st.expander("Group D", expanded = True)
            with expanderD:
                col1, col2 = st.columns(2)
                groupD = col1.selectbox("Group D Selection", options=optionsD, key = 'selectD')
                groupD_write = col2.multiselect('Optional Write In', golfers, max_selections=1, key="writeGD")
                
            expanderE = st.expander("Group E", expanded = True)
            with expanderE:
                col1, col2 = st.columns(2)
                groupE = col1.selectbox("Group E Selection", options=optionsE, key = 'selectE')
                groupE_write = col2.multiselect('Optional Write In', golfers, max_selections=1, key="writeGE")
                
            expanderF = st.expander("Group F", expanded = True)
            with expanderF:
                col1, col2 = st.columns(2)
                groupF = col1.selectbox("Group F Selection", options=optionsF, key = 'selectF')
                groupF_write = col2.multiselect('Optional Write In', golfers, max_selections=1, key="writeGF")
                
            submit = st.form_submit_button("Submit Entry")
            if submit:
                validEntry = True
                
                existingEntries = picks['Entry'].unique()
                if entryName in existingEntries:
                    validEntry = False
                    st.write("Entry Already Exists")
                
                
                if groupA_write:
                    groupA = groupA_write[0]
                #else:
                #    groupA = groupA[0]
                    
                
                if groupA[0] == "":
                    validEntry = False
                    st.write("Please Make a Group A Selection")
                    
                    
                    
                if groupB_write:
                    groupB = groupB_write[0]
                #else:
                #    groupB = groupB[0]
                    
                if groupB == "":
                    validEntry = False
                    st.write("Please Make a Group B Selection")
                    
                    
                    
                if groupC_write:
                    groupC = groupC_write[0]
                #else:
                #    groupC = groupC[0]
                    
                if groupC[0] == "":
                    validEntry = False
                    st.write("Please Make a Group C Selection")
                    
                    
                    
                if groupD_write:
                    groupD = groupD_write[0]
                #else:
                #    groupD = groupD[0]
                    
                if groupD[0] == "":
                    validEntry = False
                    st.write("Please Make a Group D Selection")
                    
                    
                    
                if groupE_write:
                    groupE = groupE_write[0]
                #else:
                #    groupE = groupE[0]
                    
                if groupE[0] == "":
                    validEntry = False
                    st.write("Please Make a Group E Selection")
                    
                    
                    
                if groupF_write:
                    groupF = groupF_write[0]
                #else:
                #    groupF = groupF[0]
                    
                if groupF[0] == "":
                    validEntry = False
                    st.write("Please Make a Group F Selection")
                    
                    
                    
                if groupA in allOptions and groupA not in optionsA:
                    validEntry = False
                    st.write("Group A write in available in another group")
                    
                if groupB in allOptions and groupB not in optionsB:
                    validEntry = False
                    st.write("Group B write in available in another group")
                    
                if groupC in allOptions and groupC not in optionsC:
                    validEntry = False
                    st.write("Group C write in available in another group")
                    
                if groupD in allOptions and groupD not in optionsD:
                    validEntry = False
                    st.write("Group D write in available in another group")
                    
                if groupE in allOptions and groupE not in optionsE:
                    validEntry = False
                    st.write("Group E write in available in another group")
                    
                if groupF in allOptions and groupF not in optionsF:
                    validEntry = False
                    st.write("Group F write in available in another group")
                    
                    
                if validEntry:
                    #newEntry = {"Entry":['test'], "Group A":['gol1'], "Group B":['gol2'],
                    #            "Group C": ['gol3'], "Group D": ['gol4'], "Group E": ['gol5'],
                    #            "Group F": ['gol6']}
                    newEntry = {"Entry":[entryName], 
                                "Group A":[groupA],
                                "Group B":[groupB], 
                                "Group C":[groupC], 
                                "Group D":[groupD], 
                                "Group E":[groupE], 
                                "Group F":[groupF]}
                    
                    newEntryDict = pd.DataFrame.from_dict(newEntry)
                    picks = pd.concat([picks, newEntryDict])  
                    path = r"./RawGolferPicks.csv"
                    picks.to_csv(path, index = False)
                    
                    #entryString = groupA + '\n'  + groupB
                    st.write("Entry Submitted Successfully!")
                    st.write("Group A: " + groupA)
                    st.write("Group B: " + groupB)
                    st.write("Group C: " + groupC)
                    st.write("Group D: " + groupD)
                    st.write("Group E: " + groupE)
                    st.write("Group F: " + groupF)
                else:
                    st.write("Entry Submission Failed")
    else:
        st.write("Entries are not currently being accepted")
        
    
with admin:
    # Define your password
    password = "bilbobaggins"
    
    # Create the password field
    password_input = st.text_input("Enter Password", type="password")
    #loginButton = st.button("Login")
    
    # Create the placeholder for the hidden widget
    groupPlayers = st.empty()
    
    #if loginButton:
        # Check if the password is correct and show the hidden widget
    if password_input == password:
        config = golfScores.read_config()
        
        
        lockedSetting = config.loc['entryLock']['value']
        if lockedSetting == 1:
            lockedSetting = 'New Entries Locked'
        else:
            lockedSetting = 'New Entries Accepted'
            
        tournamentDay = config.loc['tournamentDay']['value']
        cutValue = config.loc['cutValue']['value']
        # Clear the password input field to hide it
        password_input = st.empty()
        #loginButton = st.empty()
        
        with st.form("adminForm"):
            st.subheader("App Settings")
            # App Phase Widge
            #st.text(")
            options = ['New Entries Accepted', "New Entries Locked"]
            entryLocked = st.radio("Accept New Entries?", 
                                   options, 
                                   index=options.index(lockedSetting),
                                   horizontal=True)
    
        
            # App Phase Widget
            #st.text("Tournament Day")
            options = [1, 2, 3, 4]
            newTournamentDay = st.radio("Tournament Day", options, index=options.index(tournamentDay), horizontal=True)
            
            #Cut Value
            newCutValue = st.slider("Cut Value", min_value = -5, max_value = 5,step = 1, value=int(cutValue))
            #newCutValue = st.text_input("Enter Cut", value = cutValue)
            saveButton = st.form_submit_button("Save Settings")
            
            if saveButton:
                if entryLocked == 'New Entries Locked':
                    entryLock_setting = 1
                    tempEntry = 'New Entries Locked'
                else:
                    entryLock_setting = 0
                    tempEntry = 'New Entries Accepted'
                    
                config.loc['entryLock']['value'] = entryLock_setting
                config.loc['tournamentDay']['value'] = newTournamentDay
                config.loc['cutValue']['value'] = newCutValue
                
                golfScores.write_config(config)
                st.write("Settings Saved")
                st.write("Entries: ", tempEntry)
                st.write("Tournament Day: ", newTournamentDay)
                st.write("Cut Value: ", newCutValue)
                st.experimental_rerun()
            

    
        # Create the file uploader widget
        #st.text("Upload Player Groupings as .csv")
        st.subheader("File Upload")
        groupPlayers = st.file_uploader("Upload Player Groupings as .csv", type=["csv"])
        uploadButton = st.button("Upload")
        
        # Process the uploaded file
        if uploadButton:
            if groupPlayers is not None:
                # Add code to process the file here
                groupsDF = pd.read_csv(groupPlayers)
                path = r"./groups.csv"
                groupsDF.to_csv(path, index = False)
                st.write("You uploaded the following file:", groupPlayers.name)
            
        
        
        
    else:
        # If the password is incorrect, clear the placeholder and leave the password input field visible
        st.write("Incorrect Password")
    

