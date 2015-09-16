pytest-watch Changelog
======================


Version 3.3.0 (2015-09-16)
--------------------------

- Enhancement: Add `--beforerun` CLI argument ([#25](https://github.com/joeyespo/pytest-watch/pull/25) - thanks, [@blueyed][]!)


Version 3.2.0 (2015-06-28)
--------------------------

- Enhancement: Add `pytest-watch` to console scripts to match the name.
- Bugfix: Use `shell=True` only for MS Windows when executing `py.test` ([#18](https://github.com/joeyespo/pytest-watch/pull/18) - thanks, [@blueyed][]!)
- Bugfix: Use the default fg for `STYLE_NORMAL` ([#19](https://github.com/joeyespo/pytest-watch/pull/19) - thanks, [@blueyed][]!)


Version 3.1.0 (2015-06-20)
--------------------------

- Enhancement: Add ability to run with `python -m pytest_watch`.
- Bugfix: Revert using `pytest` directly (abfd40209a124e1555e94dcf03eeb8644465ea62) until it can handle running multiple times ([#15](https://github.com/joeyespo/pytest-watch/issues/15))


Version 3.0.0 (2015-06-14)
--------------------------

- Enhancement: Add `--poll` to work with remote file systems ([#11](https://github.com/joeyespo/pytest-watch/pull/11) - thanks, [@aldanor][]!)
- Enhancement: Add ability to have multiple watch directories ([#11](https://github.com/joeyespo/pytest-watch/pull/11) - thanks, [@aldanor][]!)
- Enhancement: Show pytest command being run ([#11](https://github.com/joeyespo/pytest-watch/pull/11) - thanks, [@aldanor][]!)
- Enhancement: Show command and filenames in color ([#11](https://github.com/joeyespo/pytest-watch/pull/11) - thanks, [@aldanor][]!)
- Enhancement: Add `--ignore` to ignore directories from being watched (initial attempt) ([#11](https://github.com/joeyespo/pytest-watch/pull/11) - thanks, [@aldanor][]!)
- Enhancement: Add ability to forward arguments to pytest with `--` ([#11](https://github.com/joeyespo/pytest-watch/pull/11) - thanks, [@aldanor][]!)
- Enhancement: Add spooling for the case where multiple watch events are triggered simultaneously ([#11](https://github.com/joeyespo/pytest-watch/pull/11) - thanks, [@aldanor][]!)
- Enhancement: Add `--verbose` and `--quiet` for controlling the verbosity ([#11](https://github.com/joeyespo/pytest-watch/pull/11) - thanks, [@aldanor][]!)
- Bugfix: Exit gracefully when `KeyboardInterrupt` occurs after the first test run ([#10](https://github.com/joeyespo/pytest-watch/pull/10) - thanks, [@carsongee][]!)


Version 2.0.0 (2015-02-06)
--------------------------

- Enhancement: Show the detected change, unless `--clear` is given.
- Enhancement: Beep by default, unless `--nobeep` is given.
- Enhancement: Add `--ext` to override the list of extensions that trigger re-runs.
- Bugfix: Unpin requirements
- Cleanup


Version 1.0.0 (2015-02-06)
--------------------------

- Enhancement: Add ability to run commands on each pass or fail - ([#4](https://github.com/joeyespo/pytest-watch/pull/4) - thanks, [@rakjin][]!)
- Bugfix: Error when no directory is provided on OSX ([#3](https://github.com/joeyespo/pytest-watch/pull/3) - thanks, [@rakjin][]!)
- Use MIT license


Version 0.1.1 (2015-01-16)
--------------------------

- Bugfix: `clear` command typo ([#1](https://github.com/joeyespo/pytest-watch/pull/1) - thanks, [@casio][]!)


Version 0.1.0 (2015-01-11)
--------------------------

First public preview release.


[@casio]: https://github.com/casio
[@rakjin]: https://github.com/rakjin
[@carsongee]: https://github.com/carsongee
[@aldanor]: https://github.com/aldanor
[@blueyed]: https://github.com/blueyed
