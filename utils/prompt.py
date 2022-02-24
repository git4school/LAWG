import re
from abc import ABC, abstractmethod

from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.validation import Validator, ValidationError


class CommandValidator(Validator):
    def __init__(self, questions):
        self.questions = questions
        questions_regex = f"({'|'.join(self.questions)})"
        self.questions_regex = rf'fix *{questions_regex} *$'

    def validate(self, document):
        if not re.match(self.questions_regex, document.text):
            raise ValidationError(message='This command is unknown.')


class PromptInterface(ABC):
    def __init__(self, questions):
        self.questions = questions

    @abstractmethod
    def prompt(self):
        pass


class PromptAutocomplete(PromptInterface):
    def prompt(self):
        questions_dict = dict.fromkeys(self.questions, None)
        command = NestedCompleter.from_nested_dict({
            'fix': questions_dict
        })
        command = prompt("Entrez une commande (utilisez Tab pour l'autocomplétion) : ",
                         completer=command,
                         complete_while_typing=True,
                         validator=CommandValidator(self.questions))
