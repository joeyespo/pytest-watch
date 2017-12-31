import unittest

from pytest_watch.command import main

from unittest.mock import patch


class TestCLIArguments(unittest.TestCase):

    @patch("pytest_watch.command.watch")
    def test_default_parameters(self, watch_callee):
        watch_callee.side_effect = lambda *args, **kwargs: 0

        default_args = dict(
            directories=[],
            ignore=[],
            extensions=None,
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

        main([])

        watch_callee.assert_called_once()
        watch_callee.assert_called_once_with(**default_args)

