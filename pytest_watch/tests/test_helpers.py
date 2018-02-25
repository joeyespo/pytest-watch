import signal
import subprocess
import sys

import pytest
from pytest_watch import helpers


@pytest.fixture
def windows_ctrlc_mock(mocker):
    k32_mock = mocker.patch("pytest_watch.helpers.ctypes")
    ctrlc_mock = mocker.patch.object(k32_mock.windll.kernel32, "GenerateConsoleCtrlEvent")
    return ctrlc_mock


@pytest.fixture
def python_version_proc():
    return subprocess.Popen(sys.executable,
                            shell=helpers.is_windows)


def test_linux_process_kill_is_called(mocker, python_version_proc):
    is_windows = mocker.patch.dict("pytest_watch.helpers.__dict__",
                                   {"is_windows": False})

    os_mock = mocker.patch("pytest_watch.helpers.os")

    kill_mock = mocker.patch.object(os_mock, "kill",
                                    side_effect=lambda pid, s: pid)

    helpers.send_keyboard_interrupt(python_version_proc)

    assert 1 == kill_mock.call_count
    assert (python_version_proc.pid, signal.SIGINT) == kill_mock.call_args[0]


def test_windows_process_kill_for_python26upper_is_called(mocker,
                                                          python_version_proc,
                                                          windows_ctrlc_mock):
    ctrl_c_code = signal.SIGINT

    is_windows = mocker.patch.dict("pytest_watch.helpers.__dict__",
                                   {"is_windows": True})
    ctrl_c_event = mocker.patch.dict("pytest_watch.helpers.signal.__dict__",
                                     {"CTRL_C_EVENT": ctrl_c_code})

    os_mock = mocker.patch("pytest_watch.helpers.os")

    kill_mock = mocker.patch.object(os_mock, "kill",
                                    side_effect=lambda pid, s: pid)

    mocker.patch.object(python_version_proc, "wait")
    helpers.send_keyboard_interrupt(python_version_proc)

    assert 0 == windows_ctrlc_mock.call_count
    assert 1 == kill_mock.call_count
    assert (0, ctrl_c_code) == kill_mock.call_args[0]


def test_windows_process_kill_for_python26_is_called(mocker,
                                                     windows_ctrlc_mock,
                                                     python_version_proc):
    ctrl_c_code = signal.SIGINT

    is_windows = mocker.patch.dict("pytest_watch.helpers.__dict__",
                                   {"is_windows": True})
    ctrl_c_event = mocker.patch.dict("pytest_watch.helpers.signal.__dict__",
                                     {"CTRL_C_EVENT": ctrl_c_code})

    os_mock = mocker.patch("pytest_watch.helpers.os")

    kill_mock = mocker.patch.object(os_mock, "kill",
                                    side_effect=AttributeError)

    mocker.patch.object(python_version_proc, "wait")
    helpers.send_keyboard_interrupt(python_version_proc)

    assert 1 == windows_ctrlc_mock.call_count
    assert (0, 0) == windows_ctrlc_mock.call_args[0]
