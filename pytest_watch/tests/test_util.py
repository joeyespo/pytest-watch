import pytest

from pytest_watch.util import silence


def test_handle_exception():
    with pytest.raises(Exception) as ex:
        with silence():
            raise ValueError()
    assert ex.errisinstance(ValueError)
