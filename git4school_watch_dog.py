import os
import time

from utils.Watcher import FileWatcherWatchdog

if __name__ == "__main__":
    folder_path = os.path.join('..', 'test-gitpython', 'src')
    repo_path = os.path.join('..', 'test-gitpython')
    ssh_path = os.path.join(os.path.expanduser('~'), '.ssh', 'id_rsa')

    file_watcher = FileWatcherWatchdog(folder_path, repo_path, ssh_path)
    file_watcher.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Fin")
        file_watcher.stop()
