<p align="center">
Add <a href="https://brew.sh"><b>Homebrew</b></a>'s shell environment to <a href="https://xon.sh"><b>xonsh</b></a> shell on <b>macOS</b>/<b>Linux</b>
<br/>
(alternative to <a href="https://docs.brew.sh/Homebrew-on-Linux">shellenv</a>).
</p>

<p align="center">  
If you like the idea click ⭐ on the repo and <a href="https://twitter.com/intent/tweet?text=Nice%20xontrib%20for%20the%20xonsh%20shell!&url=https://github.com/eugenesvk/xontrib-homebrew" target="_blank">tweet</a>. This might also accelerate adding <a href="https://github.com/Homebrew/brew/pull/10757#issuecomment-791381047">xonsh support to Homebrew</a>.
</p>


## Introduction

__Homebrew__ has a `shellenv` command to add __its environment__ to your shell: it adds a few
environment variables (`HOMEBREW_` `PREFIX`/`CELLAR`/`REPOSITORY`) and updates a few paths (`MAN`/`INFO`/ `PATH`).

This xontrib automatically translates the default __bash__ export statements of `shellenv` into __xonsh__.

## Installation

To install use pip:

```bash
xpip install xontrib-homebrew
# or: xpip install -U git+https://github.com/eugenesvk/xontrib-homebrew
```

This xontrib will get loaded automatically for interactive sessions; to stop this, set

```xonsh
$XONTRIBS_AUTOLOAD_DISABLED = {"homebrew", }
```

## Usage

Add this to your xonsh run control file (`~/.xonshrc` or `~/.config/rc.xsh`):
```bash
xontrib load homebrew
```

Set custom Homebrew installation path via `$XONTRIB_HOMEBREW_PATHBREW` to `/full/path/to/bin/brew` if it's not installed at these default paths (which always take precedence):

| macOS                   	| Linux                                	|
|:------------------------	|:-------------------------------------	|
| `/usr/local/bin/brew`   	| `/home/linuxbrew/.linuxbrew/bin/brew`	|
| `/opt/homebrew/bin/brew`	| `~/.linuxbrew/bin/brew`              	|

Set the level of verbosity via `$XONTRIB_HOMEBREW_LOGLEVEL` to __0–3__ (default __1__):

  - 0 print nothing (fail silently)
  - __1__ print errors (e.g. can't find `brew` at default locations)
  - 2 print warnings (e.g issues when parsing `shellenv`)
  - 3 print more verbose messages

## Known issues

- Xontrib autoload currently can't be disabled due to a [xonsh bug](https://github.com/xonsh/xonsh/issues/5020), so if you need precise control over when your environment variables are set (e.g., whether `/path/to/homebrew/bin` is at the top of `PATH`), try installing from a `deauto` branch:</br>
  `xpip install -U git+https://github.com/eugenesvk/xontrib-homebrew@deauto`
- Likely due to the same bug your `$XONTRIB_HOMEBREW_PATHBREW` and `$XONTRIB_HOMEBREW_LOGLEVEL` env vars might be ignored in the autoloaded version, so install the `@deauto` version mentioned above

## Credits

This package was created with [xontrib cookiecutter template](https://github.com/xonsh/xontrib-cookiecutter).
