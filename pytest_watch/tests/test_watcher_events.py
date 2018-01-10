from watchdog.events import FileModifiedEvent, DirModifiedEvent

from pytest_watch.watcher import EventListener


def test_unwatched_event():
    event = DirModifiedEvent("/tmp/file.py")
    listener = EventListener()

    assert listener.event_queue.empty()
    listener.on_any_event(event)

    assert listener.event_queue.empty()


def test_file_modified_event():
    event = FileModifiedEvent("/tmp/file.py")
    listener = EventListener()

    assert listener.event_queue.empty()
    listener.on_any_event(event)

    assert not listener.event_queue.empty()
