import contextlib
import time
from abc import ABC, abstractmethod
from pathlib import Path, PurePosixPath, PurePath

from git import RemoteProgress
from watchdog.events import RegexMatchingEventHandler
from watchdog.observers.polling import PollingObserver as Observer

from utils.git_manager import GitManagerInterface


class FileWatcherInterface(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0),
              message or "NO MESSAGE")


class PausingObserver(Observer):
    def __init__(self):
        super().__init__()
        self._is_paused = False

    def dispatch_events(self, *args, **kwargs):
        if not self._is_paused:
            super(PausingObserver, self).dispatch_events(*args, **kwargs)

    def pause(self):
        self._is_paused = True

    def resume(self):
        time.sleep(self.timeout)
        self.event_queue.queue.clear()
        self._is_paused = False

    @contextlib.contextmanager
    def ignore_events(self):
        self.pause()
        yield
        self.resume()


class FileWatcherWatchdog(FileWatcherInterface):
    def __init__(self, folder_to_watch, git_manager: GitManagerInterface):
        self.is_paused = False
        self.git_manager = git_manager
        regexes = [".*"]
        ignore_regexes = [".*~", "(?:.+\/)?\.git\/.*"]
        ignore_directories = True
        case_sensitive = True
        my_event_handler = RegexMatchingEventHandler(regexes, ignore_regexes, ignore_directories, case_sensitive)

        my_event_handler.on_created = self.on_created
        my_event_handler.on_deleted = self.on_deleted
        my_event_handler.on_modified = self.on_modified
        my_event_handler.on_moved = self.on_moved
        self.observer = PausingObserver()
        self.observer.schedule(my_event_handler, folder_to_watch,
                               recursive=True)

    def start(self):
        self.observer.start()

    def pause(self):
        self.observer.pause()

    def resume(self):
        self.observer.resume()

    def stop(self):
        self.git_manager.push()
        self.observer.stop()
        self.observer.join()

    def on_created(self, event):
        self.__save(event.src_path, event.event_type)

    def on_deleted(self, event):
        self.__save(event.src_path, event.event_type)
        pass

    def on_modified(self, event):
        self.__save(event.src_path, event.event_type)
        pass

    def on_moved(self, event):
        self.__save(event.src_path, event.event_type)
        pass

    def __save(self, raw_path: Path, event_type: str):
        with self.observer.ignore_events():
            path = Path(raw_path)
            self.git_manager.checkout("g4s-auto")
            self.git_manager.add(path)
            self.git_manager.commit(f"[auto] {path.name} has been {event_type}")
            self.git_manager.checkout("master")
            self.git_manager.read_tree("g4s-auto")
            self.git_manager.checkout_index()
