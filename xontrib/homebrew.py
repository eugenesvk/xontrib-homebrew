import subprocess
from os             	import path
from pathlib        	import Path
from xonsh          	import platform
from xonsh.built_ins	import XSH # XonshSession (${...} is 'XSH.env')

__all__ = ()

_log     	= XSH.env.get('XONTRIB_HOMEBREW_LOGLEVEL', 1) 	# 0 none, 1 error, 2 warning, 3 extra
_brewpath	= XSH.env.get('XONTRIB_HOMEBREW_PATHBREW', '')	# custom Homebrew install path

def _SetBrewEnv():
  if not platform.ON_DARWIN and not platform.ON_LINUX:
    if _log >= 3:
      print("xontrib-Homebrew: neither macOS nor Linux, exiting")
    return
  if 'HOMEBREW_PREFIX' in XSH.env: # don't overwrite existing env var
    if _log >= 3:
      print("xontrib-Homebrew: HOMEBREW_PREFIX already set, exiting")
    return
  HBS = None; full_cmd = None
  if platform.ON_DARWIN:
    if     (test_path := Path('/usr/local/bin/brew'   )).exists():
      full_cmd   = [test_path,'shellenv']
    elif   (test_path := Path('/opt/homebrew/bin/brew')).exists():
      full_cmd   = [test_path,'shellenv']
    elif   _brewpath and Path(f'{_brewpath}'      ).exists():
      if   (test_path := Path(f'{_brewpath}'     )).stem.casefold() == 'brew':
        full_cmd = [test_path,'shellenv']
      elif (test_path := Path(f'{_brewpath}/brew')).exists():
        full_cmd = [test_path,'shellenv']
    else:
      if _log >= 1:
        print("xontrib-Homebrew: ERROR: Can't find 'brew' in either of these locations:\n" + \
              "  /usr/local/bin/brew\n" + \
              "  /opt/homebrew/bin/brew")
        if _brewpath:
          print(f"  {_brewpath}\n" + \
                f"  {_brewpath}/brew")
      return
    if full_cmd:
      HBS = subprocess.run(full_cmd,capture_output=True,encoding="UTF-8").stdout
  if platform.ON_LINUX:
    if     (test_path := Path('/home/linuxbrew/.linuxbrew/bin/brew')).exists():
      full_cmd   = [test_path,'shellenv']
    elif   (test_path := Path("~",".linuxbrew/bin/brew").expanduser()).exists():
      full_cmd   = [test_path,'shellenv']
    elif   _brewpath and Path(f'{_brewpath}'      ).exists():
      if   (test_path := Path(f'{_brewpath}'     )).stem.casefold() == 'brew':
        full_cmd = [test_path,'shellenv']
      elif (test_path := Path(f'{_brewpath}/brew')).exists():
        full_cmd = [test_path,'shellenv']
    else:
      if _log >= 1:
        print("xontrib-Homebrew: ERROR: Can't find 'brew' in either of these locations:\n" + \
              "  /home/linuxbrew/.linuxbrew/bin/brew\n" + \
              "  ~/.linuxbrew/bin/brew")
        if _brewpath:
          print(f"  {_brewpath}\n" + \
                f"  {_brewpath}/brew")
      return
    if full_cmd:
      HBS = subprocess.run(full_cmd,capture_output=True,encoding="UTF-8").stdout
  if not HBS:
    if _log >= 1:
      print("xontrib-Homebrew: ERROR: got an empty 'brew shellenv' result")
    return
  """ we get the default bash shellenv output like this (macOS):
    export HOMEBREW_PREFIX="/usr/local";
    export HOMEBREW_CELLAR="/usr/local/Cellar";
    export HOMEBREW_REPOSITORY="/usr/local/Homebrew";
    export PATH="/usr/local/bin:/usr/local/sbin${PATH+:$PATH}";
    export MANPATH="/usr/local/share/man${MANPATH+:$MANPATH}:";
    export INFOPATH="/usr/local/share/info:${INFOPATH:-}";
  """
  """ ... or                                       this (Linux):
    export HOMEBREW_PREFIX="/home/linuxbrew/.linuxbrew";
    export HOMEBREW_CELLAR="/home/linuxbrew/.linuxbrew/Cellar";
    export HOMEBREW_REPOSITORY="/home/linuxbrew/.linuxbrew/Homebrew";
    export PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin${PATH+:$PATH}";
    export MANPATH="/home/linuxbrew/.linuxbrew/share/man${MANPATH+:$MANPATH}:";
    export INFOPATH="/home/linuxbrew/.linuxbrew/share/info:${INFOPATH:-}";
  """
  # 1. Remove bashisms
  HBS = HBS.replace(r'export '              	, '')\
           .replace(r'${PATH+:$PATH}'       	, '')\
           .replace(r'${MANPATH+:$MANPATH}:'	, '')\
           .replace(r':${INFOPATH:-}'       	, '')\
           .split(';\n')
  if HBS[-1] == '': # remove the last (empty) line
    del HBS[-1]
  if len(HBS) != 6:
    if _log >= 2:
      print("xontrib-Homebrew: WARNING: expected 6 variables from shellenv output, but instead got " + str(len(HBS)))

  # 2. Create empty env vars if they don't already exist
  startPath	= ['PATH', 'MANPATH', 'INFOPATH']
  for  env_path in startPath:
    if env_path not in XSH.env:
      XSH.env[env_path] = ''

  # 3. Test whether each line wants to assign a Location var or add a value to some PATH
  startLoc 	= 'HOMEBREW_' # '_PREFIX', '_CELLAR', '_REPOSITORY'
  startPath	= ['PATH', 'MANPATH', 'INFOPATH']
  matches  	= []

  for i, cmd in enumerate(HBS):
    if cmd.startswith(startLoc):	# Location vars can be executed as is
      execx('$'+HBS[i])         	# assigns env var '$HOMEBREW_X="VALUE"'
      matches.append(i)
    elif cmd.startswith(tuple(startPath)):	# PATH vars need to be appended to PATH lists
      if cmd.find('=') == -1:             	# something is wrong, '=' not found after 'PATH'
        break
      else:
        matches.append(i)
        cmdSplit = cmd.split('=',1)                    	# split 'PATH="path1:path2"'
        cmdVar = cmdSplit[0]                           	# 'PATH'
        cmdVal = cmdSplit[1].replace('"','').split(':')	# split "path1:path2"
        for pathi in reversed(cmdVal):
          ${cmdVar}.add(pathi, front=True, replace=True) # env lookup 'PATH' and add each path
  if len(matches) != 6:
    if _log >= 2:
      print("xontrib-Homebrew: WARNING: expected to successfully parse 6 variables from shellenv output, but only managed to parse " + str(len(matches)))
    if _log >= 3:
      for i in sorted(matches, reverse=True):
        del HBS[i]
      print("Remaining items:")
      print(HBS)
    return

_SetBrewEnv()
