"""fancy 1.9 reuploader v2.15

lets you reupload 1.9 levels to 2.1
with extra stuff if you want it

created by ssolsta 2021-2023
more info: https://github.com/sSolsta/fancy-1.9-level-reuploader/
"""

import multiprocessing
import traceback
import webbrowser
import time
from datetime import datetime
from lib import gjservers, gjcrypt, gjclasses, glowdotmerger
from lib.github import github_request, RELEASE_LINK
from lib.askpass import askpass
from urllib.error import HTTPError

VERSION_TAG = "v2.17"

gdps = gjservers.Server("https://19gdps.com/gdapi/", name = "1.9")
mainGD = gjservers.Server("https://www.boomlings.com/database/", name = "2.2")

# setting the infos i use in ask_yn as constants here bc it looks
# ugly setting them inline
LAYER_FIX_INFO = (
  "2.2 displays layers differently, which can break the visuals of some levels. This option "
  "changes the layers of some objects to replicate 1.9 behaviour"
  )
VISUAL_BUGS_INFO = (
  "This fixes minor visual discrepancies between 1.9 and 2.2, such as some objects having "
  "incorrect colours"
  )
GLOW_DOT_INFO = (
  "This finds and replaces glow dots (4 glow corners around a single point) with the 2.1 glow "
  "dot object, reducing the object count. May take upwards of 10 seconds on high object levels"
  )
HITBOX_FIX_INFO = (
  "Some objects have different hitboxes between 2.2 and 1.9. This option uses invisible "
  "objects to make the hitboxes in 2.2 match what they are in 1.9"
  )


def ask_yn(question, *, info=None, blank_line=True):
  """asks a yes or no question, and returns the result as a bool"""
  if blank_line:
    print()
  if info is None:
    prompt = f"{question} (enter y/n): "
  else:
    prompt = f"{question} (enter y/n or ? for more info): "
  ans = input(prompt).lower()
  if ans in {"y", "yes", "yeah", "nah yeah", "nah, yeah", "yuh-uh"}:
    return True
  elif ans in {"n", "no", "nah", "yeah nah", "yeah, nah", "nuh-uh"}:
    return False
  elif info is not None and ans == "?":
    print(info)
  else:
    print("Invalid response")
  return ask_yn(question, info=info)


def ask_level():
  """attempts to retrieve the 1.9 level specified by the user"""
  level_id = ask_val(
    f"Enter the ID of the {gdps.name} level you wish to reupload: ",
    cond = lambda x: x > 0,
    oftype = int,
    )
  
  level = gdps.req("downloadGJLevel19.php", params={"levelID": level_id})
  if not level:
    print(f"Could not find level {level_id}, maybe you mistyped the ID.")
    return ask_level()
  
  level = gjclasses.GJLevel(gjcrypt.decode_kv(level.split("#")[0]))
  if ask_yn(f"Retrieved level: {level.name}. Is this correct?", blank_line=False):
    return level
  else:
    return ask_level()


def ask_val(question, cond, *, oftype=int, allow_empty=False, blank_line=True):
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
    return ask_val(question, cond, oftype=oftype, allow_empty=allow_empty)
  if not cond(val):
    print("Invalid Response")
    return ask_val(question, cond, oftype=oftype, allow_empty=allow_empty)
  return val


def gj_login(server, *, player_id=None):
  """requests login information and attempts to log into the
  specified gd server
  """
  print()
  username = input(f"Your {server.name} username: ")
  password = askpass(f"Your {server.name} password: ")
  params = {
    "userName": username,
    # 1.9 requires plaintext password. 2.2 requires gjp2. instead of attempting
    # to figure out which to send we just send both because it's easier
    "password": password,
    "gjp2": gjcrypt.make_gjp2(password),
    "udid": gjcrypt.make_uuid(),
    "secret": "Wmfv3899gc9",
    }
  response = server.req("accounts/loginGJAccount.php", params, fail_on_neg=False)
  if not response:
    print("Failed to log in")
    return gj_login(server, player_id=player_id)
  elif response == "-1":
    print("Incorrect login")
    return gj_login(server, player_id=player_id)
  elif response == "-12":
    print("Rate limited, try using a VPN or try again later")
    return gj_login(server, player_id=player_id)
    
  login_info = {
    "username": username,
    "password": password,
    }
  login_info["account_id"], login_info["player_id"] = response.split(",")
  if player_id and (login_info["player_id"] not in {player_id, "6273"}):
    print("You must log into the account that uploaded the level")
    return gj_login(server, player_id=player_id)
  
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


CURRENT_RETRIEVE_ERROR = (
  f"Could not retrieve info for release {VERSION_TAG}. You may be using an unreleased version "
  "of the script"
  )
LATEST_RETRIEVE_ERROR = "Could not retrieve info for the latest release"

COULD_NOT_OPEN_ERROR = (
  f"Could not open the latest release page.\nThe latest release can be found at {RELEASE_LINK}"
  )

POLL_INTERVAL = 60*60*24*1  # 1 day
POLL_TIMESTAMP_PATH = "mysteriousnumber.dat"

current_time = int(time.time())


