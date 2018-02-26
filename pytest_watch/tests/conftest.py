import pytest


@pytest.fixture
def merge_config_callee(mocker):
    m = mocker.patch("pytest_watch.command.merge_config",
                     side_effect=lambda *args, **kwargs: True)
    return m


@pytest.fixture
def beep_mock(mocker):
    return mocker.patch("pytest_watch.helpers.beep")


@pytest.fixture
def watch_callee(mocker):
    watch_mock = mocker.patch("pytest_watch.command.watch")
    watch_mock.return_value.side_effect = lambda *args, **kwargs: 0
    return watch_mock
