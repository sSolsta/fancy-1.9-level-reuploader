import base64
import itertools
import zlib

def decodeLevelString(levelString):
    return zlib.decompress(base64.urlsafe_b64decode(levelString), 15 | 32).decode()
    
def xorCipher(string, key):
    return ("").join(chr(ord(x) ^ ord(y)) for x, y in zip(string, itertools.cycle(key)))