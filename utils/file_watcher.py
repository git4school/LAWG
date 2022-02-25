from abc import ABC, abstractmethod

from git import RemoteProgress
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers.polling import PollingObserver as Observer

from git_manager import GitManagerInterface


class FileWatcherInterface(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0),
              message or "NO MESSAGE")


class FileWatcherWatchdog(FileWatcherInterface):
    def __init__(self, folder_to_watch, git_manager: GitManagerInterface):
        self.git_manager = git_manager
        patterns = ["*"]
        ignore_patterns = ["*~", r"*\.git*"]
        ignore_directories = True
        case_sensitive = True
        my_event_handler = PatternMatchingEventHandler(patterns,
                                                       ignore_patterns,
                                                       ignore_directories,
                                                       case_sensitive)

        my_event_handler.on_created = self.on_created
        my_event_handler.on_deleted = self.on_deleted
        my_event_handler.on_modified = self.on_modified
        my_event_handler.on_moved = self.on_moved
        self.observer = Observer()
        self.observer.schedule(my_event_handler, folder_to_watch,
                               recursive=True)

    def start(self):
        self.observer.start()

    def stop(self):
        self.git_manager.push()
        self.observer.stop()
        self.observer.join()

    def on_created(self, event):
        print(f"{event.src_path} has been created!")

    def on_deleted(self, event):
        print(f"Someone deleted {event.src_path}!")

    def on_modified(self, event):
        path = Path(event.src_path)
        self.git_manager.add(path)
        self.git_manager.commit(f"Git4school auto-commit: {path.name} has been modified")

    def on_moved(self, event):
        print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")
