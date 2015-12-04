"""
pytest_watch
------------

Local continuous test runner with pytest and watchdog.

:copyright: (c) 2015 by Joe Esposito.
:license: MIT, see LICENSE for more details.
"""

__version__ = '3.8.0'


from .command import main, usage, version
from .watcher import watch


__all__ = ['main', 'usage', 'version', 'watch']
