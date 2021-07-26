import requests
from uuid import uuid4

uuid = str(uuid4()).upper()

secret = "Wmfd2893gb7"
levelSecret = "Wmfv2898gc9"
loginSecret = "Wmfv3899gc9"


class gdServer:
    def __init__(self, link, defaults = {}):
        self.link = link
        self.defaults = defaults
        self.uuid = uuid
        
    def request(self, endpoint, params, post = True):
        link = "".join((self.link, endpoint))
        params = {**self.defaults, **params}
        reqFunc = requests.post if post else requests.get
        req = reqFunc(link, params)
        if not req.ok:
            return
        if req.text == "-1":
            return
        return req.text
    
    def parseKV(self, str, separator = ":"):
        split = str.split(separator)
        return {int(k): v for k,v in zip(split[0::2], split[1::2])}
        
