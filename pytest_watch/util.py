import os
import sys
from contextlib import contextmanager


@contextmanager
def silence():
    """
    Silence stdout and stderr in a 'with' block.
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    nullfd = open(os.devnull, 'w')
    sys.stdout = nullfd
    sys.stderr = nullfd

    try:
        yield
    except Exception:
        raise
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        nullfd.close()
