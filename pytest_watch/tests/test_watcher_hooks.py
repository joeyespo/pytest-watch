import subprocess
from subprocess import call as _subcall
import sys
import unittest

try:
    from unittest import mock
except ImportError:
    import mock


from pytest_watch.constants import EXIT_NOTESTSCOLLECTED, EXIT_OK
from pytest_watch.watcher import watch, run_hook
from pytest_watch.watcher import subprocess as wsubprocess


def build_popen_mock(popen, config):
    mockmock = mock.Mock()
    mockmock.configure_mock(**config)
    popen.return_value = mockmock


def raise_keyboard_interrupt(*args, **kwargs):
    # force keyboard interruption
    raise KeyboardInterrupt()


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

    @mock.patch("pytest_watch.watcher.subprocess.call",
           side_effect=assertion_wrapper(0, _subcall))
    def test_run_hook_systemexit_0(self, call_mock):
        python_exec = sys.executable
        cmd_parts = [python_exec, "-c", "'exit(0)'"]
        cmd = " ".join(cmd_parts)
        run_hook(cmd)
        call_mock.assert_called_once_with(cmd, shell=True)

    @mock.patch("pytest_watch.watcher.subprocess.call",
           side_effect=assertion_wrapper(1, _subcall))
    def test_run_hook_systemexit_not_0(self, call_mock):
        python_exec = sys.executable
        cmd_parts = [python_exec, "-c", "'exit(1)'"]
        cmd = " ".join(cmd_parts)
        run_hook(cmd)
        call_mock.assert_called_once_with(cmd, shell=True)


from pytest_watch import watcher
orig = watcher.run_hook

def get_hook_stop_iteration(command_str):
    def hook(cmd, *args):
        orig(cmd, *args)
        if cmd == command_str:
            raise StopIteration("Force this only for tests purpose")
    return hook


@mock.patch.object(wsubprocess, "Popen")
@mock.patch("pytest_watch.watcher.subprocess.call",
            side_effect=lambda *args, **kwargs: 0)
class TestRunHookCallbacks(unittest.TestCase):

    def test_with_beforerun(self, call_mock, popen_mock):
        """
        Test if beforerun callback is called if it is passed as argument
        """
        config = {"poll.side_effect": raise_keyboard_interrupt,
                  "wait.return_value": 0}
        build_popen_mock(popen_mock, config)

        beforerun="{} -c 'exit(0) #it is beforerun'".format(sys.executable)

        watch(beforerun=beforerun)

        call_mock.assert_called_once_with(beforerun, shell=True)

    @mock.patch("pytest_watch.helpers.send_keyboard_interrupt")
    def test_afterrun_on_keyboard_interruption(self, keyb_int, call_mock,
                                               popen_mock):
        config = {"poll.side_effect": raise_keyboard_interrupt,
                  "wait.return_value": 10}
        build_popen_mock(popen_mock, config)

        afterrun="{} -m this".format(sys.executable)

        watch(afterrun=afterrun, wait=True)

        keyb_int.assert_not_called()

        call_mock.assert_called_once()

        expected_cmd = afterrun + " 10" # should run with p.wait() arg

        call_mock.assert_called_once_with(expected_cmd, shell=True)

    @mock.patch("pytest_watch.helpers.send_keyboard_interrupt")
    def test_afterrun_without_keyboard_interruption(self, keyb_int, call_mock,
                                                    popen_mock):
        config = {"poll.side_effect": lambda: 999}
        build_popen_mock(popen_mock, config)

        afterrun="{} -c 'exit(0) #it is afterrun'".format(sys.executable)

        watcher.run_hook = get_hook_stop_iteration(afterrun)

        watch(afterrun=afterrun, wait=True)

        keyb_int.assert_not_called()

        call_mock.assert_called_once()

        expected_cmd = afterrun + " 999" # should run with exit_code arg

        call_mock.assert_called_once_with(expected_cmd, shell=True)

    def test_onpass_on_exit(self, call_mock, popen_mock):
        config = {"poll.side_effect": lambda: EXIT_OK}
        build_popen_mock(popen_mock, config)

        onpass="{} -c 'exit(0) #it is afterpass on exit'"\
                .format(sys.executable)

        watcher.run_hook = get_hook_stop_iteration(onpass)
        watch(onpass=onpass, wait=True)

        call_mock.assert_called_once_with(onpass, shell=True)

    def test_onpass_on_not_tests_collected(self, call_mock, popen_mock):
        config = {"poll.side_effect": lambda: EXIT_NOTESTSCOLLECTED}
        build_popen_mock(popen_mock, config)

        onpass="{} -c 'exit(0) #it is afterpass on not_tests_collected'"\
                .format(sys.executable)
        watcher.run_hook = get_hook_stop_iteration(onpass)
        watch(onpass=onpass, wait=True)

        call_mock.assert_called_once_with(onpass, shell=True)

    @mock.patch("pytest_watch.watcher.beep")
    def test_onfail_without_beep(self, beep_mock, call_mock, popen_mock):
        config = {"poll.side_effect": lambda: -1000}
        build_popen_mock(popen_mock, config)

        onfail="{} -c 'exit(1) # failure happens'"\
                .format(sys.executable)
        watcher.run_hook = get_hook_stop_iteration(onfail)
        watch(onfail=onfail, wait=True, beep_on_failure=False)

        call_mock.assert_called_once_with(onfail, shell=True)
        beep_mock.assert_not_called()

    @mock.patch("pytest_watch.watcher.beep")
    def test_onfail_without_beep(self, beep_mock, call_mock, popen_mock):
        config = {"poll.side_effect": lambda: -1000}
        build_popen_mock(popen_mock, config)

        onfail="{} -c 'exit(1) # failure happens'"\
                .format(sys.executable)
        watcher.run_hook = get_hook_stop_iteration(onfail)
        watch(onfail=onfail, wait=True, beep_on_failure=True)

        call_mock.assert_called_once_with(onfail, shell=True)
        beep_mock.assert_called_once()


@unittest.skip("baby steps")
class TestRunHooksSkiped(unittest.TestCase):

    def test_run_hook_with_args(self):
        assert False, "Not yet implemented"

    def test_run_hook_without_args(self):
        assert False, "Not yet implemented"

    def test_onexit(self):
        assert False, "Not yet implemented."
