"""
pytest_watch
------------

Local continuous test runner with pytest and watchdog.

:copyright: (c) 2014 by Joe Esposito.
:license: MIT, see LICENSE for more details.
"""


def run_cli():
    import os
    import sys

    sys.path.append(os.path.dirname(__file__))

    from pytest_watch.command import main
    main(argv=sys.argv[1:])

if __name__ == '__main__': run_cli()
