# fancy 1.9 level reuploader

transfers your level from 1.9 to 2.1 but with extra stuff if you want it

created by ssolsta

## features:

- layer fixing (makes the level's layering on 2.1 like it would be on 1.9)
- glow dot merging (replaces glow dots made of corner pieces with the 2.1 glow dot object, to help reduce lag and object count)

## requirements

this script requires python to run (currently only tested on version 3.8.5, definitely won't work on versions below 3.7, if in doubt [download the latest version](https://www.python.org/) if you can)
this script also depends on the following modules:

- [requests](https://docs.python-requests.org/en/master/) (`pip install requests`)
- [gd.py](https://pypi.org/project/gd.py/) (`pip install gd.py`)

if you are unsure on how to install these modules, refer to [this tutorial](https://packaging.python.org/tutorials/installing-packages/)

## instructions

1. open `fancy19reupload.py` via the command line or via your system's file browser
2. follow the instructions given by the command prompt (you will require the login information of the 1.9 account that the level is on and the 2.1 account that you wish to upload the level to)
3. yeah that's it

## to do list
- figure out how to upload levels to 2.1 without gd.py
- try to make glow dot merging faster
