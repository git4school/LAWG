from abc import ABC, abstractmethod
from pathlib import Path

import yaml

from . import verify_path


class SettingsFileReaderInterface(ABC):
    def __init__(self):
        self._repo_path = None
        self._ssh_path = None
        self._questions = None
        self._completed_questions = None
        self._groups = None
        self._cross_close = None

    @property
    def cross_close(self):
        return self._cross_close

    @cross_close.setter
    def cross_close(self, value):
        self._cross_close = value

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
    def completed_questions(self):
        return self._completed_questions

    @completed_questions.setter
    def completed_questions(self, value):
        self._completed_questions = value

    @property
    def ssh_path(self):
        return str(self._ssh_path)

    @ssh_path.setter
    def ssh_path(self, value):
        path = verify_path(value)
        self._ssh_path = path.resolve(strict=True)

    @abstractmethod
    def read(self, path):
        """
        Reads the settings file.
        param path:
        :return:
        """
        pass

    @abstractmethod
    def create_settings_file(self):
        """
        Creates the settings file.
        """
        pass

    @abstractmethod
    def complete_question(self, question):
        pass

    @abstractmethod
    def update_completed_questions(self):
        pass

    @abstractmethod
    def set_cross_close(self, value: bool):
        pass


class YAMLSettingsFileReader(SettingsFileReaderInterface):
    def read(self, path):
        try:
            path = verify_path(path)
        except ValueError as ve:
            raise FileNotFoundError(ve)

        settings_file = open(path, "r")
        settings = yaml.load(settings_file, Loader=yaml.FullLoader)

        try:
            self.repo_path = settings["repo_path"]
            self.ssh_path = settings["ssh_path"]
            self.questions = settings["questions"]
            self.groups = settings["groups"]
        except KeyError as key:
            raise KeyError(f"{key} is missing from the settings file.")

        self.completed_questions = settings.get("completed_questions", [])
        self.cross_close = settings.get("cross_close", False)

        return self

    def create_settings_file(self):
        data_template = {'repo_path': ".",
                         'ssh_path': str(Path.home() / '.ssh' / 'id_rsa'),
                         'questions': [],
                         'groups': []}
        with open('.settings.yml', 'w') as file:
            yaml.dump(data_template, file)

    def complete_question(self, question):
        if question in self.questions \
                and question not in self.completed_questions:
            self.completed_questions.append(question)

    def update_completed_questions(self):
        with open('.settings.yml') as file:
            settings = yaml.safe_load(file)

        settings['completed_questions'] = self.completed_questions

        with open('.settings.yml', 'w') as file:
            yaml.dump(settings, file)

    def set_cross_close(self, value: bool):
        self.cross_close = value
        with open('.settings.yml') as file:
            settings = yaml.safe_load(file)

        settings['cross_close'] = self.cross_close

        with open('.settings.yml', 'w') as file:
            yaml.dump(settings, file)