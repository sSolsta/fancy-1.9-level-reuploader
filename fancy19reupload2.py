import traceback
from getpass import getpass
from lib import gjservers, gjcrypt, gjclasses, glowdotmerger

gdps = gjservers.Server("http://gdps.nettik.co.uk/database/", name = "1.9")
mainGD = gjservers.Server("http://www.boomlings.com/database/", name = "2.1")

def askYN(question, blankLine = True):
    if blankLine:
        print()
    ans = input(f"{question} (enter y/n): ").lower()
    if ans in ("y", "yes"):
        return True
    elif ans in ("n", "no"):
        return False
    else:
        print("Invalid response")
    return askYN(question)
    
def askYNInfo(question, info, blankLine = True):
    if blankLine:
        print()
    ans = input(f"{question} (enter y/n or ? for more info): ").lower()
    if ans in ("y", "yes"):
        return True
    elif ans in ("n", "no"):
        return False
    elif ans == "?":
        print(info)
    else:
        print("Invalid response")
    return askYNInfo(question, info)

def askLevel():
    print()
    try:
        levelID = int(input(f"Enter the ID of the {gdps.name} level you wish to reupload: "))
    except ValueError:
        print("Invalid response")
        return askLevel()
    if levelID < 0:
        print("Invalid response")
        return askLevel()
    
    level = gdps.req("downloadGJLevel.php", params = {"levelID": levelID})
    if not level:
        print(f"Could not find level {levelID}, maybe you mistyped the ID.")
        return askLevel()
    
    level = gjclasses.GJLevel(gjcrypt.parseKV(level.split("#")[0]))
    
    if askYN(f"Retrieved level: {level[2]}. Is this correct?", blankLine = False):
        return level
    else:
        return askLevel()

def askPosValue(question, func, blankLine = True):
    if blankLine:
        print()
    val = input(question)
    if not val:
        return
    try:
        val = func(val)
    except ValueError:
        print("Invalid Response")
        return askPosValue(question, func)
    if val < 0:
        print("Invalid Response")
        return askPosValue(question, func)
    return val

def gjLogin(server, playerID = None):
    print()
    username = input(f"Your {server.name} username: ")
    password = getpass(f"Your {server.name} password: ")
    params = {
        "userName": username,
        "password": password,
        "udid": gjcrypt.makeUUID(),
        "secret": "Wmfv3899gc9",
        }
    response = server.req("accounts/loginGJAccount.php", params, failOnNeg = False)
    if not response:
        print("Failed to log in")
        return gjLogin(server, playerID = playerID)
    elif response == "-1":
        print("Incorrect login")
        return gjLogin(server, playerID = playerID)
    elif response == "-12":
        print("Rate limited, try using a VPN or try again later")
        return gjLogin(server, playerID = playerID)
        
    response = {k: v for k,v in zip(("accountID", "playerID"), response.split(","))}
    response["username"] = username
    response["password"] = password
    
    if playerID and (response["playerID"] not in (playerID, 6273)):
        print("You must log into the account that uploaded the level")
        return gjLogin(server, playerID = playerID)
    
    print("Successfully logged in")
    return response

def uploadLevel(params):
    response = mainGD.req("uploadGJLevel21.php", params)
    print()
    if response:
        print(f"Level successfully reuploaded with ID {response}")
    elif askYN("Level failed to upload. Would you like to try again?"):
        return uploadLevel(params)
    else:
        print("Level upload failed")
        
    
# =====================================================================================================================
# main
try:
    print("=== Fancy 1.9 Level Reuploader v2 ===")
    print("Created by sSolsta")
    
    level = askLevel()
    gjLogin(gdps, playerID = level[6])
    
    loginInfo = gjLogin(mainGD)
    
    if askYNInfo("Fix layers?", "2.1 displays layers differently, which can break the visuals of some levels. This option changes the layers of some objects to replicate 1.9 behaviour"):
        print("Fixing layers...")
        level.unpack()
        for obj in level.objects:
            obj.fixLayer()
        print("Layers fixed")
    
    if askYNInfo("Fix colour bugs?", "This fixes a 2.1 bug where the colour of xstep wavey platforms doesn't work properly when set to black. It also replicates a 1.9 bug where certain 3D objects always display as white (where they should be obj colour)"):
        print("Fixing colour bugs...")
        level.unpack()
        for obj in level.objects:
            obj.fixColour()
        print("Colour bugs fixed")
    
    if askYNInfo("Merge glow dots?", "This finds and replaces glow dots (4 glow corners around a single point) with the 2.1 glow dot object, reducing the object count. May take upwards of 10 seconds on high object levels"):
        level.unpack()
        level.objects = glowdotmerger.theFuckening(level.objects)
    
    if askYN("Change the song?"):
        songID = askPosValue("Enter the song ID (leave blank to cancel): ", int, blankLine = False)
        if songID:
            level.unpack()
            level[35] = songID
            offset = askPosValue("Enter the offset (leave blank to keep it the same): ", float, blankLine = False)
            if offset is not None:
                level.startObj["kA13"] = offset
            level.startObj["kA15"] = int(askYN("Fade in?", blankLine = False))
            level.startObj["kA16"] = int(askYN("Fade out?", blankLine = False))
        else:
            print("Cancelled")
    
    params = level.uploadInfo()
    
    params["accountID"] = loginInfo["accountID"]
    params["gjp"] = gjcrypt.makeGJP(loginInfo["password"])
    params["userName"] = loginInfo["username"]
    print()
    levelName = input(f"Enter the name of the reuploaded level (keep blank to keep it as '{level[2]}'): ")
    params["unlisted"] = int(askYN("Upload as unlisted?", blankLine = False))
    if levelName:
        params["levelName"] = levelName
    
    
    uploadLevel(params)
    input("Press enter to exit")
    
except Exception:
    print()
    print("An unexpected error occurred")
    print("Please show the error below to sSolsta so that she can fix the issue\n")
    traceback.print_exc()
    input()