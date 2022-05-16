import base64
import hashlib
import itertools
import zlib
import gzip
import random
import string as stringo
from lib.strdict import StrDict

alphanumeric = stringo.ascii_letters + stringo.digits

# a lot of this is just stolen from gddocs

def xor(string, key):
    return "".join([chr(ord(s) ^ ord(k)) for s, k in zip(string, itertools.cycle(str(key)))])

def decodeLevel(string):
    return zlib.decompress(base64.urlsafe_b64decode(string), 15 | 32).decode()

def encodeLevel(string):
    return base64.urlsafe_b64encode(gzip.compress(string.encode())).decode()

def makeGJP(password):
    return base64.urlsafe_b64encode(xor(password, "37526").encode()).decode()

def makeSeed2(string):
    hash = hashlib.sha1(string.encode()[::len(string)//50][:50] + b"xI25fpAapCQg").hexdigest()
    return base64.urlsafe_b64encode(xor(hash, "41274").encode()).decode()

def parseKV(str, separator = ":"):
    split = str.split(separator)
    return StrDict({k: v for k,v in zip(split[0::2], split[1::2])})

def toKV(dict, separator = ":"):
    return separator.join(separator.join(str(y) for y in x) for x in dict.items())

def randomString(length):
    return "".join(random.choices(alphanumeric, k = length))

def makeUUID(lengths = [8, 4, 4, 4, 10]):
    return "-".join(map(randomString, lengths))