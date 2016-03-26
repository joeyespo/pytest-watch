from __future__ import print_function

import os
import subprocess
from time import sleep
from traceback import format_exc

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from colorama import Fore, Style
from watchdog.events import (
    FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent,
    FileMovedEvent, FileDeletedEvent)
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from .helpers import (
    beep, clear, dequeue_all, is_windows, samepath, send_keyboard_interrupt)


ALL_EXTENSIONS = object()


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
STYLE_BRIGHT = Fore.WHITE + Style.NORMAL + Style.BRIGHT
STYLE_HIGHLIGHT = Fore.CYAN + Style.NORMAL + Style.BRIGHT


# Exit codes from pytest
# http://pytest.org/latest/_modules/_pytest/main.html
EXIT_OK = 0
EXIT_INTERRUPTED = 2
EXIT_NOTESTSCOLLECTED = 5


class EventListener(FileSystemEventHandler):
    """
    Listens for changes to files and re-runs tests after each change.
    """
    def __init__(self, extensions=[]):
        super(EventListener, self).__init__()
        self.event_queue = Queue()
        self.extensions = extensions or DEFAULT_EXTENSIONS

    def on_any_event(self, event):
        """
        Called when a file event occurs.
        Note that this gets called on a worker thread.
        """
        # Filter for allowed event types
        if not isinstance(event, WATCHED_EVENTS):
            return

        src_path = os.path.relpath(event.src_path)
        dest_path = None
        if isinstance(event, FileMovedEvent):
            dest_path = os.path.relpath(event.dest_path)

        # Filter files that don't match the allowed extensions
        if not event.is_directory and self.extensions != ALL_EXTENSIONS:
            src_ext = os.path.splitext(src_path)[1].lower()
            src_included = src_ext in self.extensions
            dest_included = False
            if dest_path:
                dest_ext = os.path.splitext(dest_path)[1].lower()
                dest_included = dest_ext in self.extensions
            if not src_included and not dest_included:
                return

        self.event_queue.put((type(event), src_path, dest_path))


def _reduce_events(events):
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


def _show_summary(argv, events, verbose=False):
    command = ' '.join(argv)
    bright = lambda arg: STYLE_BRIGHT + arg + Style.RESET_ALL
    highlight = lambda arg: STYLE_HIGHLIGHT + arg + Style.RESET_ALL

    if not events:
        print('Running: {}'.format(highlight(command)))
        return

    events = _reduce_events(events)
    if verbose:
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

    print('\n'.join(lines))


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
          oninterrupt=None, poll=False, extensions=[], args=[], spool=None,
          verbose=False, quiet=False):
    argv = (runner or 'py.test').split(' ') + (args or [])

    if not directories:
        directories = ['.']
    directories = [os.path.abspath(directory) for directory in directories]
    for directory in directories:
        if not os.path.isdir(directory):
            raise ValueError('Directory not found: ' + directory)

    # Setup event handler
    event_listener = EventListener(extensions)

    # Setup watchdog
    observer = PollingObserver() if poll else Observer()
    recursedirs, norecursedirs = _split_recursive(directories, ignore)
    for directory in recursedirs:
        observer.schedule(event_listener, path=directory, recursive=True)
    for directory in norecursedirs:
        observer.schedule(event_listener, path=directory, recursive=False)
    observer.start()

    # Watch and run tests until interrupted by user
    events = []
    while True:
        try:
            # Prepare next run
            if auto_clear:
                clear()
            elif not quiet:
                print()

            # Show event summary
            if not quiet:
                _show_summary(argv, events, verbose)

            # Run custom command
            run_hook(beforerun)

            # Run tests
            p = subprocess.Popen(argv, shell=is_windows)
            try:
                while True:
                    # Check for completion
                    exit_code = p.poll()
                    if exit_code is not None:
                        break
                    # Interrupt the current test run on filesystem event
                    if not event_listener.event_queue.empty():
                        send_keyboard_interrupt(p)
                        exit_code = p.wait()
                        break
                    # Allow user to initiate a keyboard interrupt
                    sleep(0.1)
            except KeyboardInterrupt:
                # Wait for current test run cleanup
                if p.wait() == EXIT_INTERRUPTED:
                    run_hook(oninterrupt)
                # Exit, since this keyboard interrupt was user-initiated
                break

            # Run custom commands
            if exit_code == EXIT_INTERRUPTED:
                run_hook(oninterrupt)
            elif exit_code in [EXIT_OK, EXIT_NOTESTSCOLLECTED]:
                run_hook(onpass)
            else:
                if beep_on_failure:
                    beep()
                run_hook(onfail)

            # Wait for a filesystem event
            while event_listener.event_queue.empty():
                sleep(0.1)

            # Collect events for summary of next run
            events = dequeue_all(event_listener.event_queue, spool)
        except KeyboardInterrupt:
            break
        except Exception as ex:
            print(format_exc() if verbose else 'Error: {}'.format(ex))
            break

    # Stop and wait for observer
    observer.stop()
    observer.join()

    # Run exit script
    run_hook(onexit)
