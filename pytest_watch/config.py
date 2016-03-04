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


def merge_config(args, directories):
    collect_config = CollectConfig()
    try:
        with silence():
            pytest.main(directories + ['--collect-only'],
                        plugins=[collect_config])
    except Exception:
        print('There was an error when collecting tests/config:',
              file=sys.stderr)
        raise

    if not collect_config.path:
        return

    config = ConfigParser()
    config.read(collect_config.path)
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
        if isinstance(args[cli_name], bool):
            args[cli_name] = config.getboolean('pytest-watch', config_name)
        else:
            args[cli_name] = config.get('pytest-watch', config_name)
