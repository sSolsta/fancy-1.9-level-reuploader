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
import string
from lib.strdict import StrDict

ALPHANUMERIC = string.ascii_letters + string.digits

# a lot of this is just stolen from gddocs

def xor(string, key):
  key_cycle = itertools.cycle(str(key))
  return "".join(chr(ord(s) ^ ord(k)) for s, k in zip(string, key_cycle))


def decode_level(string):
  decoded = base64.urlsafe_b64decode(string)
  return zlib.decompress(decoded, 15 | 32).decode()


def encode_level(string):
  string = string.encode()
  compressed = gzip.compress(string)
  return base64.urlsafe_b64encode(compressed).decode()


def make_gjp(password):
  xored = xor(password, "37526").encode()
  return base64.urlsafe_b64encode(xored).decode()


def make_level_seed(string):
  string = string.encode()
  sliced = string[::len(string)//50][:50] + b"xI25fpAapCQg"
  hashed = hashlib.sha1(sliced).hexdigest()
  xored = xor(hashed, "41274").encode()
  return base64.urlsafe_b64encode(xored).decode()


def decode_kv(string, separator=":"):
  split = string.split(separator)
  return StrDict({k: v for k, v in zip(split[0::2], split[1::2])})


def encode_kv(dict, separator=":"):
  return separator.join(separator.join((k, str(v))) for k, v in dict.items())
  
  
def random_string(length):
  return "".join(random.choices(ALPHANUMERIC, k=length))


def make_uuid(lengths = (8, 4, 4, 4, 10)):
  return "-".join(map(random_string, lengths))
