import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path


class FileManagerInterface(ABC):

    @abstractmethod
    def delete_all(self, folder_path: Path, ignore_paths):
        pass


class FileManagerGlob(FileManagerInterface):

    def delete_all(self, folder_path: Path, ignore_paths):
        for path in folder_path.glob("*"):
            if all((ignore_path not in path.parents and path != ignore_path) for ignore_path in
                   ignore_paths):
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    os.remove(path)
