"""fancy 1.9 reuploader v2.113

lets you reupload 1.9 levels to 2.1
with extra stuff if you want it

created by ssolsta 2021-2022
more info: https://github.com/sSolsta/fancy-1.9-level-reuploader/
"""
import traceback
from getpass import getpass
from lib import gjservers, gjcrypt, gjclasses, glowdotmerger

gdps = gjservers.Server("http://gdps.nettik.co.uk/database/", name = "1.9")
mainGD = gjservers.Server("http://www.boomlings.com/database/", name = "2.1")


def ask_yn(question, *, info = None, blank_line = True):
    """asks a yes or no question, and returns the result as a bool"""
    if blank_line:
        print()
    if info is None:
        prompt = f"{question} (enter y/n): "
    else:
        prompt = f"{question} (enter y/n or ? for more info): "
    ans = input(prompt).lower()
    if ans in {"y", "yes"}:
        return True
    elif ans in {"n", "no"}:
        return False
    elif info is not None and ans == "?":
        print(info)
    else:
        print("Invalid response")
    return ask_yn(question, info = info)


def ask_level():
    """attempts to retrieve the 1.9 level specified by the user"""
    level_id = ask_val(
        f"Enter the ID of the {gdps.name} level you wish to reupload: ",
        cond = lambda x: x > 0,
        oftype = int,
        )
    
    level = gdps.req("downloadGJLevel.php", params = {"levelID": level_id})
    if not level:
        print(f"Could not find level {level_id}, maybe you mistyped the ID.")
        return ask_level()
    
    level = gjclasses.GJLevel(gjcrypt.decode_kv(level.split("#")[0]))
    if ask_yn(f"Retrieved level: {level.name}. Is this correct?", blank_line = False):
        return level
    else:
        return ask_level()


def ask_val(question, cond, *, oftype = int, allow_empty = False, blank_line = True):
    """asks for a value of a specified type under a specified
    condition
    """
    if blank_line:
        print()
    val = input(question)
    if allow_empty and not val:
        return
    try:
        val = oftype(val)
    except ValueError:
        print("Invalid Response")
        return ask_val(question, cond, oftype = oftype, allow_empty = allow_empty)
    if not cond(val):
        print("Invalid Response")
        return ask_val(question, cond, oftype = oftype, allow_empty = allow_empty)
    return val


def gj_login(server, *, player_id = None):
    """requests login information and attempts to log into the
    specified gd server
    """
    print()
    username = input(f"Your {server.name} username: ")
    password = getpass(f"Your {server.name} password: ")
    params = {
        "userName": username,
        "password": password,
        "udid": gjcrypt.make_uuid(),
        "secret": "Wmfv3899gc9",
        }
    response = server.req("accounts/loginGJAccount.php", params, fail_on_neg = False)
    if not response:
        print("Failed to log in")
        return gj_login(server, player_id = player_id)
    elif response == "-1":
        print("Incorrect login")
        return gj_login(server, player_id = player_id)
    elif response == "-12":
        print("Rate limited, try using a VPN or try again later")
        return gj_login(server, player_id = player_id)
        
    login_info = {
        "username": username,
        "password": password,
        }
    login_info["account_id"], login_info["player_id"] = response.split(",")
    if player_id and (login_info["player_id"] not in {player_id, "6273"}):
        print("You must log into the account that uploaded the level")
        return gj_login(server, player_id = player_id)
    
    print("Successfully logged in")
    return login_info


def upload_level(params):
    """uploads a gd level to 2.1 with the specified parameters"""
    response = mainGD.req("uploadGJLevel21.php", params)
    print()
    if response:
        print(f"Level successfully reuploaded with ID {response}")
    elif ask_yn("Level failed to upload. Would you like to try again?"):
        return upload_level(params)
    else:
        print("Level upload failed")


def main():
    """main function"""
    print("=== Fancy 1.9 Level Reuploader v2.113 ===")
    print("Created by sSolsta")
    # retrieving level and login information
    level = ask_level()
    gj_login(gdps, player_id = level.uploader_player_id)
    login_info = gj_login(mainGD)
    # level processing options
    if ask_yn("Fix layers?",
              info = ("2.1 displays layers differently, which can break the visuals of some "
                      "levels. This option changes the layers of some objects to replicate 1.9 "
                      "behaviour")):
        print("Fixing layers...")
        level.unpack()
        for obj in level.objects:
            obj.fix_layer()
        print("Layers fixed")
    
    if ask_yn("Fix visual bugs?",
              info = ("This fixes minor visual discrepancies between 1.9 and 2.1, such as some "
                      "objects having incorrect colours")):
        print("Fixing visual bugs...")
        level.unpack()
        for obj in level.objects:
            obj.fix_visual_bugs()
        print("Visual bugs fixed")
    
    if ask_yn("Merge glow dots?",
              info = ("This finds and replaces glow dots (4 glow corners around a single point) "
                      "with the 2.1 glow dot object, reducing the object count. May take upwards "
                      "of 10 seconds on high object levels")):
        level.unpack()
        level.objects = glowdotmerger.the_fuckening(level.objects)
    # change song
    if ask_yn("Change the song? (Only allows for newgrounds songs and not main level songs)"):
        song_id = ask_val(
            "Enter the song ID (leave blank to cancel): ",
            cond = lambda x: x > 0,
            oftype = int, allow_empty = True, blank_line = False,
            )
        if song_id:
            level.unpack()
            level.custom_song_id = song_id
            offset = ask_val(
                f"Enter the offset (leave blank to keep it as {level.song_offset}): ",
                cond = lambda x: x >= 0,
                oftype = float, allow_empty = True, blank_line = False,
                )
            if offset is not None:
                level.song_offset = offset
            level.song_fadein = ask_yn("Fade in?", blank_line = False)
            level.song_fadeout = ask_yn("Fade out?", blank_line = False)
        else:
            print("Cancelled")
    # retrieve upload parameters and upload level
    params = level.upload_info()
    params["accountID"] = login_info["account_id"]
    params["gjp"] = gjcrypt.make_gjp(login_info["password"])
    params["userName"] = login_info["username"]
    print()
    level_name = input(
        f"Enter the name of the reuploaded level (keep blank to keep it as '{level.name}'): "
        )
    params["unlisted"] = int(ask_yn("Upload as unlisted?", blank_line = False))
    if level_name:
        params["levelName"] = level_name
    upload_level(params)
    input("Press enter to exit")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print()
        print("An unexpected error occurred")
        print("Please show the error below to sSolsta so that she can fix the issue")
        print()
        traceback.print_exc()
        input()
