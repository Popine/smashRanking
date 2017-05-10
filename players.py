from glicko2 import Player
from matches import getParticipants


#use ben's getParticipants and compares its dictionary values to the input dict's values 
#returns a list of players
def updatePlayerList(inputPlayerDict, inputDictionary):
    #read matches.txt file and updates dictionary
    for key, value in inputDictionary.items():
        if value not in inputPlayerDict:
            userChoice = input("New player: " + value + ". Add as new player or edit tag?\nType in add to add as new player, edit to edit the tag, or press any key to exit.\n")
            if userChoice.lower() == "add":
                inputPlayerDict[value] = Player(value)
            else:
                break
            if userChoice.lower() == "edit":
                newTag = input("Enter the new tag: ")
                if newTag not in inputPlayerDict:
                    inputPlayerDict[newTag] = Player(newTag)
                else: 
                    break
            
    return inputPlayerDict

#each line in input file is of format: playerA 1 playerB 2
#adds players' opponents, and results
#returns dictionary of player objects 
def addPlayerMatches(playerDict, playerList, matches):
    
    #open player match file to read
    matchOutput = open(matches, "r")
    matchOutput = matchOutput.read()
    #split each word
    matchOutput = matchOutput.split()
    matchOutput.pop(0)

    #if a score < 0 it is a dq? haven't done anything with it yet, just 
    #disregarded those matches for now
    for x in range(1, len(matchOutput), 4):
        if matchOutput[x] > matchOutput[x+2]:
            if matchOutput[x-1] in playerDict:
                #print("a")
                playerDict[matchOutput[x-1]].addMatch(matchOutput[x+1], 1)
            if matchOutput[x+1] in playerDict:
                    #print("b")
                    playerDict[matchOutput[x+1]].addMatch(matchOutput[x-1], 0)
                
        elif matchOutput[x] < matchOutput[x+2] and int(matchOutput[x]) >=0: 
            if matchOutput[x-1] in playerDict:
                    #print("c")
                playerDict[matchOutput[x-1]].addMatch(matchOutput[x+1], 0) 
            if matchOutput[x+1] in playerDict:
                    #print("d")
                playerDict[matchOutput[x+1]].addMatch(matchOutput[x-1], 1)
                
    return playerDict

#unfinished                    
def readElo(playerInfo):
    fileToOpen = open(playerInfo, "r")
    file = fileToOpen.read()
    file = file.splitlines()
    file.pop(0)
    
    for line in file:
        print(line[0])
    

    
def main():
    #input text file of existing players
    while(True):
        playerListFile = input("Enter the file name of your list of players: ")
        try:
            playerList = open(playerListFile, "r")
            break
        except:
            print("Cannot find the file.")
    
    #create a dict for existing players from input file
    playerDict = dict()
    #only works with input files having names separated by spaces atm
    playerList = playerList.read()
    playerList = playerList.splitlines()
    for line in playerList:
        for player in line.split():
            if player.lower() not in playerDict:
                playerDict[player] = Player(player)    

    #get rid of hardcode later
    name = "edmmelee-SmashAtCASE042817Melee"
    apiKey = "iRZrPhoDkyLV2xFXyUuJ5pVauosMlZPGMMmCdSaE"
   
    players = getParticipants(name, apiKey)
    updatePlayerList(playerDict, players)
    
    #update player list text file
    outputFile = open(playerListFile, "w")
    outputFile.write("")
    outputFile.close()
    outputFile = open(playerListFile, "a")
    for player in playerDict:
        #print(player)
        outputFile.write(player + "\n")
    outputFile.close()


    matchInput = input("Enter the name of your matches file: " )
    playerDict = addPlayerMatches(playerDict, playerDict, matchInput)
    
    
    #print player objects to output file    
    file = open("text.txt", "w")
    file.write("")
    file.close()
    file = open("text.txt", "a")

    outputList = list()
    for player in playerDict:
        atts = (playerDict[player].getAttributes())
        outputList.append(atts)
        
    file.write("name, rating, rd, vol, opponentList, resultList(0 = loss, 1 = win)\n")
    
    for line in outputList:
        file.write(str(line).replace("(", "").replace(")", "").replace("'", "").replace(",", ""))
        file.write("\n")
    file.close()    
    
    readElo("text.txt")
    
main()

    
