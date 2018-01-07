import subprocess
from subprocess import call as _subcall
import sys
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pytest_watch.watcher import watch, run_hook


def assertion_wrapper(expected, callee, message=None):
    """
    Adapter to support assertions as side_effect for patched objects.

    TODO: This implementation can be more generalized for assertions, i.e. !=,
    using lambdas. For the moment, its satisfies run_hook tests.
    """
    def _wrapped(*args, **kwargs):
        if message:
            assert expected == callee(*args, **kwargs), message
        else:
            assert expected == callee(*args, **kwargs)
    return _wrapped


class TestRunHooksBasic(unittest.TestCase):

    @patch("pytest_watch.watcher.subprocess.call",
           side_effect=assertion_wrapper(0, _subcall))
    def test_run_hook_systemexit_0(self, call_mock):
        python_exec = sys.executable
        cmd_parts = [python_exec, "-c", "'exit(0)'"]
        cmd = " ".join(cmd_parts)
        run_hook(cmd)
        call_mock.assert_called_once_with(cmd, shell=True)

    @patch("pytest_watch.watcher.subprocess.call",
           side_effect=assertion_wrapper(1, _subcall))
    def test_run_hook_systemexit_not_0(self, call_mock):
        python_exec = sys.executable
        cmd_parts = [python_exec, "-c", "'exit(1)'"]
        cmd = " ".join(cmd_parts)
        run_hook(cmd)
        call_mock.assert_called_once_with(cmd, shell=True)


@patch("pytest_watch.watcher.subprocess.Popen", autospec=subprocess.Popen)
@patch("pytest_watch.watcher.subprocess.call",
       side_effect=assertion_wrapper(0, _subcall))
class TestRunHookCallbacks(unittest.TestCase):

    def test_beforerun(self, call_mock, popen_mock):
        def raise_keyboard_interrupt():
            raise KeyboardInterrupt

        popen_mock.poll = raise_keyboard_interrupt

        beforerun="python -c 'exit(0) #it is beforerun'"

        watch(beforerun=beforerun)

        assert 1 == call_mock.call_count, \
               "Only beforerun is expected to be called."
        call_mock.assert_called_with(beforerun, shell=True)

    def test_afterrun_for_keyboard_interruption(self, call_mock, popen_mock):
        # force keyboard interruption
        def raise_keyboard_interrupt():
            raise KeyboardInterrupt

        popen_mock.poll = raise_keyboard_interrupt

        afterrun="python -c 'exit(0) #it is afterrun'"

        watch(afterrun=afterrun)

        assert 1 == call_mock.call_count, \
               "Only afterrun is expected to be called."

        assert call_mock.call_args[0][0].startswith(afterrun + " ")
        assert "shell" in call_mock.call_args[1]
        assert True == call_mock.call_args[1]["shell"]


@unittest.skip("baby steps")
class TestRunHooksSkiped(unittest.TestCase):

    def test_run_hook_with_args(self):
        assert False, "Not yet implemented"

    def test_run_hook_without_args(self):
        assert False, "Not yet implemented"

    def test_afterrun_on_keyboard_interruption(self):
        assert False, "Not yet implemented."

    def test_afterrun_with_exit_code(self):
        assert False, "Not yet implemented."

    def test_onpass(self):
        assert False, "Not yet implemented."

    def test_onfail(self):
        assert False, "Not yet implemented."

    def test_onexit(self):
        assert False, "Not yet implemented."
