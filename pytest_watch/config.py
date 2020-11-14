from __future__ import print_function

import sys

import pytest

from .util import silence

import toml

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

from .constants import EXIT_INTERRUPTED, EXIT_NOTESTSCOLLECTED, EXIT_OK


CLI_OPTION_PREFIX = '--'


class CollectError(Exception):
    pass


class StopCollect(Exception):
    pass


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
            raise StopCollect()


def _run_pytest_collect(pytest_args):
    collect_config_plugin = CollectConfig()
    argv = pytest_args + ['--collect-only']

    try:
        exit_code = pytest.main(argv, plugins=[collect_config_plugin])
    except StopCollect:
        return collect_config_plugin.path

    if exit_code == EXIT_INTERRUPTED:
        # pytest raises EXIT_INTERRUPTED on *both* keyboard error and parse errors
        raise KeyboardInterrupt()
    if exit_code not in [EXIT_OK, EXIT_NOTESTSCOLLECTED]:
        raise CollectError()

    return collect_config_plugin.path


def _collect_config(pytest_args, silent=True):
    if silent:
        try:
            with silence():
                return _run_pytest_collect(pytest_args)
        except (KeyboardInterrupt, Exception, SystemExit):
            pass

        # Print message and run again without silencing
        print('Error: Could not run --collect-only to handle the pytest '
              'config file. Trying again without silencing output...',
              file=sys.stderr)

    # Collect without silencing
    return _run_pytest_collect(pytest_args)


def _parse_toml_config(path):
    config = toml.load(path).get('tool', {}).get('pytest-watch', {})
    stringify = lambda v: ','.join(v) if isinstance(v, list) else str(v)
    return {k: stringify(v) for k, v in config.items()}


def _parse_ini_config(path):
    config = ConfigParser()
    config.read(path)
    if config.has_section('pytest-watch'):
        return dict(config.items('pytest-watch'))
    return {}


def merge_config(args, pytest_args, silent=True, verbose=False):
    if verbose:
        print('Locating inifile...')

    try:
        config_path = _collect_config(pytest_args, silent)
    except (KeyboardInterrupt, CollectError):
        return False

    if not config_path:
        return True

    if config_path.endswith('.toml'):
        config = _parse_toml_config(config_path)
    elif config_path.endswith('.ini'):
        config = _parse_ini_config(config_path)
    else:
        config = {}

    if not config:
        return True

    for cli_name in args:
        if not cli_name.startswith(CLI_OPTION_PREFIX):
            continue
        config_name = cli_name[len(CLI_OPTION_PREFIX):]

        # Let CLI options take precedence
        if args[cli_name]:
            continue

        # Find config option
        if not config_name in config:
            continue

        # Merge config option using the expected type
        if isinstance(args[cli_name], list):
            args[cli_name].append(config.get(config_name))
        elif isinstance(args[cli_name], bool):
            args[cli_name] = config.get(config_name).lower() != 'false'
        else:
            args[cli_name] = config.get(config_name)

    return True
