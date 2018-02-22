import os
import sys

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pytest_watch import __main__
from pytest_watch.__main__ import run_cli


@patch("pytest_watch.command.main", side_effect=lambda argv=None: 0)
def test_add_pytest_watch_folder_to_path(main):
    run_cli()
    assert os.path.dirname(__main__.__file__) in sys.path
