from collections import UserDict

class StrDict(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    # making it so that i can access str keys with ints for convenience
    def __getitem__(self, key):
        return super().__getitem__(str(key))
        
    def __setitem__(self, key, val):
        super().__setitem__(str(key), val)
        
    def get(self, key, default = None):
        return super().get(str(key), default)
        
    def setdefault(self, key, default = None):
        return super().setdefault(str(key), default)
        
    def pop(self, key, default = None):
        return super().pop(str(key), default)
    