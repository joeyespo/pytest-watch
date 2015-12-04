import pytest

# For collecting path of the ini


class CollectIniPathPlugin(object):

    def pytest_cmdline_main(self, config):
        CollectorIniPath.pytest_ini_path = config.inifile.realpath().strpath


class CollectorIniPath(object):

    """ Object for storing the path from CollectIniPathPlugin """
    pytest_ini_path = None


def get_pytest_ini_path():

    pytest.main("--collect-only", plugins=[CollectIniPathPlugin()])
    return(CollectorIniPath.pytest_ini_path)


def get_ini_option(config_parser, option_name):
    if config_parser.has_option("pytest-watch", option_name):
        return config_parser.get("pytest-watch", option_name)
    else:
        return None


def get_ini_option_boolean(config_parser, option_name):
    if config_parser.has_option("pytest-watch", option_name):
        return config_parser.getboolean("pytest-watch", option_name)
    else:
        return False
