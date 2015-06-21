"""
pytest_watch
------------

Local continuous test runner with pytest and watchdog.

:copyright: (c) 2014 by Joe Esposito.
:license: MIT, see LICENSE for more details.
"""

import os
import sys


if __name__ == '__main__':
    sys.path.append(os.path.dirname(__file__))

    from pytest_watch.command import main
    main()
