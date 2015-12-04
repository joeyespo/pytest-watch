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
  --runner=<cmd>    Run a custom command instead of py.test.
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

    # string ini config values
    args_ini["--onpass"] = get_ini_option(config_ini, "onpass")

    args_ini["--onfail"] = get_ini_option(config_ini, "onfail")

    args_ini["--beforerun"] = get_ini_option(config_ini, "beforerun")

    args_ini["--onexit"] = get_ini_option(config_ini, "onexit")

    args_ini["--ext"] = get_ini_option(config_ini, "ext")

    args_ini["--ignore"] = get_ini_option(config_ini, "ignore")

    # boolean ini config values
    args_ini["--help"] = get_ini_option_boolean(config_ini, "help")

    args_ini["--version"] = get_ini_option_boolean(config_ini, "version")

    args_ini["--clear"] = get_ini_option_boolean(config_ini, "clear")

    args_ini["--nobeep"] = get_ini_option_boolean(config_ini, "nobeep")

    args_ini["--poll"] = get_ini_option_boolean(config_ini, "poll")

    args_ini["--no-spool"] = get_ini_option_boolean(config_ini, "no-spool")

    args_ini["--verbose"] = get_ini_option_boolean(config_ini, "verbose")

    args_ini["--quiet"] = get_ini_option_boolean(config_ini, "quiet")

    # other config values
    if config_ini.has_option("pytest-watch", "directories"):
        args_ini['<directories>'] = config_ini.get("pytest-watch", "directories")
        args_ini['<directories>'] = args_ini['<directories>'].split(", ")
    else:
        args_ini['<directories>'] = []

    args_ini["<args>"] = get_ini_option(config_ini, "addopts")

    args = {}
    for arg_key in args_cmd:
        args[arg_key] = args_cmd[arg_key] or args_ini.get(arg_key)
    if args["--verbose"]:
        print("pytest-watch args: " + str(args))

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
                 runner=args['--runner'],
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
        CollectorIniPath.pytest_ini_path = config.inifile.realpath().strpath


class CollectorIniPath(object):

    """ Object for storing the path from CollectIniPathPlugin """
    pytest_ini_path = None


def get_pytest_ini_path():

    pytest.main("--collect-only", plugins=[CollectIniPathPlugin()])
    return(CollectorIniPath.pytest_ini_path)


def get_ini_option(config_parser, option_name):
    if config_parser.has_option("pytest-watch", option_name):
        return config_parser.get("pytest-watch", option_name)
    else:
        return None


def get_ini_option_boolean(config_parser, option_name):
    if config_parser.has_option("pytest-watch", option_name):
        return config_parser.getboolean("pytest-watch", option_name)
    else:
        return False
