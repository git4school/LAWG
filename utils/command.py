import re
from abc import ABC, abstractmethod
from sys import exit

from prompt_toolkit.validation import ValidationError

from utils.constant import AUTO_BRANCH, NO_FIX_LIMITATION
from utils.data_file_manager import DataFileManagerInterface
from utils.file_watcher import FileWatcherInterface
from utils.git_manager import GitManagerInterface
from utils.config_file_manager import ConfigFileManagerInterface


def find_command(command_str, commands):
    if (not command_str) or (not command_str.strip()):
        return None

    commands_found = [command for command in commands for command_key in
                      command.command.keys() if
                      command_key == command_str.strip().split()[0]]

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
                 data_file_manager: DataFileManagerInterface,
                 file_watcher: FileWatcherInterface):
        self.questions = questions
        self.git_manager = git_manager
        self.data_file_manager = data_file_manager
        self.file_watcher = file_watcher
        questions_regex = f"({'|'.join(self.questions)})"
        regex = r'fix .*$' if NO_FIX_LIMITATION else rf'fix *{questions_regex} *$'

        questions_dict = dict.fromkeys(self.questions, None)
        command = {
            'fix': questions_dict
        }
        super().__init__(command, regex)

    def execute(self, args):
        with self.file_watcher.pause():
            commit_message = f"Fix {args}"

            self.data_file_manager.complete_question(args)

            self.git_manager.duplicate_commit(commit_message, AUTO_BRANCH, allow_empty=True)


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
