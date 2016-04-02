pytest-watch -- Continuous pytest runner
========================================

[![Current version on PyPI](http://img.shields.io/pypi/v/pytest-watch.svg)][pypi]
[![Downloads/month on PyPI](http://img.shields.io/pypi/dm/pytest-watch.svg)][pypi]

**pytest-watch** a zero-config CLI tool that runs [pytest][], and re-runs it
when a file in your project changes. It beeps on failures and can run arbitrary
commands on each passing and failing test run.


Motivation
----------

Whether or not you use the test-driven development method, running tests
continuously is far more productive than waiting until you're finished
programming to test your code. Additionally, manually running `py.test` each
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

*Note: It can also be run using its full name `py.test.watch`.*

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
the exit code of `py.test` as an argument.

```bash
$ ptw --afterrun cleanup_db.py
```

You can also use a custom runner script for full `py.test` control:

```bash
$ ptw --runner "python custom_pytest_runner.py"
```

Here's an minimal runner script that runs `py.test` and prints its exit code:

```py
# custom_pytest_runner.py

import sys
import pytest

print('py.test exited with code:', pytest.main(sys.argv[1:]))
```

Need to exclude directories from being observed or collected for tests?

```bash
$ ptw --ignore ./deep-directory --ignore ./integration_tests
```

For more information and for the full list of options, run:

```bash
$ ptw --help
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
  drops the colors outputted by py.test, whereas pytest-watch doesn't.
- [Nosey][] is the original codebase this was forked from. Nosey runs [nose][]
  instead of pytest.


Contributing
------------

1. Check the open issues or open a new issue to start a discussion around
   your feature idea or the bug you found
2. Fork the repository, make your changes, and add yourself to [Authors.md][]
3. Send a pull request

If your PR has been waiting a while, feel free to [ping me on Twitter][twitter].

Use this software often? Please consider supporting me on
<a href="http://gratipay.com/joeyespo" title="Thank you!">
  <img align="center" style="margin-bottom:1px" src="http://joeyespo.com/images/gratipay-button.png" alt="Gratipay">
</a>


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
