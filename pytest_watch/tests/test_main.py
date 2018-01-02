import sys
import unittest
import shutil
import tempfile

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pytest_watch.command import main


class TestCLIArguments(unittest.TestCase):

    def _get_default_args(self):
        return dict(
                directories=[],
                ignore=[],
                extensions=[".py"],
                beep_on_failure=True,
                auto_clear=False,
                wait=False,
                beforerun=None,
                afterrun=None,
                onpass=None,
                onfail=None,
                onexit=None,
                runner=None,
                spool=200,
                poll=False,
                verbose=False,
                quiet=False,
                pytest_args=[]
            )

    @patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
    def test_default_parameters(self, watch_callee):
        main([])

        watch_callee.assert_called_once()
        watch_callee.assert_called_once_with(**self._get_default_args())

    @patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
    def test_empty_argv(self, watch_callee):
        sys.argv[1:] = []

        main()

        watch_callee.assert_called_once()
        watch_callee.assert_called_once_with(**self._get_default_args())

    @patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
    def test_zero_spool_value(self, watch_callee):
        main("--spool 0".split())
        self.assertIn("spool", watch_callee.call_args[1])
        self.assertEqual(0, watch_callee.call_args[1]["spool"])
        watch_callee.assert_called_once()

    @patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
    def test_positive_spool_value(self, watch_callee):
        main("--spool 2000".split())

        self.assertIn("spool", watch_callee.call_args[1])
        self.assertEqual(2000, watch_callee.call_args[1]["spool"])
        watch_callee.assert_called_once()

        watch_callee.reset_mock()

        main("--spool 20".split())

        self.assertIn("spool", watch_callee.call_args[1])
        self.assertEqual(20, watch_callee.call_args[1]["spool"])
        watch_callee.assert_called_once()

    @patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
    def test_default_spool_value(self, watch_callee):
        main([])

        self.assertIn("spool", watch_callee.call_args[1])
        self.assertEqual(200, watch_callee.call_args[1]["spool"])
        watch_callee.assert_called_once()

    @patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
    def test_cause_error_for_negative_spool_values(self, watch_callee):
        self.assertEqual(2, main("--spool -1".split()))
        watch_callee.assert_not_called()

    @patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
    def test_cause_error_for_invalid_spool_values(self, watch_callee):
        self.assertEquals(2, main("--spool abc".split()), "Status code for not integer 'spool' argument should be 2")
        self.assertEquals(2, main("--spool @".split()), "Status code for not integer 'spool' argument should be 2")
        self.assertEquals(2, main("--spool []".split()), "Status code for not integer 'spool' argument should be 2")

