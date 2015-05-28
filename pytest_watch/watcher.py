from __future__ import print_function

import os
import time
import subprocess

from colorama import Fore
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import (FileSystemEventHandler, FileModifiedEvent,
                             FileCreatedEvent, FileMovedEvent)


WATCHED_EVENTS = [FileModifiedEvent, FileCreatedEvent, FileMovedEvent]
DEFAULT_EXTENSIONS = ['.py']
CLEAR_COMMAND = 'cls' if os.name == 'nt' else 'clear'
BEEP_CHARACTER = '\a'


class ChangeHandler(FileSystemEventHandler):
    """Listens for changes to files and re-runs tests after each change."""
    def __init__(self, auto_clear=False, beep_on_failure=True,
                 onpass=None, onfail=None, extensions=[], args=None):
        super(ChangeHandler, self).__init__()
        self.auto_clear = auto_clear
        self.beep_on_failure = beep_on_failure
        self.onpass = onpass
        self.onfail = onfail
        self.extensions = extensions or DEFAULT_EXTENSIONS
        self.args = args or []

    def on_any_event(self, event):
        if isinstance(event, tuple(WATCHED_EVENTS)):
            dest = event.dest_path if isinstance(event, FileMovedEvent) else event.src_path
            ext = os.path.splitext(dest)[1].lower()
            if ext in self.extensions:
                self.run(dest)

    def run(self, filename=None):
        """Called when a file is changed to re-run the tests with py.test."""
        if self.auto_clear:
            subprocess.call(CLEAR_COMMAND)
        command = ' '.join(['py.test'] + self.args)
        msg, arg = 'Running pytest command: {}', command
        if filename:
            msg, arg = 'Change detected in {}, rerunning pytest command...', filename
        print()
        print(Fore.CYAN + msg.format(Fore.LIGHTCYAN_EX + arg + Fore.CYAN) + Fore.RESET)
        if self.auto_clear:
            print()
        exit_code = subprocess.call(['py.test'] + self.args)
        passed = exit_code == 0

        # Beep if failed
        if not passed and self.beep_on_failure:
            print(BEEP_CHARACTER, end='')

        # Run custom commands
        if passed and self.onpass:
            os.system(self.onpass)
        elif not passed and self.onfail:
            os.system(self.onfail)


def watch(directories=[], ignore=[], auto_clear=False, beep_on_failure=True,
          onpass=None, onfail=None, poll=False, extensions=[], args=[]):
    if not directories:
        directories = ['.']
    directories = [os.path.abspath(directory) for directory in directories]
    for directory in directories:
        if not os.path.isdir(directory):
            raise ValueError('Directory not found: ' + directory)
    recursive_dirs = directories
    non_recursive_dirs = []
    if ignore:
        non_recursive_dirs = []
        recursive_dirs = []
        for directory in directories:
            subdirs = [
                os.path.join(directory, d)
                for d in os.listdir(directory)
                if os.path.isdir(d)
            ]
            ok_subdirs = [
                subd for subd in subdirs
                if not any(os.path.samefile(os.path.join(directory, d), subd)
                           for d in ignore)
            ]
            if len(subdirs) == len(ok_subdirs):
                recursive_dirs.append(directory)
            else:
                non_recursive_dirs.append(directory)
                recursive_dirs.extend(ok_subdirs)

    recursive_dirs = sorted(set(recursive_dirs))
    non_recursive_dirs = sorted(set(non_recursive_dirs))

    # Initial run
    event_handler = ChangeHandler(auto_clear, beep_on_failure,
                                  onpass, onfail, extensions, args)
    event_handler.run()

    # Setup watchdog
    if poll:
        observer = PollingObserver()
    else:
        observer = Observer()

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
