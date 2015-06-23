pytest-watch -- Continuous pytest runner
========================================

[![Downloads/month on PyPI](http://img.shields.io/pypi/dm/pytest-watch.svg)][pypi]
[![Current version on PyPI](http://img.shields.io/pypi/v/pytest-watch.svg)][pypi]

**pytest-watch** a zero-config CLI tool that runs [pytest][], and reruns it
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

  using [GrowlNotify][]

- **Windows**

  `> ptw --onfail flash` using [Console Flash][]


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
2. Fork the repository
3. Send a pull request

Use this software often? Please consider supporting me on
<a href="http://gratipay.com/joeyespo" title="Thank you!">
  <img align="center" style="margin-bottom:1px" src="http://joeyespo.com/images/gratipay-button.png" alt="Gratipay">
</a>


[pypi]: http://pypi.python.org/pypi/pytest-watch/
[pytest]: http://pytest.org/
[watchdog]: http://packages.python.org/watchdog
[growlnotify]: http://growl.info/downloads#generaldownloads
[console flash]: http://github.com/joeyespo/console-flash
[xdist]: http://pypi.python.org/pypi/pytest-xdist
[nosey]: http://github.com/joeyespo/nosey
[nose]: http://nose.readthedocs.org/en/latest/
