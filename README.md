pytest-watch -- Continuous pytest runner
========================================

**pytest-watch** a zero-config CLI tool that runs [pytest][], and reruns it
when a file in your project changes.


Motivation
----------

Whether or not you use the test-driven development method, running tests
continuously is far more productive than waiting until you're finished
programming to test your code. Additionally, manually running `py.test` each
time you want to see if any tests were broken has more wait-time and cognitive
overhead than merely checking the terminal here and there. This could be a
crucial difference when debugging a complex problem or on a tight deadline.


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

It can also be run using the longhand, `py.test.watch`.

Now develop normally and check the terminal every now and then to see if any
tests are broken.


Alternatives
------------

- [xdist][] offers the `--looponfail` (`-f`) option (and distributed testing
  options). This instead re-runs only those tests which have failed until you
  make them pass. This can be a speed advantage when trying to get all tests
  passing, but leave out the discovery of new failures until they do. It also
  drops the colors outputted by py.test, whereas pytest-watch doesn't.
- [Nosey][] is the original codebase this was forked from. Nosey runs [nose][]
  instead of pytest.


Contributing
------------

1. Check the open issues or open a new issue to start a discussion around
   your feature idea or the bug you found
2. Fork the repository
3. Send a pull request


[pytest]: http://pytest.org/
[watchdog]: http://packages.python.org/watchdog
[xdist]: http://pypi.python.org/pypi/pytest-xdist
[nosey]: http://github.com/joeyespo/nosey
[nose]: http://nose.readthedocs.org/en/latest/
