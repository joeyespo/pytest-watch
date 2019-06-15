pytest-watch -- Continuous pytest runner
========================================

[![Current version on PyPI](http://img.shields.io/pypi/v/pytest-watch.svg)][pypi]
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/joeyespo)

**pytest-watch** a zero-config CLI tool that runs [pytest][], and re-runs it
when a file in your project changes. It beeps on failures and can run arbitrary
commands on each passing and failing test run.


Motivation
----------

Whether or not you use the test-driven development method, running tests
continuously is far more productive than waiting until you're finished
programming to test your code. Additionally, manually running `pytest` each
time you want to see if any tests were broken has more wait-time and cognitive
overhead than merely listening for a notification. This could be a crucial
difference when debugging a complex problem or on a tight deadline.


Installation
------------

```bash
$ pip install pytest-watch
```


Usage
-----

```bash
$ cd myproject
$ ptw
 * Watching /path/to/myproject
```

*Note: It can also be run using its full name `pytest-watch`.*

Now develop normally and check the terminal every now and then to see if any
tests are broken. Alternatively, pytest-watch can **notify you** when tests
pass or fail:

- **OSX**

  `$ ptw --onpass "say passed" --onfail "say failed"`

  ```bash
  $ ptw --onpass "growlnotify -m \"All tests passed!\"" \
        --onfail "growlnotify -m \"Tests failed\""
  ```

  using [GrowlNotify][].

- **Windows**

  ```bat
  > ptw --onfail flash
  ```

  using [Console Flash][]

You can also run a command before the tests run, e.g. seeding your test database:

```bash
$ ptw --beforerun init_db.py
```

Or after they finish, e.g. deleting a sqlite file. Note that this script receives
the exit code of `pytest` as an argument.

```bash
$ ptw --afterrun cleanup_db.py
```

You can also use a custom runner script for full `pytest` control:

```bash
$ ptw --runner "python custom_pytest_runner.py"
```

Here's an minimal runner script that runs `pytest` and prints its exit code:

```py
# custom_pytest_runner.py

import sys
import pytest

print('pytest exited with code:', pytest.main(sys.argv[1:]))
```

Need to exclude directories from being observed or collected for tests?

```bash
$ ptw --ignore ./deep-directory --ignore ./integration_tests
```

See the full list of options:

```
$ ptw --help
Usage: ptw [options] [--ignore <dir>...] [<directory>...] [-- <pytest-args>...]

Options:
  --ignore <dir>        Ignore directory from being watched and during
                        collection (multi-allowed).
  --ext <exts>          Comma-separated list of file extensions that can
                        trigger a new test run when changed (default: .py).
                        Use --ext=* to allow any file (including .pyc).
  --config <file>       Load configuration from `file` instead of trying to
                        locate one of the implicit configuration files.
  -c --clear            Clear the screen before each run.
  -n --nobeep           Do not beep on failure.
  -w --wait             Waits for all tests to complete before re-running.
                        Otherwise, tests are interrupted on filesystem events.
  --beforerun <cmd>     Run arbitrary command before tests are run.
  --afterrun <cmd>      Run arbitrary command on completion or interruption.
                        The exit code of "pytest" is passed as an argument.
  --onpass <cmd>        Run arbitrary command on pass.
  --onfail <cmd>        Run arbitrary command on failure.
  --onexit <cmd>        Run arbitrary command when exiting pytest-watch.
  --runner <cmd>        Run a custom command instead of "pytest".
  --pdb                 Start the interactive Python debugger on errors.
                        This also enables --wait to prevent pdb interruption.
  --spool <delay>       Re-run after a delay (in milliseconds), allowing for
                        more file system events to queue up (default: 200 ms).
  -p --poll             Use polling instead of OS events (useful in VMs).
  -v --verbose          Increase verbosity of the output.
  -q --quiet            Decrease verbosity of the output (precedence over -v).
  -V --version          Print version and exit.
  -h --help             Print help and exit.
```


Configuration
-------------

CLI options can be added to a `[pytest-watch]` section in your
[pytest.ini file][pytest.ini] to persist them in your project. For example:

```ini
# pytest.ini

[pytest]
addopts = --maxfail=2


[pytest-watch]
ignore = ./integration-tests
nobeep = True
```


Alternatives
------------

- [xdist][] offers the `--looponfail` (`-f`) option (and distributed testing
  options). This instead re-runs only those tests which have failed until you
  make them pass. This can be a speed advantage when trying to get all tests
  passing, but leaves out the discovery of new failures until then. It also
  drops the colors outputted by pytest, whereas pytest-watch doesn't.
- [Nosey][] is the original codebase this was forked from. Nosey runs [nose][]
  instead of pytest.


Contributing
------------

1. Check the open issues or open a new issue to start a discussion around
   your feature idea or the bug you found
2. Fork the repository, make your changes, and add yourself to [Authors.md][]
3. Send a pull request

If you want to edit the README, be sure to make your changes to `README.md` and
run the following to regenerate the `README.rst` file:

```bash
$ pandoc -t rst -o README.rst README.md
```

If your PR has been waiting a while, feel free to [ping me on Twitter][twitter].

Use this software often? <a href="https://saythanks.io/to/joeyespo" target="_blank"><img src="https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg" align="center" alt="Say Thanks!"></a>
:smiley:


[pypi]: http://pypi.python.org/pypi/pytest-watch/
[pytest]: http://pytest.org/
[watchdog]: http://packages.python.org/watchdog
[growlnotify]: http://growl.info/downloads#generaldownloads
[console flash]: http://github.com/joeyespo/console-flash
[pytest.ini]: https://pytest.org/latest/customize.html
[xdist]: http://pypi.python.org/pypi/pytest-xdist
[nosey]: http://github.com/joeyespo/nosey
[nose]: http://nose.readthedocs.org/en/latest/
[authors.md]: ./AUTHORS.md
[twitter]: https://twitter.com/joeyespo
