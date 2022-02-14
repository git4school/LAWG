import time
from pathlib import Path

from utils.file_watcher import FileWatcherWatchdog

if __name__ == "__main__":
    folder_path = Path('..') / 'test-gitpython'
    repo_path = Path('..') / 'test-gitpython'
    ssh_path = Path.home() / '.ssh' / 'id_ed25519'

    file_watcher = FileWatcherWatchdog(folder_path, repo_path, ssh_path)
    file_watcher.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Fin")
        file_watcher.stop()
