pytest-watch Changelog
======================


Version 4.2.0 (dev)
-------------------

- Bugfix: Use the same Python interpreter for `pytest` when `ptw` is run outside of an activated virtual environment ([#72](https://github.com/joeyespo/pytest-watch/pull/72) - thanks, [@jacebrowning][]!)


Version 4.1.0 (2016-04-08)
--------------------------

- Enhancement: Speed up config collection
- Bugfix: Handle `KeyboardInterrupt` during inifile collection (fixes [#52](https://github.com/joeyespo/pytest-watch/issues/52))
- Cleanup


Version 4.0.0 (2016-04-06)
--------------------------

- Breaking change: Re-order `watch` arguments
- Breaking change: Add parameterized `--spool` option for finer control and remove `--no-spool`
- Breaking change: Remove `py.test.watch` console script
- Enhancement: Report filesystem events on re-run (fixes [#39](https://github.com/joeyespo/pytest-watch/issues/39))
- Enhancement: Allow `--ext=*` for watching any file type
- Enhancement: Run pytest from main thread, send `KeyboardInterrupt` on filesystem events, and wait for pytest to terminate before running next iteration (fixes [#36](https://github.com/joeyespo/pytest-watch/issues/36))
- Enhancement: Add `--pdb` option, forwarding to pytest
- Enhancement: Add `--wait` option to wait for all tests to complete before re-running on filesystem events (fixes [#21](https://github.com/joeyespo/pytest-watch/issues/21))
- Enhancement: Add `--afterrun` for running commands after pytest runs, regardless of whether it was interrupted ([#46](https://github.com/joeyespo/pytest-watch/pull/46) - thanks, [@blueyed][]! - and [fc471a457ae334e24422f939c04be25587d6d357](https://github.com/joeyespo/pytest-watch/commit/fc471a457ae334e24422f939c04be25587d6d357))
- Enhancement: Allow multiple `--ignore` args instead of one comma-separated list and forward them to pytest (fixes [#48](https://github.com/joeyespo/pytest-watch/issues/48))
- Enhancement: Add `-V` as short version of `--version`
- Enhancement: Add `--config` and include `<directory>` list in pytest args (fixes [#40](https://github.com/joeyespo/pytest-watch/issues/40))
- Enhancement: Improve config collection debuggability
- Bugfix: Fix config file collection on Python 2.6 and below ([#47](https://github.com/joeyespo/pytest-watch/pull/47) - thanks, [@lukaszb][]! - and [7f1508d908a61ade36312219d2414445e5b05686](https://github.com/joeyespo/pytest-watch/commit/7f1508d908a61ade36312219d2414445e5b05686))
- Bugfix: Re-run on directory changes (fixes [#44](https://github.com/joeyespo/pytest-watch/issues/44))
- Update LICENSE year
- Update README
- Cleanup


Version 3.10.0 (2016-02-12)
---------------------------

- Bugfix: Fix Python 2 support.


Version 3.9.0 (2016-02-12)
--------------------------

- Bugfix: Handle py.test exit code 5 (no tests are run/collected) as pass ([#42](https://github.com/joeyespo/pytest-watch/pull/42) - thanks, [@blueyed][]!)
- Bugfix: Show config-related errors instead of silently exiting with code 2 ([#45](https://github.com/joeyespo/pytest-watch/pull/45) - thanks, [@blueyed][]!)


Version 3.8.0 (2015-12-04)
--------------------------

- Enhancement: Read configuration from `pytest.ini` ([#30](https://github.com/joeyespo/pytest-watch/pull/30) - thanks, [@bendtherules][]!)


Version 3.7.0 (2015-12-02)
--------------------------

- Enhancement: Add `--runner` option
- Cleanup


Version 3.6.0 (2015-11-29)
--------------------------

- Enhancement: Add `--onexit` option ([#28](https://github.com/joeyespo/pytest-watch/pull/28) - thanks, [@blueyed][]!)
- Bugfix: Fix beep on Python 3.x by manually flushing the output buffer ([#27](https://github.com/joeyespo/pytest-watch/pull/27) - thanks, [@blueyed][]!)


Version 3.5.0 (2015-09-19)
--------------------------

- Python 3.5.0 compatibility ([#26](https://github.com/joeyespo/pytest-watch/pull/26) - thanks, [@ColtonProvias][]!)


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
[@ColtonProvias]: https://github.com/ColtonProvias
[@bendtherules]: https://github.com/bendtherules
[@lukaszb]: https://github.com/lukaszb
[@jacebrowning]: https://github.com/jacebrowning
