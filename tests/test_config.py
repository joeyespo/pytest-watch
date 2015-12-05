import pytest
from pytest_watch.config import CollectConfig, merge_config
from pytest_watch.util import silence

import os
import tempfile
import shutil


class patched_chdir(object):

    """Just like chdir, but can be used in with - sets back the old path at exit"""

    def __init__(self, new_path):
        self.old_path = os.getcwd()
        self.new_path = new_path

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, type, value, traceback):
        os.chdir(self.old_path)


def create_temp_case(case_name):
    with patched_chdir(os.path.dirname(__file__)):
        path_test_cases = os.path.abspath("test_cases/")
        path_case = os.path.join(path_test_cases, case_name)

        path_tmpdir = tempfile.mkdtemp()
        path_tmpdir_case = os.path.join(path_tmpdir, case_name)
        shutil.copytree(path_case, path_tmpdir_case)

    return path_tmpdir_case


def test_path_collected_1():
    ''' Check pytest.ini location is correct'''
    # always reset pwd to cur directory
    path_case = create_temp_case("case_1")
    os.chdir(path_case)

    collect_config = CollectConfig()
    with silence():
        pytest.main(['--collect-only'], plugins=[collect_config])

    path_pytest_ini = os.path.join(path_case, "pytest.ini")
    assert(str(collect_config.path) == path_pytest_ini)


def test_path_collected_2():
    ''' Check pytest.ini location is correct, also from a inner directory'''
    path_case = create_temp_case("case_1")
    path_case_inner = os.path.join(path_case, "dir_1")
    os.chdir(path_case_inner)

    collect_config = CollectConfig()
    with silence():
        pytest.main(['--collect-only'], plugins=[collect_config])

    path_pytest_ini = os.path.join(path_case, "pytest.ini")
    assert(str(collect_config.path) == path_pytest_ini)


class Test_merge_config(object):

    """All tests for func merge_config"""

    def test_works_alone(self):
        '''
        Check ini config works alone.
        Set pytest.ini:
            [pytest-watch]
            verbose = True
        '''
        os.chdir(os.path.dirname(__file__))
        path_case = create_temp_case("case_1")
        os.chdir(path_case)

        args = {"--verbose": False,
                "--help": False,
                "--ignore": None}
        merge_config(args)

        assert(args["--verbose"] is True)
        assert(args["--help"] is False)
        assert(args["--ignore"] is None)

    def test_works_with_cmdline(self):
        '''
        Check ini config works alongwith cmdline args.
        Set pytest.ini:
            [pytest-watch]
            verbose = True
        '''
        path_case = create_temp_case("case_1")
        os.chdir(path_case)

        args = {"--verbose": False,
                "--help": False,
                "--ignore": "dir_a"}
        merge_config(args)

        assert(args["--verbose"] is True)
        assert(args["--help"] is False)
        assert(args["--ignore"] is "dir_a")

    def test_works_with_cmdline_precedence(self):
        '''
        Check ini config works alongwith cmdline args, \
        with cmdline precedence
        Set pytest.ini:
            [pytest-watch]
            version = False
            ignore = dir_b
            help = True
        '''
        path_case = create_temp_case("case_2")
        os.chdir(path_case)

        args = {"--verbose": True,
                "--help": False,
                "--ignore": "dir_a"}
        merge_config(args)

        assert(args["--verbose"] is True)
        assert(args["--help"] is True)
        assert(args["--ignore"] is "dir_a")

    def test_works_wo_ini(self):
        '''
        Check ini config works correctly with only cmdline \
        args, without any pytest.ini.
        No pytest.ini present
        '''
        path_case = create_temp_case("case_3")
        os.chdir(path_case)

        args = {"--verbose": True,
                "--help": False,
                "--onpass": None,
                "--ignore": "dir_a"}
        merge_config(args)

        assert(args["--verbose"] is True)
        assert(args["--help"] is False)
        assert(args["--onpass"] is None)
        assert(args["--ignore"] is "dir_a")

    def test_works_wo_pytest_watch_section(self):
        '''
        Check ini config works correctly with only cmdline \
        args, without any [pytest-watch] section in pytest.ini.
        Also, shouldnt read pytest settings by mistake.
        Set pytest.ini:
            [pytest]
            verbose = True
        '''
        path_case = create_temp_case("case_4")
        os.chdir(path_case)

        args = {"--verbose": False,
                "--help": True,
                "--onpass": None,
                "--ignore": "dir_a"}
        merge_config(args)

        assert(args["--verbose"] is False)
        assert(args["--help"] is True)
        assert(args["--onpass"] is None)
        assert(args["--ignore"] is "dir_a")

    @pytest.mark.xfail
    def test_works_directories_ini_option(self):
        '''
        Currently, "directories" or "<directories>" argument \
        in pytest.ini is not respected. So, it is marked to xfail.

        When it'll pass, "directories" option should be added to \
        more test cases.
        Set pytest.ini:
            [pytest-watch]
            directories = dir_c,dir_d
            <directories> = dir_c,dir_d
        '''
        path_case = create_temp_case("case_5")
        os.chdir(path_case)

        args = {"--verbose": False,
                "--help": True,
                "--onpass": None,
                "<directories>": "dir_a,dir_b"}
        merge_config(args)

        # main condition
        assert(args["<directories>"] is ["dir_c", "dir_d"])
        # auxiliary conditions
        assert(args["--verbose"] is False)
        assert(args["--help"] is True)
        assert(args["--onpass"] is None)
