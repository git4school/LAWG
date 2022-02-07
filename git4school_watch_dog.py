import time
import os
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from git import Repo

def on_created(event):
    print(f"{event.src_path} has been created!")


def on_deleted(event):
    print(f"Someone deleted {event.src_path}!")


def on_modified(event):
    print(f"{event.src_path} has been modified, git-committed !")
    repo.index.add([event.src_path])
    repo.index.commit(f"Git4school auto-commit: {os.path.basename(event.src_path)} has been modified")


def on_moved(event):
    print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")

if __name__ == "__main__":
    repo = Repo(".")
    patterns = ["*"]
    ignore_patterns = ["*~"]
    ignore_directories = True
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved

    path = "./src"
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)

    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Fin")
        my_observer.stop()
        my_observer.join()


