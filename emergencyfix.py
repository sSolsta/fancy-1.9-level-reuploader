"""fancy 1.9 reuploader emergency fix v2.16-em

fixes levels already on the 2.2 servers that broke due to layer fixing

created by ssolsta 2023
more info: https://github.com/sSolsta/fancy-1.9-level-reuploader/
"""

import traceback
from lib import gjservers, gjcrypt, gjclasses
from lib.askpass import askpass
from urllib.error import HTTPError

from fancy19reupload2 import VERSION_TAG, mainGD, ask_yn, ask_val, gj_login, upload_level


def ask_level(player_id=None):
  """attempts to retrieve the 1.9 level specified by the user"""
  level_id = ask_val(
    f"Enter the {mainGD.name} ID of the level you wish to fix: ",
    cond = lambda x: x > 0,
    oftype = int,
    )
  
  level = mainGD.req("downloadGJLevel22.php", params={"levelID": level_id})
  if not level:
    print(f"Could not find level {level_id}, maybe you mistyped the ID.")
    return ask_level(player_id=player_id)
  
  level = gjclasses.GJLevel(gjcrypt.decode_kv(level.split("#")[0]))
  
  if player_id is not None and level.uploader_player_id != player_id:
    print(f"Level: {level.name} ({level_id}) was not uploaded by you, maybe you mistyped the ID.")
    return ask_level(player_id=player_id)
  
  if ask_yn(f"Retrieved level: {level.name}. Is this correct?", blank_line=False):
    return level
  else:
    return ask_level(player_id=player_id)


def main():
  print(f"=== Fancy 1.9 Level Reuploader Emergency Fixer {VERSION_TAG} ===")
  print("Created by sSolsta")
  print()
  print(f"This script is for fixing levels on the {mainGD.name} servers broken due to layer fixing")
  print("If you wish to reupload a level not yet on the servers, run fancy19reupload2 instead.")
  
  login_info = gj_login(mainGD)
  
  while 1:
    level = ask_level(player_id=login_info["player_id"])
    print()
    print("Removing non-standard Z layers...")
    level.unpack()
    amount = 0
    for obj in level.objects:
      if obj.z_layer in {2, "2"}:
        obj.z_layer = 3
        amount += 1
      elif obj.z_layer in {4, "4"}:
        obj.z_layer = 5
        amount += 1
    if not amount:
      print(f"Could not find non-standard Z layers, {level.name} is not broken from layer fixing.")
    else:
      print(f"Fixed {amount} out of {len(level.objects)} objects.")
      
      params = level.upload_info()
      params["accountID"] = login_info["account_id"]
      params["gjp"] = gjcrypt.make_gjp(login_info["password"])
      params["userName"] = login_info["username"]
      params["levelVersion"] = int(level.get(5, 1))
      
      if ask_yn("Increment level version (recommended)?"):
        params["levelVersion"] += 1
      
      print(f"Uploading level...")
      upload_level(params)
    
    if not ask_yn("Would you like to fix another level?"):
      break
  
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