import errno
import os
import shutil
import sys
import tempfile
from unittest import skip

try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from pytest_watch.watcher import _split_recursive, run_hook, watch,\
     _get_pytest_runner


class TestDirectoriesFiltering():

    def setup_method(self):
        self.root_dir = tempfile.mkdtemp()

    def teardown_method(self):
        try:
            shutil.rmtree(self.root_dir)
        except:
            pass

    def test_empty_split_recursive(self):
        dirs = []
        ignore = []
        assert (dirs, ignore) == _split_recursive(dirs, ignore)

    def test_non_empty_directories_empty_ignore(self):
        dirs = ["."]
        ignore = []

        assert (dirs, ignore) == _split_recursive(dirs, ignore)

    def test_invalid_directories(self):
        dirs = [self.root_dir]

        fake_dir = os.path.join(self.root_dir, "atrocadocapacausti")

        with pytest.raises(OSError) as err:
            watch(directories=[fake_dir])
        assert errno.ENOENT == err.value.errno

    def test_ignore_all_subdirs(self):
        dirs = [self.root_dir]

        a_folder = tempfile.mkdtemp(dir=self.root_dir)
        b_folder = tempfile.mkdtemp(dir=self.root_dir)

        ignore = [a_folder, b_folder]

        assert ([], [self.root_dir]) == _split_recursive(dirs, ignore)

    def test_ignore_subdirs_partially(self):
        """
        This test runs over the following tree structure:
            self.root_dir
            |_included_folder
            |_excluded_folder

        Ignoring <excluded_folder>, the following behavior is expected:
        . <self.root_dir> should be loaded non-recursivelly;
        . <excluded_folder> and its children will be excluded;
        . only <included_folder> will be loaded recursivelly.
        """
        dirs = [self.root_dir]

        included_folder = tempfile.mkdtemp(dir=self.root_dir)
        excluded_folder = tempfile.mkdtemp(dir=self.root_dir)

        ignore = [excluded_folder]

        fail_err = str("Ignoring {1}, the following behavior is expected:\n"
                       ". {0} should be loaded non-recursivelly;\n"
                       ". {1} and its children will be excluded;\n"
                       ". only {2} will be loaded recursivelly.\n")
        fail_msg = fail_err.format(self.root_dir, excluded_folder,
                                   included_folder)

        result = _split_recursive(dirs, ignore)
        assert ([included_folder], [self.root_dir]) == result, fail_msg

    @skip("Depends on pytest_watch.watcher._split_recursive support"
                   " for deep recursive navigation through directory tree")
    def test_ignore_deep_subtree_multichild(self):
        """
        This test runs over the following tree structure:
            self.root_dir
            |_tree_folder
            ..|_subtree_folder_a
            ....|_sub_subtree_folder
            ..|_subtree_folder
            ....|_sub_subtree_folder

        Ignoring <subtree_folder>, the following behavior is expected:
        . <tree_folder> should be loaded non-recursivelly;
        . <subtree_folder> and its children will be excluded;
        . only <self.root_dir> will be loaded recursivelly.
        """
        dirs = [self.root_dir]

        tree_folder = tempfile.mkdtemp(dir=self.root_dir)
        subtree_folder_a = tempfile.mkdtemp(dir=tree_folder)
        subtree_folder = tempfile.mkdtemp(dir=tree_folder)
        sub_subtree_folder = tempfile.mkdtemp(dir=tree_folder)

        ignore = [subtree_folder]

        assert ([self.root_dir], [tree_folder]) == _split_recursive(dirs,
                                                                    ignore)

    @skip("Depends on pytest_watch.watcher._split_recursive support"
                   " for deep recursive navigation through directory tree")
    def test_ignore_deep_subtree_single(self):
        """
        This test runs over the following tree structure:
            self.root_dir
            |_tree_folder
            ..|_subtree_folder
            ....|_sub_subtree_folder

        Ignoring <subtree_folder>, the following behavior is expected:
        . <tree_folder> should be loaded non-recursivelly;
        . <subtree_folder> and its children will be excluded;
        . only <self.root_dir> will be loaded recursivelly.
        """
        dirs = [self.root_dir]

        tree_folder = tempfile.mkdtemp(dir=self.root_dir)
        subtree_folder = tempfile.mkdtemp(dir=tree_folder)
        sub_subtree_folder = tempfile.mkdtemp(dir=tree_folder)

        ignore = [subtree_folder]

        assert ([self.root_dir], [tree_folder]) == _split_recursive(dirs,
                                                                    ignore)


class TestPytestRunner():
    DEFAULT_EXECUTABLE = [sys.executable, "-m", "pytest"]

    def setup_method(self):
        self.virtual_env = os.getenv("VIRTUAL_ENV")
        if "VIRTUAL_ENV" in os.environ:
            del os.environ['VIRTUAL_ENV']

    def teardown_method(self):
        if self.virtual_env:
            os.putenv("VIRTUAL_ENV", self.virtual_env)

    def test_default_sys_executable(self):
        assert TestPytestRunner.DEFAULT_EXECUTABLE == _get_pytest_runner()

    def test_empty_string_returns_sys_executable(self):
        assert TestPytestRunner.DEFAULT_EXECUTABLE == _get_pytest_runner("")
        assert TestPytestRunner.DEFAULT_EXECUTABLE == _get_pytest_runner(" ")
        assert TestPytestRunner.DEFAULT_EXECUTABLE == _get_pytest_runner(" "*8)

    def test_custom_sys_executable(self):
        assert ["mypytest"] == _get_pytest_runner("mypytest")
        assert ["mpytest", "runtest"] == _get_pytest_runner("mpytest runtest")

    def test_virtualenv_executable(self):
        os.environ["VIRTUAL_ENV"] = "/tmp/venv"

        assert ["py.test"] == _get_pytest_runner()

        del os.environ["VIRTUAL_ENV"]

        assert TestPytestRunner.DEFAULT_EXECUTABLE == _get_pytest_runner()
