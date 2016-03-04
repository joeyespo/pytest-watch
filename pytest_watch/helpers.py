import os
import subprocess
import sys


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


def samepath(left, right):
    """
    Determines whether two paths are the same.
    """
    return (os.path.abspath(os.path.normcase(left)) ==
            os.path.abspath(os.path.normcase(right)))
