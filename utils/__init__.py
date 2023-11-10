import os
import re
import typing
from pathlib import Path
from subprocess import call


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
