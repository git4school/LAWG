import contextlib
import time
from abc import ABC, abstractmethod
from pathlib import Path

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
        self.git_manager = git_manager
        regexes = [".*"]
        ignore_regexes = [".*~", "(?:.+[/\\\\])?\\.git[/\\\\].*"]
        ignore_directories = True
        case_sensitive = True
        my_event_handler = RegexMatchingEventHandler(regexes, ignore_regexes,
                                                     ignore_directories,
                                                     case_sensitive)

        my_event_handler.on_created = self.on_created
        my_event_handler.on_deleted = self.on_deleted
        my_event_handler.on_modified = self.on_modified
        my_event_handler.on_moved = self.on_moved
        self.observer = PausingObserver()
        self.observer.schedule(my_event_handler, folder_to_watch,
                               recursive=True)

    def start(self):
        self.observer.start()

    def stop(self):
        self.git_manager.push()
        self.observer.stop()
        self.observer.join()

    def on_created(self, event):
        if not self.git_manager.get_diff("g4s-auto"):
            self.__save(event.src_path, "modified", amend=True)
        else:
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

    def __save(self, raw_path: Path, event_type: str, amend=False):
        path = Path(raw_path)
        if "g4s-auto" not in self.git_manager.get_local_branches():
            self.git_manager.branch("g4s-auto")  # on pourrait pousser en vérifiant les branches en remote et en pullant
        self.git_manager.reset("g4s-auto")
        self.git_manager.add(path)
        if amend:
            self.git_manager.amend(f"[auto] {path.name} has been {event_type}")
        else:
            self.git_manager.commit(f"[auto] {path.name} has been {event_type}")
        self.git_manager.branch("g4s-auto", force=True)
        self.git_manager.reset("HEAD@{2}")

    @contextlib.contextmanager
    def pause(self):
        self.observer.pause()
        yield
        self.observer.resume()
