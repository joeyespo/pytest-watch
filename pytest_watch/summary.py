import time

from colorama import Fore, Style


STYLE_BRIGHT = Fore.WHITE + Style.NORMAL + Style.BRIGHT
STYLE_HIGHLIGHT = Fore.CYAN + Style.NORMAL + Style.BRIGHT


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


def _bright(arg):
    return STYLE_BRIGHT + arg + Style.RESET_ALL


def _highlight(arg):
    return STYLE_HIGHLIGHT + arg + Style.RESET_ALL


def show_summary(argv, events, verbose=False):
    command = ' '.join(argv)
    bright = _bright
    highlight = _highlight

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
