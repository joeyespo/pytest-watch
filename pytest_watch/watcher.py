from __future__ import print_function

import os
import time
import subprocess
import sys

from colorama import Fore, Style
from watchdog.events import (
    FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent,
    FileMovedEvent, FileDeletedEvent)
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from .spooler import EventSpooler

import pytest
import json

EVENT_NAMES = {
    FileModifiedEvent: 'modified',
    FileCreatedEvent: 'created',
    FileMovedEvent: 'moved',
    FileDeletedEvent: 'deleted',
}
WATCHED_EVENTS = list(EVENT_NAMES)
DEFAULT_EXTENSIONS = ['.py']
CLEAR_COMMAND = 'cls' if os.name == 'nt' else 'clear'
BEEP_CHARACTER = '\a'
STYLE_NORMAL = Fore.RESET
STYLE_HIGHLIGHT = Fore.CYAN + Style.NORMAL + Style.BRIGHT


class ChangeHandler(FileSystemEventHandler):
    """Listens for changes to files and re-runs tests after each change."""
    def __init__(self, auto_clear=False, beep_on_failure=True,
                 onpass=None, onfail=None, beforerun=None, extensions=[],
                 args=None, spool=True, verbose=False, quiet=False):
        super(ChangeHandler, self).__init__()
        self.auto_clear = auto_clear
        self.beep_on_failure = beep_on_failure
        self.onpass = onpass
        self.onfail = onfail
        self.beforerun = beforerun
        self.extensions = extensions or DEFAULT_EXTENSIONS
        self.args = args or []
        self.spooler = None
        if spool:
            self.spooler = EventSpooler(0.2, self.on_queued_events)
        self.verbose = verbose
        self.quiet = quiet

    def on_queued_events(self, events):
        summary = []
        for event in events:
            paths = [event.src_path]
            if isinstance(event, FileMovedEvent):
                paths.append(event.dest_path)
            event_name = EVENT_NAMES[type(event)]
            paths = tuple(map(os.path.relpath, paths))
            if any(os.path.splitext(path)[1].lower() in self.extensions
                   for path in paths):
                summary.append((event_name, paths))
        if summary:
            self.run(sorted(set(summary)))

    def on_any_event(self, event):
        if isinstance(event, tuple(WATCHED_EVENTS)):
            if self.spooler is not None:
                self.spooler.enqueue(event)
            else:
                self.on_queued_events([event])

    def run(self, summary=None):
        """Called when a file is changed to re-run the tests with py.test."""
        if self.auto_clear:
            subprocess.call(CLEAR_COMMAND, shell=True)
        command = ' '.join(['py.test'] + self.args)
        if summary and not self.auto_clear:
            print()
        if not self.quiet:
            highlight = lambda arg: STYLE_HIGHLIGHT + arg + STYLE_NORMAL
            msg = 'Running: {}'.format(highlight(command))
            if summary:
                if self.verbose:
                    file_lines = ['    {:9s}'.format(event_name + ':') + ' ' +
                                  ' -> '.join(map(highlight, paths))
                                  for event_name, paths in summary]
                    msg = ('Changes detected in files:\n{}\n\nRerunning: {}'
                           .format('\n'.join(file_lines), highlight(command)))
                else:
                    msg = ('Changes detected, rerunning: {}'
                           .format(highlight(command)))
            print(STYLE_NORMAL + msg + Fore.RESET + Style.NORMAL)
        if self.beforerun:
            os.system(self.beforerun)
        exit_code = pytest.main(self.args, plugins=[ReportCollectorPlugin()])
        passed = exit_code == 0

        # Beep if failed
        if not passed and self.beep_on_failure:
            sys.stdout.write(BEEP_CHARACTER)
            sys.stdout.flush()

        # Run custom commands
        if passed and self.onpass:
            os.system(self.onpass)
        elif not passed and self.onfail:
            os.system(self.onfail)


def watch(directories=[], ignore=[], auto_clear=False, beep_on_failure=True,
          onpass=None, onfail=None, beforerun=None, onexit=None, poll=False,
          extensions=[], args=[], spool=True, verbose=False, quiet=False):
    if not directories:
        directories = ['.']
    directories = [os.path.abspath(directory) for directory in directories]
    for directory in directories:
        if not os.path.isdir(directory):
            raise ValueError('Directory not found: ' + directory)

    if ignore:
        recursive_dirs, non_recursive_dirs = split_recursive(
            directories, ignore)
    else:
        recursive_dirs = directories
        non_recursive_dirs = []

    # Initial run
    event_handler = ChangeHandler(auto_clear, beep_on_failure,
                                  onpass, onfail, beforerun, extensions, args,
                                  spool, verbose, quiet)
    event_handler.run()

    # Setup watchdog
    observer = PollingObserver() if poll else Observer()
    for directory in recursive_dirs:
        observer.schedule(event_handler, path=directory, recursive=True)
    for directory in non_recursive_dirs:
        observer.schedule(event_handler, path=directory, recursive=False)

    # Watch and run tests until interrupted by user
    try:
        observer.start()
        while True:
            time.sleep(1)
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
    if onexit:
        os.system(onexit)


def samepath(left, right):
    return (os.path.abspath(os.path.normcase(left)) ==
            os.path.abspath(os.path.normcase(right)))


def split_recursive(directories, ignore):
    non_recursive_dirs = []
    recursive_dirs = []
    for directory in directories:
        subdirs = [os.path.join(directory, d)
                   for d in os.listdir(directory)
                   if os.path.isdir(d)]
        filtered = [subdir for subdir in subdirs
                    if not any(samepath(os.path.join(directory, d), subdir)
                               for d in ignore)]
        if len(subdirs) == len(filtered):
            recursive_dirs.append(directory)
        else:
            non_recursive_dirs.append(directory)
            recursive_dirs.extend(filtered)

    return sorted(set(recursive_dirs)), sorted(set(non_recursive_dirs))


class ReportCollectorPlugin(object):

    """ Catch report for all test and set to env"""

    def __init__(self):
        self.test_reports = []

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        # execute all other hooks to obtain the report object

        outcome = yield
        report_obj = outcome.get_result()

        test_report = {}
        # copy stuff from report_obj
        test_report["duration"] = report_obj.duration
        test_report["failed"] = report_obj.failed
        test_report["fspath"] = report_obj.fspath
        test_report["keywords"] = report_obj.keywords
        test_report["location"] = report_obj.location
        if report_obj.longrepr:
            test_report["longrepr"] = str(report_obj.longrepr)
        else:
            test_report["longrepr"] = None
        test_report["nodeid"] = report_obj.nodeid
        test_report["outcome"] = report_obj.outcome
        test_report["passed"] = report_obj.passed
        test_report["sections"] = report_obj.sections
        test_report["skipped"] = report_obj.skipped
        test_report["when"] = report_obj.when

        self.test_reports.append(test_report)

    def pytest_sessionfinish(self, session, exitstatus):
        os.environ["PYTEST_REPORTS"] = json.dumps(self.test_reports)
