"""lib.gjcrypt

contains functions used for encoding/decoding geometry dash data, among
other things
"""

import base64
import hashlib
import itertools
import zlib
import gzip
import random
import string as string
from lib.strdict import StrDict

alphanumeric = string.ascii_letters + string.digits

# a lot of this is just stolen from gddocs

def xor(string, key):
    return "".join(chr(ord(s) ^ ord(k)) for s, k in zip(string, itertools.cycle(str(key))))

def decode_level(string):
    return zlib.decompress(base64.urlsafe_b64decode(string), 15 | 32).decode()

def encode_level(string):
    return base64.urlsafe_b64encode(gzip.compress(string.encode())).decode()

def make_gjp(password):
    return base64.urlsafe_b64encode(xor(password, "37526").encode()).decode()

def make_level_seed(string):
    hash = hashlib.sha1(string.encode()[::len(string)//50][:50] + b"xI25fpAapCQg").hexdigest()
    return base64.urlsafe_b64encode(xor(hash, "41274").encode()).decode()

def decode_kv(str, separator = ":"):
    split = str.split(separator)
    return StrDict({k: v for k, v in zip(split[0::2], split[1::2])})

def encode_kv(dict, separator = ":"):
    return separator.join(separator.join((k, str(v))) for k, v in dict.items())
    
def random_string(length):
    return "".join(random.choices(alphanumeric, k = length))

def make_uuid(lengths = (8, 4, 4, 4, 10)):
    return "-".join(map(random_string, lengths))
