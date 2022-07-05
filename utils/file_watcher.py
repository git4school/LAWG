import contextlib
import os
import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path

from git import RemoteProgress
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers.polling import PollingObserver as Observer

from utils.file_manager import FileManagerInterface
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


class GitignoreEventHandler(PatternMatchingEventHandler):
    def __init__(self, git_manager: GitManagerInterface, patterns, ignore_paths,
                 ignore_directories,
                 case_sensitive):
        super().__init__(patterns, ignore_paths, ignore_directories, case_sensitive)
        self.git_manager = git_manager

    def dispatch(self, event):
        if self.ignore_directories and event.is_directory:
            return

        paths = []
        if hasattr(event, 'dest_path'):
            paths.append(Path(os.fsdecode(event.dest_path)))
        if event.src_path:
            paths.append(Path(os.fsdecode(event.src_path)))
        not_a_dot_git_file = all('.git' not in p.parts for p in paths)
        if not_a_dot_git_file and not self.git_manager.is_ignored(paths):
            super().dispatch(event)


class FileWatcherWatchdog(FileWatcherInterface):
    def __init__(self, folder_to_watch, git_manager: GitManagerInterface,
                 file_manager: FileManagerInterface):
        self.git_manager = git_manager
        self.folder_to_watch = folder_to_watch
        self.file_manager = file_manager
        patterns = ["**"]
        ignore_paths = [".git"]
        ignore_directories = True
        case_sensitive = True
        my_event_handler = GitignoreEventHandler(git_manager, patterns, ignore_paths,
                                                 ignore_directories,
                                                 case_sensitive)

        my_event_handler.on_created = self.on_created
        my_event_handler.on_deleted = self.on_deleted
        my_event_handler.on_modified = self.on_modified
        my_event_handler.on_moved = self.on_moved
        self.observer = PausingObserver()
        self.observer.schedule(my_event_handler, folder_to_watch,
                               recursive=True)
        self.previous_diff = None

    def start(self):
        self.observer.start()

    def stop(self):
        self.git_manager.add_all()
        self.git_manager.commit(f"Pause", allow_empty=True)
        self.git_manager.push(all=True)
        self.observer.stop()
        self.observer.join()
        self.git_manager.stash(all=True, message="g4s-auto")

        if getattr(sys, 'frozen', False):
            application_path = os.path.abspath(sys.executable)
        elif __file__:
            application_path = os.path.abspath(__file__)
        else:
            raise RuntimeError("For some unknown reason, the type of the currently executed file "
                               "is not recognized.")

        self.file_manager.delete_all(Path(self.folder_to_watch),
                                     [Path(self.folder_to_watch) / ".git/",
                                      Path(self.folder_to_watch) / ".settings.yml",
                                      Path(application_path)])

    def on_created(self, event):
        src_path = Path(event.src_path)
        is_diff_empty = self.__is_diff_empty(src_path)
        current_diff = self.git_manager.get_diff()
        if current_diff == self.previous_diff:
            self.__save([src_path], f"[auto] {src_path.name} has been modified", amend=True)
        elif not is_diff_empty:
            self.__save([src_path], f"[auto] {src_path.name} has been created")
        self.__reset_flags()

    def on_deleted(self, event):
        src_path = Path(event.src_path)
        if not self.__is_diff_empty(src_path):
            self.previous_diff = self.git_manager.get_diff()
            self.__save([src_path], f"[auto] {src_path.name} has been deleted")

    def on_modified(self, event):
        src_path = Path(event.src_path)
        if not self.__is_diff_empty(src_path):
            self.__save([src_path], f"[auto] {src_path.name} has been modified")
        self.__reset_flags()

    def on_moved(self, event):
        src_path = Path(event.src_path)
        dest_path = Path(event.dest_path)
        if not self.__is_diff_empty(dest_path):
            if src_path.parent == dest_path.parent:
                message = f"[auto] {src_path.name} has been renamed into {dest_path.name}"
            else:
                message = f"[auto] {src_path.name} has been moved to {dest_path.parent}"
            self.__save([Path(event.src_path), Path(event.dest_path)], message)
        self.__reset_flags()

    def __save(self, raw_paths: any, message: str, amend=False):
        if "g4s-auto" not in self.git_manager.get_local_branches():
            self.git_manager.branch("g4s-auto")
        self.git_manager.reset("g4s-auto")
        [self.git_manager.add(Path(path)) for path in raw_paths]
        self.git_manager.commit(message, amend)
        self.git_manager.branch("g4s-auto", force=True)
        self.git_manager.reset("HEAD@{2}")

    def __reset_flags(self):
        self.previous_diff = None

    def __is_diff_empty(self, path: Path) -> bool:
        self.git_manager.add(Path(path), intent_to_add=True)
        return not self.git_manager.get_diff("g4s-auto")

    @contextlib.contextmanager
    def pause(self):
        self.observer.pause()
        yield
        self.observer.resume()
