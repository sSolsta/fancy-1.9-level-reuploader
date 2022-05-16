import math as maths # i am stubborn
from lib import gjcrypt
from lib.strdict import StrDict
from lib.objecttypes import objectTypes

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
        objType = objectTypes.get(int(self[1]), 1)
        
        if objType == 1:
            pass
        elif objType in (2, 3):
            # the specific default colour here does not matter, we only care if it's one of the three or not
            default = "1" if objType == 3 else "h"
            layer = 3 if (self.get(19, default) in "125") else 1
            self[24] = layer
        elif objType == 4:
            self[24] = 1
        elif objType == 5:
            self[24] = 4
    
    def fixColour(self):
        if self[1] in ("62", "66", "65", "68", "63", "64", "294", "295", "296", "297"):
            self[41] = 1
            self[43] = "0a1a0.02a0a1"
        elif 560 <= int(self[1]) <= 577:
            self[41] = 1
            self[43] = "0a0a1a0a1"
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
    