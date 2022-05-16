from urllib import request, parse
from urllib.error import HTTPError

# shamelessly stolen from zmx
def postRequest(url, data):
    data = parse.urlencode(data).encode()
    req = request.Request(url, data = data, headers = {"User-Agent": ""})
    return request.urlopen(req).read().decode()

DEFAULTS = {
    "gameVersion": 21,
    "binaryVersion": 35,
    "gdw": 0,
    "secret": "Wmfd2893gb7",
    }

class Server:
    def __init__(self, link = "http://www.boomlings.com/database/", name = ""):
        self.link = link
        self.name = name
    
    def req(self, endpoint, params = {}, failOnNeg = True):
        url = "".join((self.link, endpoint))
        params = {**DEFAULTS, **params}
        try:
            response = postRequest(url, params)
        except HTTPError:
            return
        if failOnNeg:
            try:
                if int(response) < 0:
                    return
            except ValueError:
                pass
        return response
    