import os
import shutil
import tempfile
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pytest_watch.watcher import _split_recursive, run_hook, watch


class TestDirectoriesFiltering(unittest.TestCase):

    def setUp(self):
        self.root_dir = tempfile.mkdtemp()

    def tearDown(self):
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

        assert ([included_folder], [self.root_dir]) == \
                _split_recursive(dirs, ignore), \
                "Ignoring {1}, the following behavior is expected:\n"\
                ". {0} should be loaded non-recursivelly;\n"\
                ". {1} and its children will be excluded;\n"\
                ". only {2} will be loaded recursivelly.\n"\
                .format(self.root_dir, excluded_folder, included_folder)

    @unittest.skip("Depends on pytest_watch.watcher._split_recursive support"\
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

        assert ([self.root_dir], [tree_folder]) == \
                _split_recursive(dirs, ignore)

    @unittest.skip("Depends on pytest_watch.watcher._split_recursive support"\
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

        assert ([self.root_dir], [tree_folder]) == \
                _split_recursive(dirs, ignore)


