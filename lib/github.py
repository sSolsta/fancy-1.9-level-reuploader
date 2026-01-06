"""lib.github

contains github_request, used just to check the latest version of the script
"""

import socket
import json
from urllib import request, parse
from urllib.error import URLError
from lib.gjservers import http_request

# you know i'm kinda surprised it accepts http requests but i'm glad it does
API_LINK = "http://api.github.com/repos/solstacoded/fancy-1.9-level-reuploader/"
RELEASE_LINK = "https://github.com/solstacoded/fancy-1.9-level-reuploader/releases/latest"

def github_request(endpoint, method=None, params={}, decode_json=True):
  url = "".join((API_LINK, endpoint))
  try:
    response = http_request(url, params, method="POST", include_user_agent=False)
  except (URLError, socket.timeout):
    return
  if decode_json:
    try:
      return json.loads(response)
    except ValueError:
      return
  else:
    return response