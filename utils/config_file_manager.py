from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog

from . import verify_path, get_missing_fields_in_dict
from .constant import REPO_PATH
from .file_manager import FileManagerInterface


class Config:
    def __init__(self):
        self._repo_path = Path(REPO_PATH)
        self._ssh_path = None
        self._questions = None
        self._groups = None
        self._pat = None
        self._nickname = None

    @property
    def nickname(self):
        return self._nickname

    @nickname.setter
    def nickname(self, value):
        self._nickname = value

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
    def load_settings(self, config_path) -> Config:
        """
        Reads the config file.
        param config_path:
        :return: the config parameters
        """
        pass

    @abstractmethod
    def load_auth_settings(self, auth_config_path) -> Config:
        """
        Reads the auth config file.
        param auth_config_path:
        :return: the config parameters
        """
        pass

    @abstractmethod
    def create_auth_config_file(self):
        """
        Creates the config file for the student authentication
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

    @property
    def nickname(self):
        return self.config.nickname

    @nickname.setter
    def nickname(self, value):
        self.config.nickname = value


class YAMLConfigFileManager(ConfigFileManagerInterface):
    def load_settings(self, config_path):
        try:
            config_path = verify_path(config_path)
        except ValueError as ve:
            self.create_config_file(config_path)

        settings_file = open(config_path, "r")
        settings = yaml.load(settings_file, Loader=yaml.FullLoader)
        fields_list = ["questions", "groups"]
        missing_fields = get_missing_fields_in_dict(fields_list, settings)
        if missing_fields:
            raise KeyError(f"Following fields are missing from the settings file : {', '.join(missing_fields)}")
        else:
            self.questions = settings["questions"]
            self.groups = settings["groups"]

        settings_file.close()

        return self

    def load_auth_settings(self, auth_config_path):
        try:
            auth_config_path = verify_path(auth_config_path)
        except ValueError as ve:
            self.create_auth_config_file(auth_config_path)

        auth_settings_file = open(auth_config_path, "r")
        auth_settings = yaml.load(auth_settings_file, Loader=yaml.FullLoader)
        auth_settings_file.close()

        fields_list = ["ssh_path", "pat", "nickname"]
        missing_fields = get_missing_fields_in_dict(fields_list, auth_settings)
        if missing_fields:
            if "ssh_path" in missing_fields:
                if "pat" in missing_fields:
                    auth_mode = self.ask_authentication_mode()
                    if auth_mode == "pat":
                        auth_settings["pat"] = self.ask_pat()
                        if "nickname" in missing_fields:
                            auth_settings["nickname"] = self.ask_nickname()
                    elif auth_mode == "ssh":
                        auth_settings["ssh_path"] = self.ask_ssh_key()

            with self.file_manager.open(auth_config_path, 'w') as file:
                yaml.dump(auth_settings, file)

        if auth_settings.get("ssh_path"):
            self.ssh_path = auth_settings.get("ssh_path")
        else:
            self.pat = auth_settings.get("pat")
            self.nickname = auth_settings.get("nickname")

        return self

    def create_auth_config_file(self, path):
        data = {}

        with self.file_manager.open(path, 'w') as file:
            yaml.dump(data, file)

    def create_config_file(self, path):
        data = {'questions': [],
                'groups': []}
        with self.file_manager.open(path, 'w') as file:
            yaml.dump(data, file)

    def ask_nickname(self) -> str:
        nickname = input_dialog(
            title='Creation of the config file',
            text='Please enter your Github nickname: ').run()

        return nickname

    def ask_ssh_key(self) -> str:
        ssh_key = input_dialog(
            title='Creation of the config file',
            text='Please enter your ssh key path (absolute): ').run()

        return ssh_key

    def ask_pat(self) -> str:
        pat = input_dialog(
            title='Creation of the config file',
            text='Please enter your PAT: ').run()

        return pat

    def ask_authentication_mode(self) -> str:
        auth_mode = radiolist_dialog(
            title='Creation of the config file',
            text='What authentication mode do you want to use ?',
            values=[
                ('pat', 'Personal Access Token'),
                ('ssh', 'SSH key')
            ]
        ).run()

        return auth_mode

