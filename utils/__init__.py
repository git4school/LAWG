import os
import re
import typing
from pathlib import Path
from subprocess import call
from typing import Optional, Sequence

from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.layout import HSplit, D
from prompt_toolkit.shortcuts.dialogs import _create_app, _T
from prompt_toolkit.widgets import Dialog, Label, Button, TextArea, ValidationToolbar, RadioList


def verify_path(path: typing.Union[str, bytes, os.PathLike]) -> Path:
    """
    Ensures that the path exists.
    """
    path = Path(path)
    if not path.exists():
        raise ValueError(f"{path} does not exist.")
    return path


def generate_authenticated_repo_uri(token: str, remote_uri: str) -> str:
    repo_id = re.search(r"(?:https?://|git@)?github\.com[:/](.*?\.git)", remote_uri).group(1)
    return "https://" + token + "@github.com/" + repo_id


def get_missing_fields_in_dict(list: list[str], dict: dict[str, any]):
    return [field for field in list if field not in dict]


def find_stash_with_message(input_string, target_message):
    match = re.search(rf'stash@{{(\d+)}}: [^:]*: {target_message}', input_string)
    return f'stash@{{{match.group(1)}}}' if match else None


def clear_console():
    # check and make call for specific operating system
    _ = call('clear' if os.name == 'posix' else 'cls', shell=True)

def ok_dialog(
    title: AnyFormattedText = "",
    text: AnyFormattedText = "",
) -> Application[bool]:
    def accept(buf: Buffer) -> bool:
        get_app().layout.focus(ok_button)
        return True  # Keep text.

    def ok_handler() -> None:
        if len(textfield.text)>0:
            get_app().exit(result=textfield.text)

    ok_button = Button(text="Ok", handler=ok_handler)

    textfield = TextArea(
        multiline=False,
        accept_handler=accept,
    )

    dialog = Dialog(
        title=title,
        body=HSplit(
            [
                Label(text=text, dont_extend_height=True),
                textfield,
                ValidationToolbar(),
            ],
            padding=D(preferred=1, max=1),
        ),
        buttons=[ok_button],
        with_background=True,
    )

    return _create_app(dialog, None)


def radiolist_dialog(
    title: AnyFormattedText = "",
    text: AnyFormattedText = "",
    values: Optional[Sequence[tuple[_T, AnyFormattedText]]] = None,
    default: Optional[_T] = None,
) -> Application[_T]:
    if values is None:
        values = []

    def ok_handler() -> None:
        get_app().exit(result=radio_list.current_value)

    radio_list = RadioList(values=values, default=default)

    dialog = Dialog(
        title=title,
        body=HSplit(
            [Label(text=text, dont_extend_height=True), radio_list],
            padding=1,
        ),
        buttons=[
            Button(text="Ok", handler=ok_handler)
        ],
        with_background=True,
    )

    return _create_app(dialog, None)


class Object:
    def __init__(self, value):
        self.value = value
