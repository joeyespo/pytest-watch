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


class TestSpoolArguments(unittest.TestCase):

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
        self.assertEquals(2, main("--spool abc".split()),
                          "Status code for not integer 'spool' " \
                          "argument should be 2")
        self.assertEquals(2, main("--spool @".split()),
                          "Status code for not integer 'spool' " \
                          "argument should be 2")
        self.assertEquals(2, main("--spool []".split()),
                          "Status code for not integer 'spool' " \
                          "argument should be 2")


@patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
class TestExtensionsArguments(unittest.TestCase):

    def test_default_extensions(self, watch_callee):
        main([])
        self.assertIn("extensions", watch_callee.call_args[1])
        self.assertListEqual([".py"], watch_callee.call_args[1]["extensions"])
        watch_callee.assert_called_once()

    def test_single_without_dot_extensions(self, watch_callee):
        main("--ext py".split())
        self.assertIn("extensions", watch_callee.call_args[1])
        self.assertListEqual([".py"], watch_callee.call_args[1]["extensions"])
        watch_callee.assert_called_once()

    def test_single_with_dot_extensions(self, watch_callee):
        main("--ext .py".split())
        self.assertIn("extensions", watch_callee.call_args[1])
        self.assertListEqual([".py"], watch_callee.call_args[1]["extensions"])
        watch_callee.assert_called_once()

    def test_multiple_extensions(self, watch_callee):
        main("--ext .py,.html".split())
        self.assertIn("extensions", watch_callee.call_args[1])
        self.assertListEqual([".py", ".html"], watch_callee.call_args[1]["extensions"])
        watch_callee.assert_called_once()

    def test_multiple_with_and_without_dots_extensions(self, watch_callee):
        main("--ext .py,html".split())
        self.assertIn("extensions", watch_callee.call_args[1])
        self.assertListEqual([".py", ".html"], watch_callee.call_args[1]["extensions"])
        watch_callee.assert_called_once()

        watch_callee.reset_mock()

        main("--ext py,.html".split())
        self.assertIn("extensions", watch_callee.call_args[1])
        self.assertListEqual([".py", ".html"], watch_callee.call_args[1]["extensions"])
        watch_callee.assert_called_once()


@patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
class TestDirectoriesAndPytestArgsArgumentsSplit(unittest.TestCase):

    def setUp(self):
        self.root_tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root_tmp)

    def test_no_directory_empty_pytest_arg(self, watch_callee):
        main(["--"])

        self.assertIn("pytest_args", watch_callee.call_args[1])
        self.assertListEqual([], watch_callee.call_args[1]["pytest_args"])
        watch_callee.assert_called_once()

    def test_no_directory_single_pytest_arg(self, watch_callee):
        main("-- --pdb".split())

        self.assertIn("pytest_args", watch_callee.call_args[1])
        self.assertListEqual(["--pdb"], watch_callee.call_args[1]["pytest_args"])
        watch_callee.assert_called_once()

    def test_no_directory_multiple_pytest_args(self, watch_callee):
        main("-- --pdb --cov=.".split())

        self.assertIn("pytest_args", watch_callee.call_args[1])
        self.assertListEqual(["--pdb", "--cov=."], watch_callee.call_args[1]["pytest_args"])
        watch_callee.assert_called_once()

    def test_multiple_directory_no_pytest_args(self, watch_callee):
        directories = [tempfile.mkdtemp(dir=self.root_tmp) for _ in range(2)]

        directories.append("--")
        main(directories)

        self.assertIn("pytest_args", watch_callee.call_args[1])
        self.assertIn("directories", watch_callee.call_args[1])

        fetched_pytest_args = watch_callee.call_args[1]["pytest_args"]
        fetched_directories = watch_callee.call_args[1]["directories"]

        self.assertListEqual(directories[:-1], fetched_directories)

        self.assertGreater(len(fetched_pytest_args), 1)
        self.assertEqual(len(fetched_pytest_args), len(fetched_directories))
        self.assertListEqual(fetched_directories, fetched_pytest_args)
        watch_callee.assert_called_once()

    def test_single_directory_no_pytest_args(self, watch_callee):
        main([self.root_tmp, "--"])

        self.assertIn("pytest_args", watch_callee.call_args[1])
        pytest_args = watch_callee.call_args[1]["pytest_args"]
        self.assertGreater(len(pytest_args), 0)
        self.assertListEqual([self.root_tmp], pytest_args)
        watch_callee.assert_called_once()

        fetched_directories = watch_callee.call_args[1]["directories"]
        self.assertListEqual([self.root_tmp], fetched_directories)

    def test_single_directory_single_pytest_args(self, watch_callee):
        vargs = [self.root_tmp, "--", "--pdb"]
        main(vargs)

        self.assertIn("pytest_args", watch_callee.call_args[1])
        self.assertIn("directories", watch_callee.call_args[1])

        fetched_pytest_args = watch_callee.call_args[1]["pytest_args"]
        fetched_directories = watch_callee.call_args[1]["directories"]

        self.assertListEqual([vargs[0]], fetched_directories)

        pytest_args = watch_callee.call_args[1]["pytest_args"]
        self.assertGreater(len(pytest_args), 0)
        self.assertListEqual([self.root_tmp, "--pdb"], pytest_args)
        watch_callee.assert_called_once()

        self.assertListEqual([self.root_tmp], fetched_directories)

    def test_single_directory_multiple_pytest_args(self, watch_callee):
        vargs = [self.root_tmp, "--", "--pdb", "--cov=."]
        main(vargs)

        self.assertIn("pytest_args", watch_callee.call_args[1])
        self.assertIn("directories", watch_callee.call_args[1])

        fetched_pytest_args = watch_callee.call_args[1]["pytest_args"]
        fetched_directories = watch_callee.call_args[1]["directories"]

        self.assertListEqual([vargs[0]], fetched_directories)

        pytest_args = watch_callee.call_args[1]["pytest_args"]
        self.assertGreater(len(pytest_args), 0)
        self.assertListEqual([self.root_tmp, "--pdb", "--cov=."], pytest_args)
        watch_callee.assert_called_once()

        self.assertListEqual([self.root_tmp], fetched_directories)


class TestDirectoriesArguments(unittest.TestCase):

    def setUp(self):
        self.root_tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root_tmp)

    @patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
    def test_default_directories(self, watch_callee):
        directories = []

        main(directories)

        self.assertIn("directories", watch_callee.call_args[1])
        fetched_directories = watch_callee.call_args[1]["directories"]
        self.assertListEqual(directories, fetched_directories)
        watch_callee.assert_called_once()

    def test_single_directory(self):
        directories = [self.root_tmp]
        self._assert_directories(directories)

    def test_two_directory_values(self):
        directories = [tempfile.mkdtemp(dir=self.root_tmp) for _ in range(2)]
        self._assert_directories(directories)

    def test_hundred_directory_values(self):
        directories = [tempfile.mkdtemp(dir=self.root_tmp) for _ in range(10)]
        self._assert_directories(directories)

    @patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
    def _assert_directories(self, directories, watch_callee=None):
        self.assertGreater(len(directories), 0, "Testing multiple directories")

        main(directories)

        self.assertIn("directories", watch_callee.call_args[1])

        fetched_directories = watch_callee.call_args[1]["directories"]
        self.assertEqual(len(directories), len(fetched_directories))

        self.assertListEqual(directories, fetched_directories)
        watch_callee.assert_called_once()
