"""
pytest_watch.command
~~~~~~~~~~~~~~~~~~~~

Implements the command-line interface for pytest-watch.

All positional arguments after `--` are passed directly to py.test executable.


Usage: ptw [options] [<directories>...] [-- <args>...]

Options:
  -h --help             Show this help.
  --version             Show version.
  --ignore=<dirs>       Comma-separated list of directories to ignore
                        (if relative, starts from root of each watched dir).
  -c --clear            Automatically clear the screen before each run.
  --beforerun=<cmd>     Run arbitrary command before tests are run.
  --afterrun <cmd>      Run arbitrary command on completion or interruption.
                        The exit code of "py.test" is passed as an argument.
  --onpass=<cmd>        Run arbitrary command on pass.
  --onfail=<cmd>        Run arbitrary command on failure.
  --onexit=<cmd>        Run arbitrary command when exiting pytest-watch.
  --runner=<cmd>        Run a custom command instead of "py.test".
  --pdb                 Start the interactive Python debugger on errors.
                        This also enables --wait to prevent pdb interruption.
  --nobeep              Do not beep on failure.
  -p --poll             Use polling instead of OS events (useful in VMs).
  --spool=<ms>          Re-run only after this delay (in milliseconds) to allow
                        more file system events to queue up (default: 200 ms).
  --ext=<exts>          Comma-separated list of file extensions that trigger a
                        new test run when changed (default: .py).
                        Use --ext=* to run on any file (including .pyc).
  -w --wait             Waits for all tests to complete before re-running.
                        Otherwise, tests are interrupted on filesystem events.
  -v --verbose          Increase verbosity of the output.
  -q --quiet            Decrease verbosity of the output
                        (takes precedence over verbose).
"""

import sys

import colorama
from docopt import docopt

from . import __version__
from .watcher import ALL_EXTENSIONS, watch
from .config import merge_config


doc = '\n\n\n'.join(__doc__.split('\n\n\n')[1:])
version = 'pytest-watch ' + __version__


def main(argv=None):
    """
    The entry point of the application.
    """
    if argv is None:
        argv = sys.argv[1:]

    # Initialize terminal colors
    colorama.init()

    # Parse CLI arguments
    args = docopt(doc, argv=argv, version=version)

    # Split paths and pytest arguments
    pytest_args = []
    directories = args['<directories>']
    if '--' in directories:
        index = directories.index('--')
        directories, pytest_args = directories[:index], directories[index + 1:]

    # Merge config file options
    merge_config(args, directories)

    ignore = (args['--ignore'] or '').split(',')
    if args['--ext'] == '*':
        extensions = ALL_EXTENSIONS
    elif args['--ext']:
        extensions = [('.' if not e.startswith('.') else '') + e
                      for e in args['--ext'].split(',')]
    else:
        extensions = None

    # Parse numeric arguments
    spool = args['--spool']
    if spool is not None:
        try:
            spool = int(spool)
        except ValueError:
            sys.stderr.write('Error: Spool must be an integer.\n')
            return 2

    # Adjust pytest args
    if args['--pdb']:
        pytest_args.append('--pdb')

    # Run pytest and watch for changes
    return watch(directories=directories,
                 ignore=ignore,
                 auto_clear=args['--clear'],
                 beep_on_failure=not args['--nobeep'],
                 onpass=args['--onpass'],
                 onfail=args['--onfail'],
                 runner=args['--runner'],
                 beforerun=args['--beforerun'],
                 afterrun=args['--afterrun'],
                 onexit=args['--onexit'],
                 poll=args['--poll'],
                 extensions=extensions,
                 args=pytest_args,
                 spool=spool,
                 wait=args['--wait'] or args['--pdb'],
                 verbose=args['--verbose'],
                 quiet=args['--quiet'])
