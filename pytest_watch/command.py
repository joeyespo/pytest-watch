"""\
pytest_watch.command
~~~~~~~~~~~~~~~~~~~~

Implements the command-line interface for pytest-watch.


Usage:
  ptw [options] [<directory>]

Options:
  -h --help                 Show this help.
  --version                 Show version.
  -c --clear                Automatically clear the screen before each run.
  --onpass=<cmd>            Run arbitrary programs on pass.
  --onfail=<cmd>            Run arbitrary programs on failure.
  --nobeep                  Do not beep on failure.
  --nowatchdirs=<fnmatch>   Do not watch any directory basename which matches one 
                            of the patterns supplied
                            (similar to pytest's norecursedirs)
  --ext=<exts>              Comma-separated list of file extensions that trigger a
                            new test run when changed (default: .py)
"""

import sys

import colorama
from docopt import docopt

from .watcher import watch
from . import __version__


def main(argv=None):
    """The entry point of the application."""
    colorama.init()

    if argv is None:
        argv = sys.argv[1:]
    usage = '\n\n\n'.join(__doc__.split('\n\n\n')[1:])
    version = 'pytest-watch ' + __version__

    args = docopt(usage, argv=argv, version=version)

    extensions = args['--ext'].split(',') if args['--ext'] else []
    return watch(args['<directory>'], args['--clear'], not args['--nobeep'],
                 args['--onpass'], args['--onfail'], args['--nowatchdirs'], 
                 extensions)
