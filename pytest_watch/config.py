from __future__ import print_function

import sys

import pytest

from .util import silence

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


CLI_OPTION_PREFIX = '--'


class CollectConfig(object):
    """
    A pytest plugin to gets the configuration file.
    """
    def __init__(self):
        self.path = None

    def pytest_cmdline_main(self, config):
        if hasattr(config, 'inifile'):
            # pytest >= 2.7.0
            inifile = config.inifile
        else:
            # pytest < 2.7.0
            inifile = config.inicfg.config.path
        if inifile:
            self.path = str(inifile)


def collect(pytest_args, silent=True):
    collect_config = CollectConfig()
    argv = pytest_args + ['--collect-only']

    if silent:
        try:
            with silence():
                exit_code = pytest.main(argv, plugins=[collect_config])
                if exit_code == 0:
                    return collect_config.path
        except Exception:
            pass
        # Print message and run again without silencing
        print('Error: Could not run --collect-only to find the pytest config '
              'file. Trying again without silencing stdout...',
              file=sys.stderr)

    status_code = pytest.main(argv, plugins=[collect_config])
    if not collect_config.path and status_code != 0:
        print('Could not determine the pytest config file.', file=sys.stderr)
    return collect_config.path


def merge_config(args, pytest_args, silent=True):
    config_path = collect(pytest_args, silent)

    if not config_path:
        return

    config = ConfigParser()
    config.read(config_path)
    if not config.has_section('pytest-watch'):
        return

    for cli_name in args:
        if not cli_name.startswith(CLI_OPTION_PREFIX):
            continue
        config_name = cli_name[len(CLI_OPTION_PREFIX):]

        # Let CLI options take precedence
        if args[cli_name]:
            continue

        # Find config option
        if not config.has_option('pytest-watch', config_name):
            continue

        # Merge config option using the expected type
        if isinstance(args[cli_name], list):
            args[cli_name].append(config.get('pytest-watch', config_name))
        elif isinstance(args[cli_name], bool):
            args[cli_name] = config.getboolean('pytest-watch', config_name)
        else:
            args[cli_name] = config.get('pytest-watch', config_name)
