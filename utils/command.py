import re
from abc import ABC, abstractmethod

from prompt_toolkit.validation import ValidationError

from file_watcher import FileWatcherInterface


class CommandInterface(ABC):
    @abstractmethod
    def __init__(self, command, regex):
        self.command = command
        self.regex = regex

    @abstractmethod
    def validate(self, args):
        pass

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

    def validate(self, args):
        if not re.match(self.regex, args):
            raise ValidationError(message='This command is unknown.')

    def execute(self, args):
        print("fix command executed")


class ExitCommand(CommandInterface):
    def __init__(self, file_watcher: FileWatcherInterface):
        self.file_watcher = file_watcher
        regex = rf'exit *$'
        command = {
            'exit': None
        }
        super().__init__(command, regex)

    def validate(self, args):
        if not re.match(self.regex, args):
            raise ValidationError(message='This command is unknown.')

    def execute(self, args):
        self.file_watcher.stop()
        print("exit command executed")
