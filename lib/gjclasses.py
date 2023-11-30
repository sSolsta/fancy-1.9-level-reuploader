"""lib.gjclasses

contains GJLevel and GJObject
"""

import math as maths  # i am stubborn
from lib import gjcrypt
from lib.strdict import StrDict
from lib.objinfo import obj_info

TENSQRTTWO = 10 * maths.sqrt(2)

TWO_POINT_TWO_FIX = True  # if 2.2 truly breaks it

class GJLevel(StrDict):
  """GJLevel(StrDict)
  
  contains geometry dash level info
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.unpacked = False
  
  def unpack(self):
    """decrypts level string and decomposes it into level
    objects
    """
    if self.unpacked:
      return
    obj_strings = gjcrypt.decode_level(self.data_string).split(";")
    self.objects = [GJObject(gjcrypt.decode_kv(x, separator=",")) for x in obj_strings if x]
    self.start_obj = self.objects.pop(0)
    
    self.unpacked = True
  
  def repack(self):
    """repacks all level objects back into level string"""
    self.objects.insert(0, self.start_obj)
    self.data_string = gjcrypt.encode_level("".join(str(x) for x in self.objects))
    
    self.unpacked = False
  
  def upload_info(self):
    """returns upload info, doesn't include account info"""
    if self.unpacked:
      self.repack()
    return {
      "levelID": 0,
      "levelName": self.name,
      "levelDesc": self.description,
      "levelVersion": 1,
      "levelLength": self.length,
      "audioTrack": self.default_song_id,
      "auto": 0,
      "password": self.password,
      "original": 0,
      "twoPlayer": self.is_two_player,
      "songID": self.custom_song_id,
      "objects": self.object_count,
      "coins": 0,
      "requestedStars": 0,
      "unlisted": 0,
      "ldm": 0,
      "levelString": self.data_string,
      "seed2": gjcrypt.make_level_seed(self.data_string),
      }
  
  # boilerplate pt 1
  @property
  def id(self):
    return self[1]
  @id.setter
  def id(self, v):
    self[1] = v
  
  @property
  def name(self):
    return self[2]
  @name.setter
  def name(self, v):
    self[2] = v
  
  @property
  def description(self):
    return self[3]
  @description.setter
  def description(self, v):
    self[3] = v
  
  @property
  def data_string(self):
    return self[4]
  @data_string.setter
  def data_string(self, v):
    self[4] = v
  
  @property
  def uploader_player_id(self):
    return self[6]
  @uploader_player_id.setter
  def uploader_player_id(self, v):
    self[6] = v
  
  @property
  def default_song_id(self):
    return self[12]
  @default_song_id.setter
  def default_song_id(self, v):
    self[12] = v
  
  @property
  def length(self):
    return self[15]
  @length.setter
  def length(self, v):
    self[15] = v
  
  @property
  def password(self):
    return self[27]
  @password.setter
  def password(self, v):
    self[27] = v
  
  @property
  def is_two_player(self):
    return self[31]
  @is_two_player.setter
  def is_two_player(self, v):
    self[31] = int(v)
  
  @property
  def custom_song_id(self):
    return self[35]
  @custom_song_id.setter
  def custom_song_id(self, v):
    self[35] = v
  
  @property
  def object_count(self):
    return self[45]
  @object_count.setter
  def object_count(self, v):
    self[45] = v
  
  @property
  def song_offset(self):
    if not self.unpacked:
      self.unpack()
    return self.start_obj["kA13"]
  @song_offset.setter
  def song_offset(self, v):
    if not self.unpacked:
      self.unpack()
    self.start_obj["kA13"] = v
  
  @property
  def song_fadein(self):
    if not self.unpacked:
      self.unpack()
    return self.start_obj["kA15"]
  @song_fadein.setter
  def song_fadein(self, v):
    if not self.unpacked:
      self.unpack()
    self.start_obj["kA15"] = int(v)
  
  @property
  def song_fadeout(self):
    if not self.unpacked:
      self.unpack()
    return self.start_obj["kA16"]
  @song_fadeout.setter
  def song_fadeout(self, v):
    if not self.unpacked:
      self.unpack()
    self.start_obj["kA16"] = int(v)


