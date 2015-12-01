"""
pytest_watch.command
~~~~~~~~~~~~~~~~~~~~

Implements the command-line interface for pytest-watch.

All positional arguments after `--` are passed directly to py.test executable.


Usage: ptw [options] [<directories>...] [-- <args>...]

Options:
  -h --help         Show this help.
  --version         Show version.
  --ignore=<dirs>   Comma-separated list of directories to ignore
                    (if relative: starting from the root of each watched dir).
  -c --clear        Automatically clear the screen before each run.
  --beforerun=<cmd> Run arbitrary command before tests are run.
  --onpass=<cmd>    Run arbitrary command on pass.
  --onfail=<cmd>    Run arbitrary command on failure.
  --onexit=<cmd>    Run arbitrary command when exiting.
  --nobeep          Do not beep on failure.
  -p --poll         Use polling instead of events (useful in VMs).
  --ext=<exts>      Comma-separated list of file extensions that trigger a
                    new test run when changed (default: .py).
  --no-spool        Disable event spooling (default: 200ms cooldown).
  -v --verbose      Increase verbosity of the output.
  -q --quiet        Decrease verbosity of the output
                    (takes precedence over verbose).
"""

import sys

import colorama
from docopt import docopt

from .watcher import watch
from . import __version__

import pytest

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0


def main(argv=None):
    """
    The entry point of the application.
    """
    colorama.init()

    usage = __doc__[__doc__.find('Usage:'):]
    version = 'pytest-watch ' + __version__
    argv = argv if argv is not None else sys.argv[1:]
    args_cmd = docopt(usage, argv=argv, version=version)

    config_ini = ConfigParser()
    pytest_ini_path = get_pytest_ini_path()
    config_ini.read(pytest_ini_path)
    args_ini = {}
    if config_ini.has_section("pytest-watch"):
        # string config values
        if config_ini.has_option("pytest-watch", "onpass"):
            args_ini['--onpass'] = config_ini.get("pytest-watch", "onpass")
        else:
            args_ini['--onpass'] = None

        if config_ini.has_option("pytest-watch", "onfail"):
            args_ini['--onfail'] = config_ini.get("pytest-watch", "onfail")
        else:
            args_ini['--onfail'] = None

        if config_ini.has_option("pytest-watch", "beforerun"):
            args_ini['--beforerun'] = config_ini.get("pytest-watch", "beforerun")
        else:
            args_ini['--beforerun'] = None

        if config_ini.has_option("pytest-watch", "onexit"):
            args_ini['--onexit'] = config_ini.get("pytest-watch", "onexit")
        else:
            args_ini['--onexit'] = None

        if config_ini.has_option("pytest-watch", "ext"):
            args_ini['--ext'] = config_ini.get("pytest-watch", "ext")
        else:
            args_ini['--ext'] = None

        if config_ini.has_option("pytest-watch", "ignore"):
            args_ini['--ignore'] = config_ini.get("pytest-watch", "ignore")
        else:
            args_ini['--ignore'] = None

        # boolean config values
        if config_ini.has_option("pytest-watch", "help"):
            args_ini["--help"] = config_ini.getboolean("pytest-watch", "help")
        else:
            args_ini["--help"] = False

        if config_ini.has_option("pytest-watch", "version"):
            args_ini["--version"] = config_ini.getboolean("pytest-watch", "version")
        else:
            args_ini["--version"] = False

        if config_ini.has_option("pytest-watch", "clear"):
            args_ini["--clear"] = config_ini.getboolean("pytest-watch", "clear")
        else:
            args_ini["--clear"] = False

        if config_ini.has_option("pytest-watch", "nobeep"):
            args_ini["--nobeep"] = config_ini.getboolean("pytest-watch", "nobeep")
        else:
            args_ini["--nobeep"] = False

        if config_ini.has_option("pytest-watch", "poll"):
            args_ini["--poll"] = config_ini.getboolean("pytest-watch", "poll")
        else:
            args_ini["--poll"] = False

        if config_ini.has_option("pytest-watch", "no-spool"):
            args_ini["--no-spool"] = config_ini.getboolean("pytest-watch", "no-spool")
        else:
            args_ini["--no-spool"] = False

        if config_ini.has_option("pytest-watch", "verbose"):
            args_ini["--verbose"] = config_ini.getboolean("pytest-watch", "verbose")
        else:
            args_ini["--verbose"] = False

        if config_ini.has_option("pytest-watch", "quiet"):
            args_ini["--quiet"] = config_ini.getboolean("pytest-watch", "quiet")
        else:
            args_ini["--quiet"] = False

        # other config values
        if config_ini.has_option("pytest-watch", "directories"):
            args_ini['<directories>'] = config_ini.get("pytest-watch", "directories")
            args_ini['<directories>'] = args_ini['<directories>'].split(", ")
        else:
            args_ini['<directories>'] = []

        if config_ini.has_option("pytest-watch", "addopts"):
            args_ini["<args>"] = config_ini.get("pytest-watch", "addopts")
        else:
            args_ini["<args>"] = None

    args = {}
    for arg_key in args_cmd:
        args[arg_key] = args_cmd[arg_key] or args_ini.get(arg_key)

    pytest_args = []
    directories = args['<directories>']
    if '--' in directories:
        index = directories.index('--')
        pytest_args = directories[index + 1:]
        directories = directories[:index]
    ignore = (args['--ignore'] or '').split(',')
    extensions = [('.' if not ext.startswith('.') else '') + ext
                  for ext in (args['--ext'] or '.py').split(',')]

    return watch(directories=directories,
                 ignore=ignore,
                 auto_clear=args['--clear'],
                 beep_on_failure=not args['--nobeep'],
                 onpass=args['--onpass'],
                 onfail=args['--onfail'],
                 beforerun=args['--beforerun'],
                 onexit=args['--onexit'],
                 poll=args['--poll'],
                 extensions=extensions,
                 args=pytest_args,
                 spool=not args['--no-spool'],
                 verbose=args['--verbose'],
                 quiet=args['--quiet'])

# For collecting path of the ini


class CollectIniPathPlugin(object):

    def pytest_cmdline_main(self, config):
        CollectorIniPath.pytest_ini_path = str(config.inifile.realpath())


class CollectorIniPath(object):

    """ Object for storing the path from CollectIniPathPlugin """
    pytest_ini_path = None


def get_pytest_ini_path():

    pytest.main("--collect-only", plugins=[CollectIniPathPlugin()])
    return(CollectorIniPath.pytest_ini_path)
