# fancy 1.9 level reuploader (v2)

transfers your level from 1.9 to 2.1 but with extra stuff if you want it

created by solsta (me)

## features:

- layer fixing (makes the level's layering on 2.1 like it would be on 1.9)
- colour bug fixing (fixes a 2.1 colour bug and replicates a different 1.9 colour bug)
- glow dot merging (replaces glow dots made of corner pieces with the 2.1 glow dot object, to help reduce lag and object count)
- change the song (for if the song used is not on newgrounds, though this isn't a requirement to use this feature)
- change the name
- upload as unlisted

## requirements

- [python](https://www.python.org/) (only tested with 3.8.10, will probably not work on earlier versions, if in doubt install the latest version)

## instructions

1. open `fancy19reupload.py` via the command line or via your system's file browser
2. follow the instructions given by the command prompt (you will require the login information of the 1.9 account that the level is on and the 2.1 account that you wish to upload the level to)
3. yeah that's it

## changelog
- 3rd october 2021: fixed a bug preventing you from logging in after a failed login attempt
- 16th may 2022 (v2): completely rewrote the script from scratch, important changes include:
	- removed the dependency on the requests and gd.py modules
	- made glow dot merging faster
	- added colour bug fixing
	- improved song changing (no longer requires a reupload song, allows you to change offset and fade in/outs)
	- added option to upload the level as unlisted
	- changed pronoun in unexpected error message from 'he' to 'she'