class GJObject(StrDict):
  """GJObject(StrDict)
  
  contains geometry dash object info, and functions used to
  manipulate said objects
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
  
  def __str__(self):
    return gjcrypt.encode_kv(self, separator=",") + ";"

  def fix_layer(self):
    """uses 2.1 z layer and z order properties to emulate 1.9
    layering
    """
    try:
      info = obj_info[self.id]
    except KeyError:
      return
    
    col = self.colour
    if info["hasColourChild"]:
      col = 0
    elif info["hasChildObj"]:
      col = self.default_colour
    bottom = (info["z"] < 0)
    if col not in {1, 2, 5}:
      bottom |= info["forceBottom"]
    
    self.z_layer = 2 if bottom else 4
    if TWO_POINT_TWO_FIX:
      self.z_layer += 1
    self.z_order = info["z"]
  
  def fix_visual_bugs(self):
    """fixes/reintroduces various visual bugs that exist in either
    1.9 or 2.1 but not both
    """
    if self.id in {"62", "66", "65", "68", "63", "64", "294", "295", "296", "297"}:
      self.main_hsv_enabled = True
      self.main_hsv_string = "0a1a0.02a0a1"
    elif 560 <= int(self.id) <= 577:
      self.main_hsv_enabled = True
      self.main_hsv_string = "0a0a1a0a1"
    
    if self.id in {"36", "63", "64", "67", "84", "140", "141"}:
      self.disable_glow = True
  
  def init_glow_corner_values(self):
    """initialises corner values for glow dot merging"""
    offset = self.flip_x*3 ^ self.flip_y
    self.angle = (int(self.rotation) - offset*90) % 360
    
    temp = maths.radians(self.angle + 135)
    self.centre = (
      self.x + maths.sin(temp)*TENSQRTTWO,
      self.y + maths.cos(temp)*TENSQRTTWO,
      )
    self.merge_group = (self.colour, self.angle % 90)
    self.subgroup = (self.angle - self.merge_group[1]) // 90
  
  # boilerplate pt 2
  @property
  def id(self):
    return self[1]
  @id.setter
  def id(self, v):
    self[1] = v
  
  @property
  def x(self):
    return float(self[2])
  @x.setter
  def x(self, v):
    self[2] = v
  
  @property
  def y(self):
    return float(self[3])
  @y.setter
  def y(self, v):
    self[3] = v
  
  @property
  def flip_x(self):
    return bool(int(self.get(4, 0)))
  @flip_x.setter
  def flip_x(self, v):
    self[4] = int(v)
  
  @property
  def flip_y(self):
    return bool(int(self.get(5, 0)))
  @flip_y.setter
  def flip_y(self, v):
    self[5] = int(v)
  
  @property
  def rotation(self):
    return float(self.get(6, 0))
  @rotation.setter
  def rotation(self, v):
    self[6] = v
  
  @property
  def default_colour(self):
    try:
      return self._default_colour
    except AttributeError:
      try:
        info = obj_info[self.id]
      except KeyError:
        default = 0
      else:
        default = info["defaultCol"]
      self._default_colour = default
      return default
  
  @property
  def colour(self):
    return int(self.get(19, self.default_colour))
  @colour.setter
  def colour(self, v):
    self[19] = v
  
  @property
  def z_layer(self):
    return int(self.get(24, 0))
  @z_layer.setter
  def z_layer(self, v):
    self[24] = v
  
  @property
  def z_order(self):
    return int(self.get(25, 0))
  @z_order.setter
  def z_order(self, v):
    self[25] = v
  
  @property
  def main_hsv_enabled(self):
    return bool(int(self.get(41, 0)))
  @main_hsv_enabled.setter
  def main_hsv_enabled(self, v):
    self[41] = int(v)
  
  @property
  def main_hsv_string(self):
    return self.get(43, 0)
  @main_hsv_string.setter
  def main_hsv_string(self, v):
    self[43] = v
  
  @property
  def disable_glow(self):
    return bool(int(self.get(96, 0)))
  @disable_glow.setter
  def disable_glow(self, v):
    self[96] = int(v)
