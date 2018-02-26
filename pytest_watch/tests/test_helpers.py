import os
import signal
import subprocess
import sys
from time import sleep

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

import pytest
from pytest_watch import helpers


@pytest.fixture
def windows_ctrlc_mock(mocker):
    k32_mock = mocker.patch("pytest_watch.helpers.ctypes")
    ctrlc_mock = mocker.patch.object(k32_mock.windll.kernel32,
                                     "GenerateConsoleCtrlEvent")
    return ctrlc_mock


@pytest.fixture
def python_version_proc():
    return subprocess.Popen(sys.executable,
                            shell=helpers.is_windows)


def test_linux_clear_with_clear_command(mocker):
    is_windows = mocker.patch.dict("pytest_watch.helpers.__dict__",
                                   {"is_windows": False})

    call_mock = mocker.patch("pytest_watch.helpers.subprocess.call")

    helpers.clear()

    assert 1 == call_mock.call_count
    assert ("clear",) == call_mock.call_args[0]
    assert dict(shell=True) == call_mock.call_args[1]


def test_windows_clear_with_cls_command(mocker):
    is_windows = mocker.patch.dict("pytest_watch.helpers.__dict__",
                                   {"is_windows": True})

    call_mock = mocker.patch("pytest_watch.helpers.subprocess.call")

    helpers.clear()

    assert 1 == call_mock.call_count
    assert ("cls",) == call_mock.call_args[0]
    assert dict(shell=True) == call_mock.call_args[1]


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
                                    side_effect=KeyboardInterrupt)

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


def test_dequeall_from_an_empty_queue_with_no_spool():
    q = Queue()
    assert [] == helpers.dequeue_all(q, 0)


def test_dequeall_from_a_single_queue_with_no_spool():
    q = Queue()
    q.put("element 1")
    assert ["element 1"] == helpers.dequeue_all(q, 0)


def test_dequeall_from_multi_queue_with_no_spool():
    q = Queue()
    q.put("element 1")
    assert ["element 1"] == helpers.dequeue_all(q, 0)
    q.put("element 2")
    q.put("element 3")
    assert ["element 2", "element 3"] == helpers.dequeue_all(q, 0)


def test_dequeall_from_multi_with_spool_200(mocker):
    def _is_first_empty():
        empty = False
        yield empty

    sleep_mock = mocker.patch("pytest_watch.helpers.sleep", wrap=sleep)
    q = Queue()
    mocker.patch.object(q, "empty", side_effect=_is_first_empty)
    q.put("element 1")
    q.put("element 2")
    dequeued = helpers.dequeue_all(q)
    sleep(.3)
    q.put("element 3")
    assert (.2,) == sleep_mock.call_args[0]
    assert ["element 1", "element 2"] == dequeued
    assert ["element 3"] == helpers.dequeue_all(q, 0)


def test_samepath_for_non_existent_file_without_errors(tmpdir):
    samedir = tmpdir.mkdir("samepath")
    file1 = samedir.join("file1.txt")
    with open(file1.strpath, "w") as f:
        f.write(".")
    file2 = samedir.join("inexistent.txt")

    assert file1.exists()
    assert not file2.exists()
    assert not helpers.samepath(file1.strpath, file2.strpath)


def test_samepath_for_name_spaced_symbolic_link(tmpdir):
    samedir = tmpdir.mkdir("samepath")
    file1 = samedir.join("file1.txt")
    with open(file1.strpath, "w") as f:
        f.write(".")
    symlink = samedir.join("Symbolic Link.txt")
    symlink.mksymlinkto(file1)

    assert os.path.islink(symlink.strpath)
    assert helpers.samepath(file1.strpath, symlink.strpath)


def test_samepath_for_symbolic_link(tmpdir):
    samedir = tmpdir.mkdir("samepath")
    file1 = samedir.join("file1.txt")
    with open(file1.strpath, "w") as f:
        f.write(".")
    symlink = samedir.join("symlink1.txt")
    symlink.mksymlinkto(file1)

    assert os.path.islink(symlink.strpath)
    assert helpers.samepath(file1.strpath, symlink.strpath)


def test_samepath_for_same_file(tmpdir):
    samedir = tmpdir.mkdir("samepath")
    file1 = samedir.join("file1.txt")
    assert helpers.samepath(file1.strpath, file1.strpath)


def test_samepath_fail_for_different_absolute_path(tmpdir):
    samedir = tmpdir.mkdir("samepath")
    assert not helpers.samepath(samedir.join("file1.txt").strpath,
                                samedir.join("file2.txt").strpath)
