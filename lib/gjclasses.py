import math as maths # i am stubborn
from lib import gjcrypt
from lib.strdict import StrDict
from lib.objinfo import objInfo

TENSQRTTWO = 10 * maths.sqrt(2)

class GJLevel(StrDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unpacked = False
    # decrypts level string and decomposes into level objects
    def unpack(self):
        if self.unpacked:
            return
        self.objects = [GJObject(gjcrypt.parseKV(x, separator = ",")) for x in gjcrypt.decodeLevel(self[4]).split(";") if x]
        self.startObj = self.objects.pop(0)
        
        self.unpacked = True
    # repacks all level objects back into level string
    def repack(self):
        self[4] = gjcrypt.encodeLevel("".join(str(x) for x in ([self.startObj] + self.objects)))
    # returns upload info, doesn't include account info
    def uploadInfo(self):
        if self.unpacked:
            self.repack()
        return {
            "levelID": 0,
            "levelName": self[2],
            "levelDesc": self[3],
            "levelVersion": 1,
            "levelLength": self[15],
            "audioTrack": self[12],
            "auto": 0,
            "password": self[27],
            "original": 0,
            "twoPlayer": self[31],
            "songID": self[35],
            "objects": self[45],
            "coins": 0,
            "requestedStars": 0,
            "unlisted": 0,
            "ldm": 0,
            "levelString": self[4],
            "seed2": gjcrypt.makeSeed2(self[4]),
            }

class GJObject(StrDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __str__(self):
        return gjcrypt.toKV(self, separator = ",") + ";"
    # layer fixing oh yeah
    def fixLayer(self):
        try:
            info = objInfo[self[1]]
        except KeyError:
            return
        
        col = int(self.get(19, 0))
        if info["hasColourChild"]:
            col = 0
        elif not col or info["hasChildObj"]:
            col = info["defaultCol"]
        bottom = (info["z"] < 0)
        if col not in {1, 2, 5}:
            bottom |= info["forceBottom"]
        
        self[24] = 2 if bottom else 4
        self[25] = info["z"]
    
    def fixVisualBugs(self):
        if self[1] in {"62", "66", "65", "68", "63", "64", "294", "295", "296", "297"}:
            self[41] = 1
            self[43] = "0a1a0.02a0a1"
        elif 560 <= int(self[1]) <= 577:
            self[41] = 1
            self[43] = "0a0a1a0a1"
        # disabling glow, no idea if this works
        if self[1] in {"36", "63", "64", "67", "84", "140", "141"}:
            self[96] = 1
    # for glow dot merging
    def initGlowCornerValues(self):
        offset = (int(self.get(4, 0)) * 3) ^ int(self.get(5, 0))
        self.angle = (int(self.get(6, 0)) - (offset * 90)) % 360
        
        temp = maths.radians(self.angle + 135)
        self.centre = (
            float(self[2]) + (maths.sin(temp) * TENSQRTTWO),
            float(self[3]) + (maths.cos(temp) * TENSQRTTWO),
            )
        self.mergeGroup = (self.get(19, "3"), self.angle % 90)
        self.subgroup = (self.angle - self.mergeGroup[1]) // 90
    