"""\
pytest_watch.command
~~~~~~~~~~~~~~~~~~~~

Implements the command-line interface for pytest-watch.


Usage:
  ptw [options] [<directory>]

Options:
  -h --help         Show this help.
  --version         Show version.
  -c --clear        Automatically clear the screen before each run.
  --onpass=<cmd>    Run arbitrary programs on pass.
  --onfail=<cmd>    Run arbitrary programs on failure.
"""

import sys
from docopt import docopt
from .watcher import watch
from . import __version__


def main(argv=None):
    """The entry point of the application."""
    if argv is None:
        argv = sys.argv[1:]
    usage = '\n\n\n'.join(__doc__.split('\n\n\n')[1:])
    version = 'pytest-watch ' + __version__

    # Parse options
    args = docopt(usage, argv=argv, version=version)

    # Execute
    return watch(args['<directory>'], args['--clear'], args['--onpass'], args['--onfail'])
