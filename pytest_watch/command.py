"""
pytest_watch.command
~~~~~~~~~~~~~~~~~~~~

Implements the command-line interface for pytest-watch.


Usage: ptw [options] [--ignore <dir>...] [<directory>...] [-- <pytest-args>...]

Options:
  --ignore <dir>        Ignore directory from being watched and during
                        collection (multi-allowed).
  --ext <exts>          Comma-separated list of file extensions that can
                        trigger a new test run when changed (default: .py).
                        Use --ext=* to allow any file (including .pyc).
  --config <file>       Load configuration from `file` instead of trying to
                        locate one of the implicit configuration files.
  -c --clear            Clear the screen before each run.
  -n --nobeep           Do not beep on failure.
  -w --wait             Waits for all tests to complete before re-running.
                        Otherwise, tests are interrupted on filesystem events.
  --beforerun <cmd>     Run arbitrary command before tests are run.
  --afterrun <cmd>      Run arbitrary command on completion or interruption.
                        The exit code of "py.test" is passed as an argument.
  --onpass <cmd>        Run arbitrary command on pass.
  --onfail <cmd>        Run arbitrary command on failure.
  --onexit <cmd>        Run arbitrary command when exiting pytest-watch.
  --runner <cmd>        Run a custom command instead of "py.test".
  --pdb                 Start the interactive Python debugger on errors.
                        This also enables --wait to prevent pdb interruption.
  --spool <delay>       Re-run after a delay (in milliseconds), allowing for
                        more file system events to queue up (default: 200 ms).
  -p --poll             Use polling instead of OS events (useful in VMs).
  -v --verbose          Increase verbosity of the output.
  -q --quiet            Decrease verbosity of the output (precedence over -v).
  -V --version          Print version and exit.
  -h --help             Print help and exit.
"""

import sys

import colorama
from docopt import docopt

from . import __version__
from .config import merge_config
from .constants import ALL_EXTENSIONS
from .watcher import watch


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

    # Get paths and initial pytest arguments
    directories = args['<directory>']
    pytest_args = list(directories)
    if '--' in directories:
        index = directories.index('--')
        directories = directories[:index]
        del pytest_args[index]

    # Adjust pytest and --collect-only args
    for ignore in args['--ignore'] or []:
        pytest_args.extend(['--ignore', ignore])
    if args['--config']:
        pytest_args.extend(['-c', args['--config']])

    # Merge config file options
    if not merge_config(args, pytest_args, verbose=args['--verbose']):
        return 0

    # Adjust pytest args
    if args['--pdb']:
        pytest_args.append('--pdb')

    # Parse extensions
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

    # Run pytest and watch for changes
    return watch(entries=directories,
                 ignore=args['--ignore'],
                 extensions=extensions,
                 beep_on_failure=not args['--nobeep'],
                 auto_clear=args['--clear'],
                 wait=args['--wait'] or '--pdb' in pytest_args,
                 beforerun=args['--beforerun'],
                 afterrun=args['--afterrun'],
                 onpass=args['--onpass'],
                 onfail=args['--onfail'],
                 onexit=args['--onexit'],
                 runner=args['--runner'],
                 spool=spool,
                 poll=args['--poll'],
                 verbose=args['--verbose'],
                 quiet=args['--quiet'],
                 pytest_args=pytest_args)
