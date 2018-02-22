import shutil
import tempfile

try:
    from unittest import mock
except:
    import mock

from watchdog.events import FileModifiedEvent, FileMovedEvent, \
     FileCreatedEvent, FileDeletedEvent, FileCreatedEvent, DirModifiedEvent, \
     FileSystemEvent

from pytest_watch.constants import ALL_EXTENSIONS
from pytest_watch.watcher import EventListener
from pytest_watch.watcher import os as wos


def _assert_watched_filesystem_event(event, event_listener=None):
    listener = event_listener if event_listener else EventListener()

    assert listener.event_queue.empty()
    listener.on_any_event(event)

    assert not listener.event_queue.empty()


def _assert_unwatched_filesystem_event(event, event_listener=None):
    listener = event_listener if event_listener else EventListener()

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


@mock.patch.object(wos.path, "relpath")
def test_file_move_event(relpath):
    relpath.side_effect = lambda *args, **kwargs: args[0]
    src_path = "/tmp/file.py"
    dest_path = "/tmp/file-new.py"

    _assert_watched_filesystem_event(FileMovedEvent(src_path, dest_path))

    assert 2 == relpath.call_count, str("os.path.relpath should be called "
                                        "twice when file is moved src,dst")

    relpath.assert_any_call(src_path)
    relpath.assert_any_call(dest_path)


class TestExtensionsMatch():
    def setup_method(self):
        self.root_dir = tempfile.mkdtemp()

    def teardown_method(self):
        try:
            shutil.rmtree(self.root_dir)
        except:
            pass

    def test_event_over_all_extesions(self):
        _, filename = tempfile.mkstemp(dir=self.root_dir, suffix=".py")
        event = FileCreatedEvent(filename)
        listener = EventListener(extensions=ALL_EXTENSIONS)
        _assert_watched_filesystem_event(event, event_listener=listener)

    def test_event_over_observed_file(self):
        _, filename = tempfile.mkstemp(dir=self.root_dir, suffix=".py")
        event = FileCreatedEvent(filename)
        listener = EventListener(extensions=[".py"])
        _assert_watched_filesystem_event(event, event_listener=listener)

    def test_event_over_not_observed_file(self):
        _, filename = tempfile.mkstemp(dir=self.root_dir, suffix=".pyc")
        event = FileCreatedEvent(filename)
        listener = EventListener(extensions=[".py"])
        _assert_unwatched_filesystem_event(event, event_listener=listener)
