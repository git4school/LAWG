import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TextIO

import yaml


class FileManagerInterface(ABC):
    # @abstractmethod
    # def create(self, path: Path, data):
    #     pass

    @abstractmethod
    def delete_file(self, file_path: Path):
        pass

    @abstractmethod
    def delete_folder(self, folder_path: Path):
        pass

    @abstractmethod
    def delete_all(self, repo_path: Path, ignore_paths):
        pass

    @abstractmethod
    def open(self, path: Path, mode: str = "r"):
        pass

    @abstractmethod
    def file_exists(self, path: Path):
        pass


class FileManagerGlob(FileManagerInterface):

    def file_exists(self, path: Path):
        return path.is_file()

    def delete_folder(self, folder_path: Path):
        shutil.rmtree(folder_path)

    # def create(self, path: Path, data):
    #     with open(path, 'w') as file:
    #         yaml.dump(data, file)

    def delete_file(self, path: Path):
        os.remove(path)

    def delete_all(self, repo_path: Path, ignore_paths):
        for path in repo_path.glob("*"):
            if all((ignore_path not in path.parents and path != ignore_path) for ignore_path in
                   ignore_paths):
                if path.is_dir():
                    self.delete_folder(path)
                else:
                    self.delete_file(path)

    def open(self, path: Path, mode="r"):
        return open(path, mode)


