from abc import ABC, abstractmethod
from typing import List

from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.validation import Validator, ValidationError

from utils.command import CommandInterface, find_command


class CommandValidator(Validator):
    def __init__(self, commands: List[CommandInterface]):
        self.commands = commands

    def validate(self, document):
        command = find_command(document.text, self.commands)

        if command:
            command.validate(document.text)
        else:
            raise ValidationError(message='This command is unknown.')


class PromptInterface(ABC):
    def __init__(self, commands: List[CommandInterface], bottom_toolbar):
        self.commands = commands
        self.bottom_toolbar = bottom_toolbar

    @abstractmethod
    def prompt(self):
        pass


class PromptAutocomplete(PromptInterface):
    def prompt(self):
        commands_dict = {command: args for x in
                         self.commands for command, args in
                         x.command.items()}
        commands = NestedCompleter.from_nested_dict(commands_dict)
        command_str = prompt(
            "Type a command (use Tab for autocompletion): ",
            completer=commands,
            complete_while_typing=True,
            validator=CommandValidator(self.commands),
            bottom_toolbar=self.bottom_toolbar)
        command = find_command(command_str, self.commands)
        if command:
            command.execute(" ".join(command_str.split()[1:]))
