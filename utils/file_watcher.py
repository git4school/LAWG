from abc import ABC, abstractmethod
from pathlib import Path

from git import Repo, RemoteProgress
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers.polling import PollingObserver as Observer


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

    def start(self):
        self.observer.start()

    def stop(self):
        self.push()
        self.observer.stop()
        self.observer.join()

    def push(self):
        try:
            ssh_cmd = f'ssh -v -i {self.ssh_path}'
            with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                self.origin.push()  # progress=MyProgressPrinter())
                print("Pushed !")
        except Exception as e:
            print(e)

    def __init__(self, folder_to_watch, repo_path, ssh_path):
        self.repo = Repo(repo_path)
        self.ssh_path = ssh_path
        patterns = ["*"]
        ignore_patterns = ["*~", r"*\.git*"]
        ignore_directories = True
        case_sensitive = True
        my_event_handler = PatternMatchingEventHandler(patterns,
                                                       ignore_patterns,
                                                       ignore_directories,
                                                       case_sensitive)
        self.origin = self.repo.remote(name="origin")

        print(self.origin.url)

        my_event_handler.on_created = self.on_created
        my_event_handler.on_deleted = self.on_deleted
        my_event_handler.on_modified = self.on_modified
        my_event_handler.on_moved = self.on_moved
        self.observer = Observer()
        self.observer.schedule(my_event_handler, folder_to_watch,
                               recursive=True)

    def on_created(self, event):
        print(f"{event.src_path} has been created!")

    def on_deleted(self, event):
        print(f"Someone deleted {event.src_path}!")

    def on_modified(self, event):
        path = Path(event.src_path)
        self.repo.index.add([path.resolve()])
        self.repo.index.commit(
            f"Git4school auto-commit: {path.name} has been modified")

    def on_moved(self, event):
        print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")
