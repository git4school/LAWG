import re
from abc import ABC, abstractmethod
from sys import exit

from prompt_toolkit.validation import ValidationError

from utils.file_watcher import FileWatcherInterface
from utils.git_manager import GitManagerInterface
from utils.settings_file_reader import SettingsFileReaderInterface


def find_command(command_str, commands):
    commands_found = [command for command in commands for command_key in
                      command.command.keys() if
                      command_key == command_str.split()[0]] \
        if command_str else None
    return commands_found[0] if commands_found else None


class CommandInterface(ABC):
    @abstractmethod
    def __init__(self, command, regex):
        self.command = command
        self.regex = regex

    def validate(self, args):
        if not re.match(self.regex, args):
            raise ValidationError(message='This command is unknown.')

    @abstractmethod
    def execute(self, args):
        pass


class FixCommand(CommandInterface):
    def __init__(self, questions,
                 git_manager: GitManagerInterface,
                 setting_file_reader: SettingsFileReaderInterface,
                 file_watcher: FileWatcherInterface):
        self.questions = questions
        self.git_manager = git_manager
        self.setting_file_reader = setting_file_reader
        self.file_watcher = file_watcher
        questions_regex = f"({'|'.join(self.questions)})"
        regex = rf'fix *{questions_regex} *$'

        questions_dict = dict.fromkeys(self.questions, None)
        command = {
            'fix': questions_dict
        }
        super().__init__(command, regex)

    def execute(self, args):
        with self.file_watcher.pause():
            self.setting_file_reader.complete_question(args)
            self.setting_file_reader.update_completed_questions()
            self.git_manager.add_all()
            self.git_manager.commit(f"Fix {args}")
            self.git_manager.push()


class ExitCommand(CommandInterface):
    def __init__(self, file_watcher: FileWatcherInterface):
        self.file_watcher = file_watcher
        regex = rf'(exit|quit) *$'
        command = {
            'exit': None,
            'quit': None
        }
        super().__init__(command, regex)

    def execute(self, args):
        # self.file_watcher.stop()
        exit()
