import pytest

from pytest_watch.util import silence


def test_handle_exception_type():
    with pytest.raises(ValueError) as ex:
        with silence():
            raise ValueError("Custom message error")
    assert ex.errisinstance(ValueError)


def test_handle_exception_message():
    with pytest.raises(KeyError) as ex:
        with silence():
            raise KeyError("Custom message error")
    assert ex.match("Custom message error")
