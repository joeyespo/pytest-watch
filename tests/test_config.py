import pytest
from pytest_watch.config import CollectConfig, merge_config
from pytest_watch.util import silence

import os
import tempfile
import shutil

def create_temp_case(case_name):
    path_test_cases = os.path.abspath("test_cases/")
    path_case = os.path.join(path_test_cases, case_name)
    
    path_tmpdir = tempfile.mkdtemp()
    path_tmpdir_case = os.path.join(path_tmpdir, case_name)
    shutil.copytree(path_case, path_tmpdir_case) 
    
    return path_tmpdir_case


def test_path_collected_1():
    ''' Check pytest.ini location is correct'''
    # always reset pwd to cur directory
    os.chdir(os.path.dirname(__file__))
    path_case = create_temp_case("case_1")
    os.chdir(path_case)

    collect_config = CollectConfig()
    with silence():
        pytest.main(['--collect-only'], plugins=[collect_config])

    path_pytest_ini = os.path.join(path_case, "pytest.ini")
    assert(str(collect_config.path) == path_pytest_ini)


def test_path_collected_2():
    ''' Check pytest.ini location is correct, also from a inner directory'''
    os.chdir(os.path.dirname(__file__))
    path_case = create_temp_case("case_1")
    path_case_inner = os.path.join(path_case, "dir_1")
    os.chdir(path_case_inner)

    collect_config = CollectConfig()
    with silence():
        pytest.main(['--collect-only'], plugins=[collect_config])

    path_pytest_ini = os.path.join(path_case, "pytest.ini")
    assert(str(collect_config.path) == path_pytest_ini)


def test_merge_config_basic():
    ''' Check ini config works alone'''
    os.chdir(os.path.dirname(__file__))
    path_case = create_temp_case("case_1")
    os.chdir(path_case)

    args = {"--verbose":False,
            "--help" : False,
            "--ignore" : None}
    merge_config(args)
    
    assert(args["--verbose"] is True)
    assert(args["--help"] is False)
    assert(args["--ignore"] is None)




    
