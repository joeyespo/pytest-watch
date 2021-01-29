"""
pytest_watch
------------

Local continuous test runner with pytest and watchdog.

:copyright: (c) 2014-2016 by Joe Esposito.
:license: MIT, see LICENSE for more details.
"""

__version__ = '2021.01.29'


from .command import main, doc, version
from .watcher import watch


__all__ = ['main', 'doc', 'version', 'watch']
