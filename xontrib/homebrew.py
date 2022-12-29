from os      	import path
from xonsh   	import platform
from builtins	import __xonsh__	# XonshSession (${...} is '__xonsh__.env')

__all__ = ()

_log     	= __xonsh__.env.get('XONTRIB_HOMEBREW_LOGLEVEL', 1) 	# 0 none, 1 error, 2 warning, 3 extra
_brewpath	= __xonsh__.env.get('XONTRIB_HOMEBREW_PATHBREW', '')	# custom Homebrew install path

def _SetBrewEnv():
  if not platform.ON_DARWIN and not platform.ON_LINUX:
    if _log >= 3:
      print("xontrib-Homebrew: neither macOS nor Linux, exiting")
    return
  if 'HOMEBREW_PREFIX' in __xonsh__.env: # don't overwrite existing env var
    if _log >= 3:
      print("xontrib-Homebrew: HOMEBREW_PREFIX already set, exiting")
    return
  HBS = ''
  if platform.ON_DARWIN:
    if      p'/usr/local/bin/brew'.exists():
      HBS = $(/usr/local/bin/brew shellenv)
    elif    p'/opt/homebrew/bin/brew'.exists():
      HBS = $(/opt/homebrew/bin/brew shellenv)
    elif _brewpath and pf'{_brewpath}'.exists():
      if path.basename(path.normpath(pf'{_brewpath}')).casefold() == 'brew':
        HBS = $(pf'{_brewpath}' shellenv)
      elif pf'{_brewpath}/brew'.exists():
        HBS = $(pf'{_brewpath}/brew' shellenv)
    else:
      if _log >= 1:
        print("xontrib-Homebrew: ERROR: Can't find 'brew' in either of these locations:\n" + \
              "  /usr/local/bin/brew\n" + \
              "  /opt/homebrew/bin/brew")
        if _brewpath:
          print(f"  {_brewpath}\n" + \
                f"  {_brewpath}/brew")
      return
  if platform.ON_LINUX:
    if      p'/home/linuxbrew/.linuxbrew/bin/brew'.exists():
      HBS = $(/home/linuxbrew/.linuxbrew/bin/brew shellenv)
    elif      pf'{path.join(path.expanduser("~"), ".linuxbrew/bin/brew")}'.exists():
      HBS = $(pf'{path.join(path.expanduser("~"), ".linuxbrew/bin/brew")}' shellenv)
    elif _brewpath and pf'{_brewpath}'.exists():
      if path.basename(path.normpath(pf'{_brewpath}')).casefold() == 'brew':
        HBS = $(pf'{_brewpath}' shellenv)
      elif pf'{_brewpath}/brew'.exists():
        HBS = $(pf'{_brewpath}/brew' shellenv)
    else:
      if _log >= 1:
        print("xontrib-Homebrew: ERROR: Can't find 'brew' in either of these locations:\n" + \
              "  /home/linuxbrew/.linuxbrew/bin/brew\n" + \
              "  ~/.linuxbrew/bin/brew")
        if _brewpath:
          print(f"  {_brewpath}\n" + \
                f"  {_brewpath}/brew")
      return
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
  """ ... or this (Linux):
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
  if 'PATH'    	not in __xonsh__.env:
    $PATH      	= ''
  if 'MANPATH' 	not in __xonsh__.env:
    $MANPATH   	= ''
  if 'INFOPATH'	not in __xonsh__.env:
    $INFOPATH  	= ''

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
