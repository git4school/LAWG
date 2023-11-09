import re
from abc import ABC, abstractmethod
from sys import exit
from typing import Sequence

from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.layout import D, Float, VSplit, HSplit, HorizontalAlign
#from prompt_toolkit.shortcuts import checkboxlist_dialog
from prompt_toolkit.shortcuts.dialogs import _create_app, _T, radiolist_dialog
from prompt_toolkit.styles import BaseStyle
from prompt_toolkit.validation import ValidationError
from prompt_toolkit.widgets import TextArea, Dialog, Button, CheckboxList, Label

from utils.constant import AUTO_BRANCH, NO_FIX_LIMITATION
from utils.data_file_manager import DataFileManagerInterface
from utils.file_watcher import FileWatcherInterface
from utils.git_manager import GitManagerInterface
from utils.spinner import Spinner


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

    def execute(self, args):
        with Spinner():
            self._execute(args)

    @abstractmethod
    def _execute(self, args):
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


    def _execute(self, args):
        with self.file_watcher.pause():

            commit_message = f"Fix {args}"

            self.data_file_manager.complete_question(args)

            self.git_manager.duplicate_commit(commit_message, AUTO_BRANCH, allow_empty=True)
            self.file_watcher.last_message = commit_message
            get_app().invalidate()


class FixCommandOneBranch(FixCommand):
    def execute(self, args):
        perceived_difficulty = perceived_difficulty_dialog().run()
        perceived_emotions = perceived_emotions_dialog().run()
        arguments = {
            'question': args,
            'perceived_difficulty': perceived_difficulty,
            'perceived_emotions': perceived_emotions
        }
        super().execute(arguments)

    def _execute(self, args):
        with self.file_watcher.pause():
            commit_message = f"Fix {args['question']}\nD={args['perceived_difficulty']}\nE={args['perceived_emotions']}"
            self.data_file_manager.complete_question(args)
            self.git_manager.add_all()
            self.git_manager.commit(commit_message, allow_empty=True)
            self.git_manager.push(all=True)
            self.file_watcher.last_message = commit_message
            get_app().invalidate()


class ExitCommand(CommandInterface):
    def __init__(self, file_watcher: FileWatcherInterface):
        self.file_watcher = file_watcher
        regex = rf'(exit|quit) *$'
        command = {
            'exit': None,
            'quit': None
        }
        super().__init__(command, regex)

    def _execute(self, args):
        # self.file_watcher.stop()
        exit()


def perceived_emotions_dialog() -> Application[list[_T]]:

    dialog = Dialog(
        title="Émotions perçues",
        body=HSplit(
            [
                Label(text="Quelle(s) émotion(s) avez-vous ressenties ?", dont_extend_height=True),
                VSplit(
                    [
                        Button(text="\U0001F641\U0001F641\U0001F641", handler=likert1, left_symbol="", right_symbol=""),
                        Button(text="\U0001F641\U0001F641", handler=likert2, left_symbol="", right_symbol=""),
                        Button(text="\U0001F641", handler=likert3, left_symbol="", right_symbol=""),
                        Button(text="\U0001F610", handler=likert4, left_symbol="", right_symbol=""),
                        Button(text="\U0001F603", handler=likert5, left_symbol="", right_symbol=""),
                        Button(text="\U0001F603\U0001F603", handler=likert6, left_symbol="", right_symbol=""),
                        Button(text="\U0001F603\U0001F603\U0001F603", handler=likert7, left_symbol="", right_symbol="")
                    ],
                    padding=1,
                    align=HorizontalAlign.CENTER,
                    padding_char="|"
                )

            ],
            padding=1,
        ),
        with_background=True,
    )

    return _create_app(dialog, None)


def perceived_difficulty_dialog() -> Application[list[_T]]:
    title = "Difficulté perçue"
    text = "Indiquez à quel point vous êtes d'accord avec l'affirmation suivante (1: Pas du tout d'accord, 7: Totalement d'accord) :\n\"J'ai trouvé cette tâche difficile.\""

    dialog = Dialog(
        title=title,
        body=HSplit(
            [
                Label(text=text, dont_extend_height=True),
                VSplit(
                    [
                        Button(text="1", handler=likert1, left_symbol="", right_symbol=""),
                        Button(text="2", handler=likert2, left_symbol="", right_symbol=""),
                        Button(text="3", handler=likert3, left_symbol="", right_symbol=""),
                        Button(text="4", handler=likert4, left_symbol="", right_symbol=""),
                        Button(text="5", handler=likert5, left_symbol="", right_symbol=""),
                        Button(text="6", handler=likert6, left_symbol="", right_symbol=""),
                        Button(text="7", handler=likert7, left_symbol="", right_symbol="")
                    ],
                    padding=1,
                    align=HorizontalAlign.CENTER,
                    padding_char="|"
                )
            ],
            padding=1,
        ),
        with_background=True,
    )

    return _create_app(dialog, None)


def likert1():
    get_app().exit(result=1)


def likert2():
    get_app().exit(result=2)


def likert3():
    get_app().exit(result=3)


def likert4():
    get_app().exit(result=4)


def likert5():
    get_app().exit(result=5)


def likert6():
    get_app().exit(result=6)


def likert7():
    get_app().exit(result=7)



def happy():
    return get_app().exit(result="happy")

def sad():
    return get_app().exit(result="sad")

def neutral():
    return get_app().exit(result="neutral")
