import unittest


from pytest_watch.watcher import _split_recursive


class TestSplitRecursive(unittest.TestCase):

    def test_empty_split_recursive(self):
        dirs = []
        ignore = []
        assert (dirs, ignore) == _split_recursive(dirs, ignore)
