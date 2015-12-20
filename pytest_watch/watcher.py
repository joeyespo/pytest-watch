from __future__ import print_function

import os
import subprocess
from time import sleep

from colorama import Fore, Style
from watchdog.events import (
    FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent,
    FileMovedEvent, FileDeletedEvent)
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from .helpers import beep, clear, is_windows, samepath
from .spooler import EventSpooler


EVENT_NAMES = {
    FileModifiedEvent: 'Change',
    FileCreatedEvent: 'New file',
    FileMovedEvent: 'Move',
    FileDeletedEvent: 'Deletion',
}
VERBOSE_EVENT_NAMES = {
    FileModifiedEvent: 'Modified:',
    FileCreatedEvent: 'Created:',
    FileMovedEvent: 'Moved:',
    FileDeletedEvent: 'Deleted:',
}
WATCHED_EVENTS = tuple(EVENT_NAMES)
DEFAULT_EXTENSIONS = ['.py']
STYLE_NORMAL = Fore.RESET
STYLE_BRIGHT = Fore.WHITE + Style.NORMAL + Style.BRIGHT
STYLE_HIGHLIGHT = Fore.CYAN + Style.NORMAL + Style.BRIGHT


# Exit codes from pytest
# http://pytest.org/latest/_modules/_pytest/main.html
EXIT_OK = 0
EXIT_INTERRUPTED = 2
EXIT_NOTESTSCOLLECTED = 5


class ChangeHandler(FileSystemEventHandler):
    """
    Listens for changes to files and re-runs tests after each change.
    """
    def __init__(self, auto_clear=False, beep_on_failure=True, onpass=None,
                 onfail=None, oninterrupt=None, runner=None, beforerun=None,
                 extensions=[], args=None, spool=True, verbose=False,
                 quiet=False):
        super(ChangeHandler, self).__init__()
        self.auto_clear = auto_clear
        self.beep_on_failure = beep_on_failure
        self.beforerun = beforerun
        self.onpass = onpass
        self.onfail = onfail
        self.oninterrupt = oninterrupt
        self.runner = runner or 'py.test'
        self.args = args or []
        self.argv = self.runner.split(' ') + self.args
        self.extensions = extensions or DEFAULT_EXTENSIONS
        self.spooler = None
        if spool:
            self.spooler = EventSpooler(0.2, self.on_queued_events)
        self.verbose = verbose
        self.quiet = quiet

    def on_queued_events(self, queue):
        """
        Called when a file is changed.
        """
        events = []
        for event in queue:
            event_type = type(event)
            src_path = os.path.relpath(event.src_path)
            if isinstance(event, FileMovedEvent):
                dest_path = os.path.relpath(event.dest_path)
            else:
                dest_path = None

            src_ext = os.path.splitext(src_path)[1].lower()
            included = src_ext in self.extensions

            if dest_path and not included:
                dest_ext = os.path.splitext(dest_path)[1].lower()
                included = dest_ext in self.extensions

            if included:
                events.append((event_type, src_path, dest_path))

        # Do nothing if all events are filtered out
        if not events:
            return

        # Run pytest
        self.run(events)

    def on_any_event(self, event):
        # Filter for watched events
        if not isinstance(event, WATCHED_EVENTS):
            return

        # Enqueue event if spooler is available
        if self.spooler:
            self.spooler.enqueue(event)
            return

        # Handle event directly
        self.on_queued_events([event])

    def reduce_events(self, events):
        # FUTURE: Reduce ['a -> b', 'b -> c'] renames to ['a -> c']

        creates = []
        moves = []
        for event, src, dest in events:
            if event == FileCreatedEvent:
                creates.append(dest)
            if event == FileMovedEvent:
                moves.append(dest)

        seen = []
        filtered = []
        for event, src, dest in events:
            # Skip 'modified' event during 'created'
            if src in creates and event != FileCreatedEvent:
                continue

            # Skip 'modified' event during 'moved'
            if src in moves:
                continue

            # Skip duplicate events
            if src in seen:
                continue
            seen.append(src)

            filtered.append((event, src, dest))
        return filtered

    def show_summary(self, events):
        command = ' '.join(self.argv)
        bright = lambda arg: STYLE_BRIGHT + arg + Style.RESET_ALL
        highlight = lambda arg: STYLE_HIGHLIGHT + arg + Style.RESET_ALL
        events = self.reduce_events(events)

        if not events:
            lines = ['Running: {}'.format(highlight(command))]
        elif self.verbose:
            lines = ['Changes detected:']
            m = max(map(len, map(lambda e: VERBOSE_EVENT_NAMES[e[0]], events)))
            for event, src, dest in events:
                event = VERBOSE_EVENT_NAMES[event].ljust(m)
                lines.append('  {} {}'.format(
                    event,
                    highlight(src + (' -> ' + dest if dest else ''))))
            lines.append('')
            lines.append('Running: {}'.format(highlight(command)))
        else:
            lines = []
            for event, src, dest in events:
                lines.append('{} detected: {}'.format(
                    EVENT_NAMES[event],
                    bright(src + (' -> ' + dest if dest else ''))))
            lines.append('')
            lines.append('Running: {}'.format(highlight(command)))

        print(STYLE_NORMAL + '\n'.join(lines) + Fore.RESET + Style.NORMAL)

    def run(self, events=[]):
        """
        Called when a file is changed to re-run the tests with py.test.
        """
        # Prepare status update
        if self.auto_clear:
            clear()
        elif not self.quiet:
            print()

        # Show event summary
        if not self.quiet:
            self.show_summary(events)

        # Run custom command
        run_hook(self.beforerun)

        # Run py.test or py.test runner
        exit_code = subprocess.call(self.argv, shell=is_windows)

        # Translate exit codes
        interrupted = exit_code == EXIT_INTERRUPTED
        passed = exit_code in [EXIT_OK, EXIT_NOTESTSCOLLECTED]

        # Beep if failed
        if not passed and self.beep_on_failure:
            beep()

        # Run custom commands
        if interrupted:
            run_hook(self.oninterrupt)
        elif passed:
            run_hook(self.onpass)
        else:
            run_hook(self.onfail)


