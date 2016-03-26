import os
import signal
import subprocess
import sys
from time import sleep

try:
    from queue import Empty
except ImportError:
    from Queue import Empty


is_windows = sys.platform == 'win32'


def beep():
    """
    Emits a beep sound.
    """
    sys.stdout.write('\a')
    sys.stdout.flush()


def clear():
    """
    Clears the terminal.
    """
    subprocess.call('cls' if is_windows else 'clear', shell=True)


def dequeue_all(queue, spool=None):
    """
    Empties the specified queue into a list, optionally with spooling.

    Spool default is 200 (ms). Set to 0 to disable.
    """
    if spool is None:
        spool = 200
    items = []
    while True:
        try:
            while True:
                items.append(queue.get_nowait())
        except Empty:
            # If spooling, wait a moment and check for new items
            if spool:
                sleep(spool / 1000.0)
                if not queue.empty():
                    continue
            break
    return items


def samepath(left, right):
    """
    Determines whether two paths are the same.
    """
    return (os.path.abspath(os.path.normcase(left)) ==
            os.path.abspath(os.path.normcase(right)))


def send_keyboard_interrupt(proc):
    """
    Sends a KeyboardInterrupt to the specified child process.
    """
    if is_windows:
        try:
            # Send KeyboardInterrupt to self, and therefore, to child processes
            try:
                os.kill(0, signal.CTRL_C_EVENT)
            except AttributeError:
                # Python 2.6 and below
                import ctypes
                ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, 0)
            # Immediately throws KeyboardInterrupt from the simulated CTRL-C
            proc.wait()
        except KeyboardInterrupt:
            # Ignore the simulated CTRL-C
            pass
    else:
        os.kill(proc.pid, signal.SIGINT)