def set_poll_timestamp():
  """sets the timestamp in the last update poll file to the current
  time
  """
  timestamp = str(current_time)
  with open(POLL_TIMESTAMP_PATH, "w") as f:
    f.write(timestamp)
  

def update_recently_polled():
  """checks when updates were last polled for and returns True if the
  timestamp was less than POLL_INTERVAL ago
  """
  try:
    with open(POLL_TIMESTAMP_PATH, "r") as f:
      timestamp = int(f.read())
  except (FileNotFoundError, ValueError):
    set_poll_timestamp()
    return False
  
  return (timestamp+POLL_INTERVAL) > current_time

def get_repo_info(endpoint, keys):
  """retrieves specific information from the github repository
  metadata
  """
  try:
    response = github_request(endpoint, method="GET")
  except HTTPError:
    return
  try:
    data = {k: response[k] for k in keys}
  except (KeyError, TypeError):
    return
  return data


def check_for_update(silent=False):
  """checks if there is a new release of the script on github, and
  links you to the release if there is
  """
  set_poll_timestamp()
  # get latest release tag and timestamp
  data = get_repo_info("releases/latest", ["tag_name", "created_at"])
  if data is None:
    if not silent:
      print(LATEST_RETRIEVE_ERROR)
    return
  latest_tag = data["tag_name"]
  latest_timestamp = datetime.fromisoformat(data["created_at"])
  
  # get current release timestamp
  data = get_repo_info(f"releases/tags/{VERSION_TAG}", ["created_at"])
  if data is None:
    if not silent:
      print(CURRENT_RETRIEVE_ERROR)
    return
  current_timestamp = datetime.fromisoformat(data["created_at"])
  
  # compare
  if latest_tag == VERSION_TAG:
    if not silent:
      print("There are no new updates")
  
  elif latest_timestamp > current_timestamp:
    print()
    print(f"A new version, {latest_tag}, has been found on GitHub.")
    if latest_tag.lower().endswith("em"):
      print("It has been marked as an emergency update, I highly recommend you update.")
    if ask_yn("Go to the release page?"):
      try:
        webbrowser.open(RELEASE_LINK)
      except webbrowser.Error:
        print(COULD_NOT_OPEN_ERROR)
  else:
    print(f"You're using a draft/prerelease version newer than the latest release, {latest_tag}")
  

def main():
  """main function"""
  print(f"=== Fancy 1.9 Level Reuploader {VERSION_TAG} ===")
  print("Created by sSolsta")
  # check for latest version
  
  # if ask_yn("Would you like to check for updates?"):
    # check_for_update()
  
  if not update_recently_polled():
    check_for_update(silent=True)
  
  # retrieving level and login information
  level = ask_level()
  gj_login(gdps, player_id=level.uploader_player_id)
  login_info = gj_login(mainGD)
  # level processing options
  if ask_yn("Fix layers?", info=LAYER_FIX_INFO):
    print("Fixing layers...")
    level.unpack()
    for obj in level.objects:
      obj.fix_layer()
    print("Layers fixed")
  
  if ask_yn("Fix visual bugs?", info=VISUAL_BUGS_INFO):
    print("Fixing visual bugs...")
    level.unpack()
    for obj in level.objects:
      obj.fix_visual_bugs()
    print("Visual bugs fixed")
  
  if ask_yn("Merge glow dots?", info=GLOW_DOT_INFO):
    level.unpack()
    enable_multi = ask_yn(
      "Use multiprocessing? (Faster, only disable if it crashes)",
      blank_line=False,
      )
    level.objects = glowdotmerger.the_fuckening(level.objects, enable_multi=enable_multi)
  # change song
  if ask_yn("Change the song? (Only allows for newgrounds songs and not main level songs)"):
    song_id = ask_val(
      "Enter the song ID (leave blank to cancel): ",
      cond = lambda x: x > 0,
      oftype=int, allow_empty=True, blank_line=False,
      )
    if song_id:
      level.unpack()
      level.custom_song_id = song_id
      offset = ask_val(
        f"Enter the offset (leave blank to keep it as {level.song_offset}): ",
        cond = lambda x: x >= 0,
        oftype=float, allow_empty=True, blank_line=False,
        )
      if offset is not None:
        level.song_offset = offset
      level.song_fadein = ask_yn("Fade in?", blank_line=False)
      level.song_fadeout = ask_yn("Fade out?", blank_line=False)
    else:
      print("Cancelled")
  # retrieve upload parameters and upload level
  params = level.upload_info()
  params["accountID"] = login_info["account_id"]
  params["gjp2"] = gjcrypt.make_gjp2(login_info["password"])
  params["userName"] = login_info["username"]
  print()
  level_name = input(
    f"Enter the name of the reuploaded level (keep blank to keep it as '{level.name}'): "
    )
  params["unlisted"] = int(ask_yn("Upload as unlisted?", blank_line=False))
  if level_name:
    params["levelName"] = level_name
  upload_level(params)
  input("Press enter to exit")


if __name__ == "__main__":
  try:
    # required for windows pyinstaller
    multiprocessing.freeze_support()
    main()
  except Exception:
    print()
    print("An unexpected error occurred")
    print("Please show the error below to sSolsta so that she can fix the issue")
    print()
    traceback.print_exc()
    input()
