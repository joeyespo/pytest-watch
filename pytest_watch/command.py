"""\
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


def main(argv=None):
    """
    The entry point of the application.
    """
    colorama.init()

    usage = __doc__[__doc__.find('Usage:'):]
    version = 'pytest-watch ' + __version__
    argv = argv if argv is not None else sys.argv[1:]
    args = docopt(usage, argv=argv, version=version)

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
