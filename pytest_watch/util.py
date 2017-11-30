import importlib
import os
import sys
from contextlib import contextmanager

sentinel = object()


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


def import_function_from_module(fn_name, module_path, default=sentinel):
    throw = default == sentinel

    if not module_path:
        if throw:
            raise ImportError('Must specify a module to import %s from' % fn_name)
        return default

    try:
        mod = importlib.import_module(module_path)
    except ImportError as e:
        if throw:
            raise e
        return default

    if throw and not hasattr(mod, fn_name):
        raise Exception('Expected the function %s to exist in the %s module'
                        '' % (fn_name, module_path))

    return getattr(mod, fn_name, default)
