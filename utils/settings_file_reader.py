from abc import ABC, abstractmethod
from pathlib import Path


def verify_path(path: str) -> Path:
    """
    Verifies that the path exists.
    """
    path = Path(path)
    if not path.exists():
        raise ValueError(f"{path} does not exist.")
    return path


class SettingsFileReaderInterface(ABC):
    def __init__(self):
        self._folder_path = ""
        self._repo_path = ""
        self._ssh_path = ""

    @abstractmethod
    def read(self, path):
        pass

    @property
    def folder_path(self):
        return self._folder_path

    @folder_path.setter
    def folder_path(self, value):
        path = verify_path(value)
        self._folder_path = path.resolve()

    @property
    def repo_path(self):
        return self._repo_path

    @repo_path.setter
    def repo_path(self, value):
        path = verify_path(value)
        self._repo_path = path.resolve()

    @property
    def ssh_path(self):
        return self._ssh_path

    @ssh_path.setter
    def ssh_path(self, value):
        path = verify_path(value)
        self._ssh_path = path.resolve()


class YAMLSettingsFileReader(SettingsFileReaderInterface):
    def read(self, path):
        pass
