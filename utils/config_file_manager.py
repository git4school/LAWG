from abc import ABC, abstractmethod
from pathlib import Path

import yaml

from . import verify_path
from .constant import CONFIG_FILE_NAME
from .file_manager import FileManagerInterface


class Config:
    def __init__(self):
        self._repo_path = None
        self._ssh_path = None
        self._questions = None
        self._groups = None
        self._pat = None

    @property
    def pat(self):
        return self._pat

    @pat.setter
    def pat(self, value):
        self._pat = value

    @property
    def groups(self):
        return self._groups

    @groups.setter
    def groups(self, value):
        self._groups = value

    @property
    def repo_path(self):
        return str(self._repo_path)

    @repo_path.setter
    def repo_path(self, value):
        path = verify_path(value)
        self._repo_path = path.resolve(strict=True)

    @property
    def questions(self):
        return self._questions

    @questions.setter
    def questions(self, value):
        self._questions = value

    @property
    def ssh_path(self):
        return str(self._ssh_path)

    @ssh_path.setter
    def ssh_path(self, value):
        path = verify_path(value)
        self._ssh_path = path.resolve(strict=True)


class ConfigFileManagerInterface(ABC):
    def __init__(self, file_manager: FileManagerInterface):
        self.config = Config()
        self.file_manager = file_manager

    @abstractmethod
    def load(self, path) -> Config:
        """
        Reads the config file.
        param path:
        :return: the config parameters
        """
        pass

    @abstractmethod
    def create_config_file(self):
        """
        Creates the config file.
        """
        pass

    @property
    def groups(self):
        return self.config.groups

    @groups.setter
    def groups(self, value):
        self.config.groups = value

    @property
    def repo_path(self):
        return str(self.config.repo_path)

    @repo_path.setter
    def repo_path(self, value):
        path = verify_path(value)
        self.config.repo_path = path.resolve(strict=True)

    @property
    def questions(self):
        return self.config.questions

    @questions.setter
    def questions(self, value):
        self.config.questions = value

    @property
    def ssh_path(self):
        return str(self.config.ssh_path)

    @ssh_path.setter
    def ssh_path(self, value):
        path = verify_path(value)
        self.config.ssh_path = path.resolve(strict=True)

    @property
    def pat(self):
        return self.config.pat

    @pat.setter
    def pat(self, value):
        self.config.pat = value


class YAMLConfigFileManager(ConfigFileManagerInterface):
    def load(self, path):
        try:
            path = verify_path(path)
        except ValueError as ve:
            raise FileNotFoundError(ve)

        settings_file = open(path, "r")
        settings = yaml.load(settings_file, Loader=yaml.FullLoader)

        try:
            self.questions = settings["questions"]
            self.groups = settings["groups"]
        except KeyError as key:
            raise KeyError(f"{key} is missing from the settings file.")

        ssh_path = settings.get("ssh_path")
        pat = settings.get("pat")

        if ssh_path is not None:
            self.ssh_path = ssh_path
        else:
            if pat is not None:
                self.pat = pat
            else:
                raise KeyError(f"SSH key or PAT is missing from the settings file.")

        self.repo_path = settings.get("repo_path", ".")

        return self

    def create_config_file(self):
        data_template = {'ssh_path': str(Path.home() / '.ssh' / 'id_rsa'),
                         'questions': [],
                         'groups': []}
        with self.file_manager.open(CONFIG_FILE_NAME, 'w') as file:
            yaml.dump(data_template, file)
