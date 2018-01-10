try:
    from unittest import mock
except:
    import mock

from watchdog.events import FileModifiedEvent, FileMovedEvent, FileCreatedEvent, \
     FileDeletedEvent, FileCreatedEvent, DirModifiedEvent, FileSystemEvent

from pytest_watch.watcher import EventListener


def _assert_watched_filesystem_event(event):
    listener = EventListener()

    assert listener.event_queue.empty()
    listener.on_any_event(event)

    assert not listener.event_queue.empty()


def _assert_unwatched_filesystem_event(event):
    listener = EventListener()

    assert listener.event_queue.empty()
    listener.on_any_event(event)

    assert listener.event_queue.empty()


def test_unwatched_event():
    _assert_unwatched_filesystem_event(FileSystemEvent("/tmp/file.py"))
    _assert_unwatched_filesystem_event(DirModifiedEvent("/tmp/"))


def test_file_modify_event():
    _assert_watched_filesystem_event(FileModifiedEvent("/tmp/file.py"))


def test_file_create_event():
    _assert_watched_filesystem_event(FileCreatedEvent("/tmp/file.py"))


def test_file_delete_event():
    _assert_watched_filesystem_event(FileDeletedEvent("/tmp/file.py"))


from pytest_watch.watcher import os as wos


@mock.patch.object(wos.path, "relpath")
def test_file_move_event(relpath):
    relpath.side_effect = lambda *args, **kwargs: args[0]
    src_path = "/tmp/file.py"
    dest_path = "/tmp/file-new.py"

    _assert_watched_filesystem_event(FileMovedEvent(src_path, dest_path))

    assert 2 == relpath.call_count, \
           "os.path.relpath should be called twice (src_path, dest_path)"

    relpath.assert_any_call(src_path)
    relpath.assert_any_call(dest_path)


