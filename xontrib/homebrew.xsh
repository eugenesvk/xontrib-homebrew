from xonsh import platform
from os import path

__all__ = ()

_log = __xonsh__.env.get('XONTRIB_LINUXBREW_LOGLEVEL', 1) # 0 none, 1 error, 2 warning, 3 extra

def _SetBrewEnv():
  if not platform.ON_LINUX:
    if _log >= 3:
      print("xontrib-LinuxBrew: not Linux, exiting")
    return
  if 'HOMEBREW_PREFIX' in ${...}: # don't overwrite existing env var
    if _log >= 3:
      print("xontrib-LinuxBrew: HOMEBREW_PREFIX already set, exiting")
    return
  LBS = ''
  if p'/home/linuxbrew/.linuxbrew/bin/brew'.exists():
    LBS = $(/home/linuxbrew/.linuxbrew/bin/brew shellenv)
  elif pf'{path.join(path.expanduser("~"), ".linuxbrew/bin/brew")}'.exists():
    LBS = $(pf'{path.join(path.expanduser("~"), ".linuxbrew/bin/brew")}' shellenv)
  else:
    if _log >= 1:
      print("xontrib-LinuxBrew: ERROR: Can't find 'brew' in neither '/home/linuxbrew/.linuxbrew/bin/' nor in '~/.linuxbrew/bin/'")
    return
  """ we get the default bash shellenv output like this
    export HOMEBREW_PREFIX="/home/linuxbrew/.linuxbrew";
    export HOMEBREW_CELLAR="/home/linuxbrew/.linuxbrew/Cellar";
    export HOMEBREW_REPOSITORY="/home/linuxbrew/.linuxbrew/Homebrew";
    export PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin${PATH+:$PATH}";
    export MANPATH="/home/linuxbrew/.linuxbrew/share/man${MANPATH+:$MANPATH}:";
    export INFOPATH="/home/linuxbrew/.linuxbrew/share/info:${INFOPATH:-}";
  """
  # 1. Remove bashisms
  LBS = LBS.replace(r'export '                , '')\
           .replace(r'${PATH+:$PATH}'         , '')\
           .replace(r'${MANPATH+:$MANPATH}:'  , '')\
           .replace(r':${INFOPATH:-}'         , '')\
           .split(';\n')
  if LBS[-1] == '': # remove the last (empty) line
    del LBS[-1]
  if len(LBS) != 6:
    if _log >= 2:
      print("xontrib-LinuxBrew: WARNING: expected 6 variables from shellenv output, but instead got " + str(len(LBS)))

  # 2. Create empty env vars if they don't already exist
  if 'PATH'     not in ${...}:
    $PATH       = ''
  if 'MANPATH'  not in ${...}:
    $MANPATH    = ''
  if 'INFOPATH' not in ${...}:
    $INFOPATH   = ''

  # 3. Test whether each line wants to assign a Location var or add a value to some PATH
  startLoc  = 'HOMEBREW_' # '_PREFIX', '_CELLAR', '_REPOSITORY'
  startPath = ['PATH', 'MANPATH', 'INFOPATH']
  matches   = []

  for i, cmd in enumerate(LBS):
    if cmd.startswith(startLoc):  # Location vars can be executed as is
      execx('$'+LBS[i])           # assigns env var '$HOMEBREW_X="VALUE"'
      matches.append(i)
    elif cmd.startswith(tuple(startPath)):  # PATH vars need to be appended to PATH lists
      if cmd.find('=') == -1:               # something is wrong, '=' not found after 'PATH'
        break
      else:
        matches.append(i)
        cmdSplit = cmd.split('=',1)                     # split 'PATH="path1:path2"'
        cmdVar = cmdSplit[0]                            # 'PATH'
        cmdVal = cmdSplit[1].replace('"','').split(':') # split "path1:path2"
        for pathi in reversed(cmdVal):
          ${cmdVar}.add(pathi, front=True, replace=True) # env lookup 'PATH' and add each path
  if len(matches) != 6:
    if _log >= 2:
      print("xontrib-LinuxBrew: WARNING: expected to successfully parse 6 variables from shellenv output, but only managed to parse " + str(len(matches)))
    if _log >= 3:
      for i in sorted(matches, reverse=True):
        del LBS[i]
      print("Remaining items:")
      print(LBS)
    return

_SetBrewEnv()
