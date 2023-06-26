# fancy 1.9 level reuploader (v2)

transfers your level from 1.9 to 2.1 but with extra stuff if you want it

created by ssolsta

## features:

- layer fixing (makes the level's layering on 2.1 like it would be on 1.9)
- visual bug fixing (fixes a 2.1 colour bug, replicates a different 1.9 colour bug, and removes glow from a select few objects)
- glow dot merging (replaces glow dots made of corner pieces with the 2.1 glow dot object, to help reduce lag and object count)
- change the song (for if the song used is not on newgrounds, though this isn't a requirement to use this feature)
- change the name
- upload as unlisted

## requirements

### python distribution (multi-platform)
- [python](https://www.python.org/) (only tested with 3.8.10 and 3.11.1, will probably not work on earlier versions, if in doubt install the latest version)

### win64 distribution (windows)
- a 64-bit version of windows (only tested with windows 10, no guarantee it will work on any earlier versions)

## downloads
downloads for both distributions can be found [on the github releases page](https://github.com/sSolsta/fancy-1.9-level-reuploader/releases/latest)

## instructions

1. open `fancy19reupload2.py` via the command line or via your system's file browser
	- `fancy19reupload2.exe` if you are using the win64 distribution
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
- 22 august 2022 (v2.1):
	- reworked the layer fixing function to be more true to how layering actually works in 1.9
	- renamed "colour bug fixing" to "visual bug fixing" and added glow removal to it
- 24 august 2022:
	- created win64 executable with pyinstaller
- 25 august 2022 (v2.11):
	- fixed issue with 3d layering (i was making a comparison where i shouldn't have)
- 13 september 2022 (v2.113):
	- cleaned up the code and attempted to make it almost pep-8 compliant (no spaces around equals signs is ugly) (and also pep-8 specifically states the line length limit can be extended to 99 characters)
	- rewrote the glow dot merger slightly to utilise multiprocessing (much faster, only really matters for levels like right out and freedom19 with a fuckton of glow dots)
- 25 june 2023 (v2.12):
	- fixed issue with 3d layering (i wasn't making a comparison where i should have) (yes i'm pretty sure this is just reverting the change made in v2.11)
  - had a change of heart about spaces around equals signs
- 26 june 2023 (v2.14):
	- added code to automatically check for new updates on github
## future plans

- add hitbox fixing
	- will involve going through and reverse-engineering 2.1 just enough to be able to retrieve 2.1 hitboxes
	- will not attempt to adjust for physics differences
	- may have trouble with fixing objects with larger hitboxes in 2.1 if they exist