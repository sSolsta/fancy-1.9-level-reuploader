try:
  from pwinput import pwinput
except ImportError:
  from getpass import getpass
  askpass = getpass
else:
  def askpass(prompt=""):
    return pwinput(prompt=prompt, mask="*")