def _split_recursive(directories, ignore):
    if not ignore:
        return directories, []

    recursedirs, norecursedirs = [], []
    for directory in directories:
        subdirs = [os.path.join(directory, d)
                   for d in os.listdir(directory)
                   if os.path.isdir(d)]
        filtered = [subdir for subdir in subdirs
                    if not any(samepath(os.path.join(directory, d), subdir)
                               for d in ignore)]
        if len(subdirs) == len(filtered):
            recursedirs.append(directory)
        else:
            norecursedirs.append(directory)
            recursedirs.extend(filtered)

    return sorted(set(recursedirs)), sorted(set(norecursedirs))


def run_hook(cmd):
    """
    Runs a command hook, if specified.
    """
    if cmd:
        os.system(cmd)


def watch(directories=[], ignore=[], auto_clear=False, beep_on_failure=True,
          onpass=None, onfail=None, runner=None, beforerun=None, onexit=None,
          oninterrupt=None, poll=False, extensions=[], args=[], spool=True,
          verbose=False, quiet=False):
    if not directories:
        directories = ['.']
    directories = [os.path.abspath(directory) for directory in directories]
    for directory in directories:
        if not os.path.isdir(directory):
            raise ValueError('Directory not found: ' + directory)

    event_handler = ChangeHandler(
        auto_clear, beep_on_failure, onpass, onfail, oninterrupt, runner,
        beforerun, extensions, args, spool, verbose, quiet)

    # Setup watchdog
    observer = PollingObserver() if poll else Observer()
    recursedirs, norecursedirs = _split_recursive(directories, ignore)
    for directory in recursedirs:
        observer.schedule(event_handler, path=directory, recursive=True)
    for directory in norecursedirs:
        observer.schedule(event_handler, path=directory, recursive=False)
    observer.start()

    # Initial run
    event_handler.run()

    # Watch and run tests until interrupted by user
    try:
        while True:
            sleep(1)
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        run_hook(oninterrupt)
    else:
        run_hook(onexit)
