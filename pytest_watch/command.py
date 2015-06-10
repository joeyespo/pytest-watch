"""\
pytest_watch.command
~~~~~~~~~~~~~~~~~~~~

Implements the command-line interface for pytest-watch.

All positional arguments after `--` are passed directly to py.test executable.


Usage:
  ptw [options] [<directories>...] [-- <args>...]

Options:
  -h --help         Show this help.
  --version         Show version.
  --ignore=<dirs>   Command-separated list of directories to ignore when descending
                    (if relative: starting from the root of each watched dir).
  -c --clear        Automatically clear the screen before each run.
  --onpass=<cmd>    Run arbitrary command on pass.
  --onfail=<cmd>    Run arbitrary command on failure.
  --nobeep          Do not beep on failure.
  -p --poll         Use polling instead of events (useful in VMs).
  --ext=<exts>      Comma-separated list of file extensions that trigger a
                    new test run when changed (default: .py).
"""

import sys

import colorama
from docopt import docopt

from .watcher import watch
from . import __version__


def main(argv=None):
    """The entry point of the application."""
    colorama.init()

    usage = __doc__[__doc__.find('Usage:'):]
    version = 'pytest-watch ' + __version__
    argv = argv if argv is not None else sys.argv[1:]
    args = docopt(usage, argv=argv, version=version)

    directories, pytest_args = args['<directories>'], []
    if '--' in directories:
        ix = directories.index('--')
        directories, pytest_args = directories[:ix], directories[(ix + 1):]

    ignore = (args['--ignore'] or '').split(',')
    extensions = [
        '.' * (not ext.startswith('.')) + ext
        for ext in (args['--ext'] or '.py').split(',')
    ]
    print(ignore, extensions)

    return watch(directories=directories,
                 ignore=ignore,
                 auto_clear=args['--clear'],
                 beep_on_failure=not args['--nobeep'],
                 onpass=args['--onpass'],
                 onfail=args['--onfail'],
                 poll=args['--poll'],
                 extensions=extensions,
                 args=pytest_args)
