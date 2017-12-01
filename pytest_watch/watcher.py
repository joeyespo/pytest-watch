from __future__ import print_function

import os
import re
import sys
import subprocess
import time
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

from .constants import (
    ALL_EXTENSIONS, EXIT_NOTESTSCOLLECTED, EXIT_OK, DEFAULT_EXTENSIONS)
from .helpers import (
    beep, clear, dequeue_all, is_test_filepath, is_windows, samepath,
    send_keyboard_interrupt)
from .util import import_function_from_module


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
STYLE_BRIGHT = Fore.WHITE + Style.NORMAL + Style.BRIGHT
STYLE_HIGHLIGHT = Fore.CYAN + Style.NORMAL + Style.BRIGHT


class EventListener(FileSystemEventHandler):
    """
    Listens for changes to files and re-runs tests after each change.
    """
    def __init__(self, extensions=[], confwatch=None):
        super(EventListener, self).__init__()
        self.event_queue = Queue()
        self.extensions = extensions or DEFAULT_EXTENSIONS
        self.should_ignore_event = import_function_from_module(
            'should_ignore_event',
            confwatch,
            default=lambda _: False)

    def on_any_event(self, event):
        """
        Called when a file event occurs.
        Note that this gets called on a worker thread.
        """
        # Filter for allowed event types
        if not isinstance(event, WATCHED_EVENTS):
            return

        if self.should_ignore_event(event):
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


def _get_pytest_runner(custom=None, pytest_args=None, events=None,
                       all_valid_test_filepaths=None,
                       get_test_filepath_for_modified_filepath=None):
    if custom:
        args = custom.split(' ')
    elif os.getenv('VIRTUAL_ENV'):
        args = ['py.test']
    else:
        args = [sys.executable, '-m', 'pytest']

    args += (pytest_args or [])

    if not events or not get_test_filepath_for_modified_filepath:
        return args

    return args + _get_runner_filepath_args(events, all_valid_test_filepaths,
                                            get_test_filepath_for_modified_filepath)


def _get_runner_filepath_args(events, all_valid_test_filepaths,
                              get_test_filepath_for_modified_filepath):
    # convert & filter test file paths from modified file paths
    test_filepaths = set()
    for filepath in _get_changed_filepaths_for_events(events):
        test_filepath = get_test_filepath_for_modified_filepath(filepath)
        if test_filepath:
            test_filepaths.add(test_filepath)

    # only run a subset of tests if all the test file paths are valid
    valid_filepaths = {f for f in test_filepaths if f in all_valid_test_filepaths}
    if valid_filepaths.issubset(all_valid_test_filepaths):
        return list(valid_filepaths)

    # otherwise run all tests
    return []


def _get_changed_filepaths_for_events(events):
    for event, src_path, dest_path in events:
        if event in (FileModifiedEvent, FileCreatedEvent):
            yield src_path
        elif event == FileMovedEvent:
            yield dest_path


def _get_all_valid_test_filepaths(runner):
    cmd = runner + ['--collect-only']
    p = subprocess.Popen(cmd, shell=is_windows, stdout=subprocess.PIPE)
    stdout, _ = p.communicate()
    lines = stdout.decode('utf-8').splitlines()
    matcher = re.compile(r"^<Module '(?P<filepath>.+)'>$")
    matches = [matcher.match(line) for line in lines]
    return {m.group('filepath') for m in matches if m}


def _update_valid_test_filepaths(all_valid_test_filepaths, events):
    for event, src_path, dest_path in events:
        is_test = is_test_filepath(src_path)
        if is_test and event in (FileCreatedEvent, FileModifiedEvent):
            all_valid_test_filepaths.add(src_path)
        elif event == FileDeletedEvent and src_path in all_valid_test_filepaths:
            all_valid_test_filepaths.remove(src_path)
        elif event == FileMovedEvent and src_path in all_valid_test_filepaths:
            all_valid_test_filepaths.remove(src_path)
            all_valid_test_filepaths.add(dest_path)
    return all_valid_test_filepaths


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

    time_stamp = time.strftime("%c", time.localtime(time.time()))
    run_command_info = '[{}] Running: {}'.format(time_stamp,
                                                 highlight(command))
    if not events:
        print(run_command_info)
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
        lines.append(run_command_info)
    else:
        lines = []
        for event, src, dest in events:
            lines.append('{} detected: {}'.format(
                EVENT_NAMES[event],
                bright(src + (' -> ' + dest if dest else ''))))
        lines.append('')
        lines.append(run_command_info)

    print('\n'.join(lines))


def _split_recursive(directories, ignore):
    if not ignore:
        return directories, []

    # TODO: Have this work recursively

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


def run_hook(cmd, *args):
    """
    Runs a command hook, if specified.
    """
    if cmd:
        command = ' '.join(map(str, (cmd,) + args))
        subprocess.call(command, shell=True)


def watch(directories=[], ignore=[], extensions=[], beep_on_failure=True,
          auto_clear=False, wait=False, beforerun=None, afterrun=None,
          onpass=None, onfail=None, onexit=None, runner=None, spool=None,
          poll=False, verbose=False, quiet=False, pytest_args=[],
          confwatch=None):

    if not directories:
        directories = ['.']
    directories = [os.path.abspath(directory) for directory in directories]
    for directory in directories:
        if not os.path.isdir(directory):
            raise ValueError('Directory not found: ' + directory)

    # Setup event handler
    event_listener = EventListener(extensions, confwatch)

    # Setup watchdog
    observer = PollingObserver() if poll else Observer()
    recursedirs, norecursedirs = _split_recursive(directories, ignore)
    for directory in recursedirs:
        observer.schedule(event_listener, path=directory, recursive=True)
    for directory in norecursedirs:
        observer.schedule(event_listener, path=directory, recursive=False)
    observer.start()

    # Get user function to determine which tests to run for modified files
    get_test_filepath_for_modified_filepath = import_function_from_module(
        'get_test_filepath_for_modified_filepath',
        confwatch,
        default=None)

    all_valid_test_filepaths = _get_all_valid_test_filepaths(
        _get_pytest_runner(runner, pytest_args))

    # Watch and run tests until interrupted by user
    events = []
    while True:
        try:
            # Prepare next run
            if auto_clear:
                clear()
            elif not quiet:
                print()

            # check if any new test files
            all_valid_test_filepaths = _update_valid_test_filepaths(
                all_valid_test_filepaths, events)

            # get pytest args for the queued events
            argv = _get_pytest_runner(runner, pytest_args, events,
                                      all_valid_test_filepaths,
                                      get_test_filepath_for_modified_filepath)

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
                    if not wait and not event_listener.event_queue.empty():
                        send_keyboard_interrupt(p)
                        exit_code = p.wait()
                        break
                    # Allow user to initiate a keyboard interrupt
                    time.sleep(0.1)
            except KeyboardInterrupt:
                # Wait for current test run cleanup
                run_hook(afterrun, p.wait())
                # Exit, since this keyboard interrupt was user-initiated
                break

            # Run custom command
            run_hook(afterrun, exit_code)

            # Run dependent commands
            if exit_code in [EXIT_OK, EXIT_NOTESTSCOLLECTED]:
                run_hook(onpass)
            else:
                if beep_on_failure:
                    beep()
                run_hook(onfail)

            # Wait for a filesystem event
            while event_listener.event_queue.empty():
                time.sleep(0.1)

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
