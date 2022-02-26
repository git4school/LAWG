import re
from abc import ABC, abstractmethod

from prompt_toolkit.validation import ValidationError

from utils.file_watcher import FileWatcherInterface


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
    def __init__(self, questions):
        self.questions = questions
        questions_regex = f"({'|'.join(self.questions)})"
        regex = rf'fix *{questions_regex} *$'

        questions_dict = dict.fromkeys(self.questions, None)
        command = {
            'fix': questions_dict
        }
        super().__init__(command, regex)

    def execute(self, args):
        print("fix command executed")


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
        self.file_watcher.stop()
