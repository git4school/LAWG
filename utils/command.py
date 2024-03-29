import re
from abc import ABC, abstractmethod
from sys import exit

from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.layout import VSplit, HSplit, HorizontalAlign
from prompt_toolkit.shortcuts.dialogs import _create_app, _T, yes_no_dialog
from prompt_toolkit.validation import ValidationError
from prompt_toolkit.widgets import Dialog, Button, Label

from utils import Object
from utils.constant import AUTO_BRANCH, NO_FIX_LIMITATION, NO_AUTO_BRANCH
from utils.data_file_manager import DataFileManagerInterface
from utils.file_manager import FileManagerGlob
from utils.file_watcher import FileWatcherInterface
from utils.git_manager import GitManagerInterface
from utils.session_manager import SessionManagerInterface
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


class FinishCommand(CommandInterface):
    def __init__(self, git_manager: GitManagerInterface):
        self.git_manager = git_manager
        regex = r'finish'
        command = {
            'finish': None
        }
        super().__init__(command, regex)

    def execute(self, args):
        response = yes_no_dialog(
            title='Finish work',
            text='Do you confirm you want to conclude your work and tag "v1.0.0"?').run()
        if response:
            super().execute(args)

    def _execute(self, args):
        commit_message = f"Finish"
        if NO_AUTO_BRANCH:
            self.git_manager.add_all()
            self.git_manager.commit(commit_message, allow_empty=True)
            self.git_manager.tag("v1.0.0")
            self.git_manager.push(all=True)
            self.git_manager.push(tags=True)
        else:
            self.git_manager.duplicate_commit(commit_message, AUTO_BRANCH, allow_empty=True)
        exit()


class ExitCommand(CommandInterface):
    def __init__(self, file_watcher: FileWatcherInterface, session_manager: SessionManagerInterface, repo_path,
                 __file__):
        self.file_watcher = file_watcher
        self.session_manager = session_manager
        self.repo_path = repo_path
        self.__file__ = __file__
        regex = rf'(exit|quit) *$'
        command = {
            'quit': None
        }
        super().__init__(command, regex)

    def _execute(self, args):
        # self.file_watcher.stop()
        self.session_manager.close_session(self.repo_path, self.__file__)
        exit()


def perceived_emotions_dialog() -> Application[list[_T]]:
    return likert_dialog("Émotions perçues", "Durant la réalisation de la tâche, j'ai ressenti des émotions "
                                             "positives. (1: Pas du tout d'accord, 7: Totalement d'accord)")


def perceived_difficulty_dialog() -> Application[list[_T]]:
    return likert_dialog("Difficulté perçue",
                         "Indiquez à quel point vous êtes d'accord avec l'affirmation suivante (1: Pas "
                         "du tout d'accord, 7: Totalement d'accord) :\n\"J'ai trouvé cette tâche "
                         "difficile.\"")


def likert_dialog(title: str, text: str) -> Application[list[_T]]:
    selected = Object(1)

    class MyButtonLikert(ButtonLikert):
        def handler(self):
            self.focus()
            selected.value = self.value
            # get_app().exit(result=self.value)

    def handler_ok():
        get_app().exit(result=selected.value)

    dialog = Dialog(
        title=title,
        body=HSplit(
            [
                Label(text=text, dont_extend_height=True),
                VSplit(
                    [
                        MyButtonLikert(1),
                        MyButtonLikert(2),
                        MyButtonLikert(3),
                        MyButtonLikert(4),
                        MyButtonLikert(5),
                        MyButtonLikert(6),
                        MyButtonLikert(7),
                    ],
                    padding=1,
                    align=HorizontalAlign.CENTER,
                    padding_char="|"
                )
            ],
            padding=1,
        ),
        buttons=[Button(text="Ok", handler=handler_ok)],
        with_background=True,
    )

    return _create_app(dialog, None)


class ButtonLikert(Button):
    def __init__(self, value: str):
        self.value = value
        super().__init__(text=value, handler=self.handler, left_symbol="", right_symbol="")

    def handler(self):
        self.focus()

    def focus(self):
        get_app().layout.focus(self)
