import sys
import unittest
import shutil
import tempfile

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pytest_watch.command import main
from pytest_watch.constants import ALL_EXTENSIONS


@patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
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

    def test_default_parameters(self, watch_callee):
        main([])

        watch_callee.assert_called_once()
        watch_callee.assert_called_once_with(**self._get_default_args())

    def test_empty_argv(self, watch_callee):
        sys.argv[1:] = []

        main()

        watch_callee.assert_called_once()
        watch_callee.assert_called_once_with(**self._get_default_args())


@patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
class TestPdbArgument(unittest.TestCase):

    def test_default_pdb_argument(self, watch_callee):
        sys.argv[1:] = []

        main()

        self.assertFalse(watch_callee.call_args[1]["wait"])

        self.assertNotIn("pdb", watch_callee.call_args[1])

        self.assertNotIn("--pdb",
                         watch_callee.call_args[1]["pytest_args"])

    def test_pdb_argument(self, watch_callee):
        main(["--pdb"])

        self.assertTrue(watch_callee.call_args[1]["wait"])

        self.assertNotIn("pdb", watch_callee.call_args[1])

        self.assertIn("--pdb",
                         watch_callee.call_args[1]["pytest_args"])

    def test_pdb_and_wait_arguments(self, watch_callee):
        main("--pdb --wait".split())

        self.assertTrue(watch_callee.call_args[1]["wait"])

        self.assertNotIn("pdb", watch_callee.call_args[1])

        self.assertIn("--pdb",
                         watch_callee.call_args[1]["pytest_args"])

    def test_pdb_off_and_wait_on_arguments(self, watch_callee):
        main("--wait".split())

        self.assertTrue(watch_callee.call_args[1]["wait"])

        self.assertNotIn("pdb", watch_callee.call_args[1])

        self.assertNotIn("--pdb",
                         watch_callee.call_args[1]["pytest_args"])


@patch("pytest_watch.command.merge_config", side_effect=lambda *args, **kwargs: True)
@patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
class TestConfigArgument(unittest.TestCase):
    def test_default_config(self, watch_callee, merge_config_callee):
        sys.argv[1:] = []

        main()

        self.assertNotIn("config", watch_callee.call_args[1])
        self.assertNotIn("-c", watch_callee.call_args[1]["pytest_args"])

    def test_config_argument(self, watch_callee, merge_config_callee):
        self._assert_config_file(watch_callee, "pytest.ini")
        watch_callee.reset_mock()
        self._assert_config_file(watch_callee, "custom_config_file.txt")

    def _assert_config_file(self, watch_callee, filename):
        main(["--config", filename])

        self.assertNotIn("config", watch_callee.call_args[1])

        pytest_args = watch_callee.call_args[1]["pytest_args"]
        self.assertIn("-c", pytest_args)
        self.assertEqual(filename, pytest_args[pytest_args.index("-c")+1])


@patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
class TestIgnoreArgument(unittest.TestCase):

    def setUp(self):
        self.root_tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root_tmp)

    def test_default_ignore_argument(self, watch_callee):
        sys.argv[1:] = []

        main()

        self.assertListEqual([], watch_callee.call_args[1]["ignore"])

        self.assertNotIn("--ignore",
                         watch_callee.call_args[1]["pytest_args"])

    def test_ignore_argument(self, watch_callee):
        main(["--ignore", "pytest_watch"])

        self.assertEqual(["pytest_watch"],
                         watch_callee.call_args[1]["ignore"])

        self.assertIn("--ignore",
                         watch_callee.call_args[1]["pytest_args"])

    def test_multiple_ignore_argument(self, watch_callee):
        directories = []
        argv = []

        for _ in range(2):
            new_dir = tempfile.mkdtemp(dir=self.root_tmp)
            argv.append("--ignore")
            argv.append(new_dir)
            directories.append(new_dir)

        main(argv)

        self.assertEqual(directories,
                         watch_callee.call_args[1]["ignore"])

        pytest_args = watch_callee.call_args[1]["pytest_args"]
        self.assertIn("--ignore", pytest_args)
        ignore_idx = pytest_args.index("--ignore")
        self.assertListEqual(argv, pytest_args)

    def test_multiple_ignore_argument_conflict(self, watch_callee):
        directories = []
        argv = []

        for _ in range(2):
            new_dir = tempfile.mkdtemp(dir=self.root_tmp)
            argv.append("--ignore")
            argv.append(new_dir)
            directories.append(new_dir)

        argv.append("--")
        argv.append("--ignore")
        argv.append(tempfile.mkdtemp(dir=self.root_tmp))

        main(argv)

        self.assertEqual(directories,
                         watch_callee.call_args[1]["ignore"])

        pytest_args = watch_callee.call_args[1]["pytest_args"]
        self.assertIn("--ignore", pytest_args)
        self.assertEqual(3, pytest_args.count("--ignore"))


@patch("pytest_watch.command.watch", side_effect=lambda *args, **kwargs: 0)
class TestSpoolArguments(unittest.TestCase):

    def test_zero_spool_value(self, watch_callee):
        main("--spool 0".split())
        self.assertIn("spool", watch_callee.call_args[1])
        self.assertEqual(0, watch_callee.call_args[1]["spool"])
        watch_callee.assert_called_once()

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

    def test_default_spool_value(self, watch_callee):
        main([])

        self.assertIn("spool", watch_callee.call_args[1])
        self.assertEqual(200, watch_callee.call_args[1]["spool"])
        watch_callee.assert_called_once()

    def test_cause_error_for_negative_spool_values(self, watch_callee):
        self.assertEqual(2, main("--spool -1".split()))
        watch_callee.assert_not_called()

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

    def test_all_extensions(self, watch_callee):
        main("--ext *".split())

        self.assertEqual(object, type(watch_callee.call_args[1]["extensions"]))
        self.assertIsNotNone(watch_callee.call_args[1]["extensions"])
        self.assertEqual(ALL_EXTENSIONS, watch_callee.call_args[1]["extensions"])
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
