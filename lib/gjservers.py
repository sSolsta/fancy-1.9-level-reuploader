"""lib.gjservers

contains Server, used to interact with gd servers
"""

import socket
from urllib import request, parse
from urllib.error import URLError

# shamelessly stolen from zmx
def post_request(url, data):
    data = parse.urlencode(data).encode()
    req = request.Request(url, data = data, headers = {"User-Agent": ""})
    return request.urlopen(req, timeout = 30).read().decode()

DEFAULTS = {
    "gameVersion": 21,
    "binaryVersion": 35,
    "gdw": 0,
    "secret": "Wmfd2893gb7",
    }


class Server:
    def __init__(self, link = "http://www.boomlings.com/database/", *, name = ""):
        self.link = link
        self.name = name
    
    def req(self, endpoint, params = {}, fail_on_neg = True):
        url = "".join((self.link, endpoint))
        params = {**DEFAULTS, **params}
        try:
            response = post_request(url, params)
        except (URLError, socket.timeout):
            return
        if fail_on_neg:
            try:
                if int(response) < 0:
                    return
            except ValueError:
                pass
        return response
