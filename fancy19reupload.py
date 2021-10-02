import argparse
import gd
import sys
import traceback
from getpass import getpass
from lib import classes, gdCrypto, gdRequest, glowDotMerger, objectTypes

onePointNine = gdRequest.gdServer("http://gdps.nettik.co.uk/database/")

def askForLevel():
    print()
    try:
        levelID = int(input("Please input the ID of the 1.9 level you wish to upload to 2.1: "))
    except ValueError:
        print("That is not a valid level ID")
        return askForLevel()
    
    level = onePointNine.request("downloadGJLevel.php", {"levelID": levelID})
    if not level:
        print("Could not find the specified level, maybe you mistyped the ID.")
        return askForLevel()
    
    level = onePointNine.parseKV(level.split("#")[0])
    print(f"Retrieved level: {level[2]}. If this is not the level you intended to reupload, close the program and try again.")
    return level

def loginOnePointNine(playerID):
    print()
    params = {
        "udid": onePointNine.uuid, # yeah confusing
        "userName": input("Your 1.9 username: "), # why the fuck would you camelcase username
        "password": getpass("Your 1.9 password: "),
        }
    
    response = onePointNine.request("accounts/loginGJAccount.php", params)
    if not response:
        print("Could not log into the specified account, maybe you made a typo.")
        loginOnePointNine(playerID)
        return
    
    if response.split(",")[1] == playerID:
        print("Successfully logged in")
        return
    else:
        print("You must log into the account that the level is uploaded onto.")
        loginOnePointNine(playerID)

def loginTwoPointOne():
    print()
    username = input("Your 2.1 username: ")
    password = getpass("Your 2.1 password: ")
    
    try:
        client.run(client.login(username, password))
    except gd.errors.LoginFailure:
        print("Could not log into the specified account, maybe you made a typo.")
        loginTwoPointOne(client)

def askForMode(printInfo = True):
    print()
    if printInfo:
        print("MODES:")
        print("[A] - Direct reupload (no level manipulation)")
        print("[B] - Layer fixing")
        print("[C] - Glow dot merging")
        print("[D] - Layer fixing & glow dot merging")
        print()
        print("If you are intending to reupload this level back to 1.9, choose [A].")
        print("Note that glow dot merging is experimental, could break the level's decoration, and could take a while.")
        print()
    choice = input("Select Mode: ").upper()
    
    # i made it unclear if you should type '[A]' or 'A' so instead of clarifying i made it so that you can do both
    if choice in ("A", "[A]"):
        return 0b00
    elif choice in ("B", "[B]"):
        return 0b01
    elif choice in ("C", "[C]"):
        return 0b10
    elif choice in ("D", "[D]"):
        return 0b11
    else:
        print("Please choose one of the four options.")
        askForMode(False)

def askForSongID(printInfo = True):
    print()
    if printInfo:
        print("The song used in the level appears to be a non-newgrounds song.")
    try:
        song = int(input("Please provide the ID of a replacement song: "))
    except ValueError:
        print("That is not a valid song ID.")
        return askForSongID(False)
    if song < 1:
        print("That is not a valid song ID.")
        return askForSongID(False)
    if song >= 5105655:
        print("That is a non-newgrounds song.")
        return askForSongID(False)
    return song

def tryUploadLevel(level, song):
    try:
        client.run(level.upload(**song))
    except gd.errors.MissingAccess:
        choice = input("Unable to upload level. Press enter to try again, or type 'CANCEL' to give up and exit the program. ").upper()
        if choice == "CANCEL":
            sys.exit()
        tryUploadLevel(level)

def fixObjectLayer(obj):
    objType = objectTypes.objectTypes.get(obj.getObjID(), 1)
    if objType == 1:
        pass
    elif objType in (2, 3):
        # the specific default colour here does not matter, we only care if it's one of the three or not
        default = 1 if objType == 3 else 420
        layer = 3 if (obj.getColour(default = default) in (1, 2, 5)) else 1
        obj.setLayer(layer)
    elif objType == 4:
        obj.setLayer(1)
    elif objType == 5:
        obj.setLayer(4)

if __name__ == "__main__":
    print("=== Fancy 1.9 Level Reuploader ===")
    print("Created by sSolsta")
    try:
        level = askForLevel()
        loginOnePointNine(level[6])
        mode = askForMode()
        levelString = gdCrypto.decodeLevelString(level[4])
        
        if mode:
            split = levelString.split(";")
            header = split.pop(0)
            objects = [classes.LevelObject().fromString(x) for x in split if x]
            
            if mode & 0b01:
                print("Fixing object layering...")
                for obj in objects:
                    fixObjectLayer(obj)
                print("Layers fixed")
            
            if mode & 0b10:
                print("Merging glow dots... (this may take a while)")
                objects = glowDotMerger.merge(objects, logging = True)
                print("Glow dots merged.")
            
            levelString = ";".join((
                header,
                ";".join([x.toString() for x in objects]),
                "" # janky way of adding extra semicolon to end of string
                ))
        
        client = gd.Client()
        loginTwoPointOne()
        
        levelName = input(f"Enter the name of the reuploaded level (keep blank to keep it as '{level[2]}'): ")
        levelName = levelName if levelName else level[2]
        
        song = {
            "track": int(level[12]),
            "song_id": int(level[35])
            }
        
        if song["song_id"] >= 5105655:
            song["song_id"] = askForSongID()
        
        # i hope i did this right
        levelToUpload = gd.Level(
            client = client,
            name = levelName,
            id = 0,
            version = int(level[5]),
            length = int(level[15]),
            is_auto = 0,
            two_player = bool(int(level[31])),
            objects = int(level[45]),
            password = level[27][1:] if len(level[27]) == 7 else None,
            copyable = bool(int(level[27])),
            data = levelString,
            description = level[3],
            )
        
        tryUploadLevel(levelToUpload, song)
        print(f"Level uploaded with ID {levelToUpload.id}")
        input("Press enter to exit")
    except Exception:
        print()
        print("An unexpected error occurred when attempting to execute the program")
        print("Please provide information about the error to sSolsta so that he can fix this issue")
        traceback.print_exc()
        input()
