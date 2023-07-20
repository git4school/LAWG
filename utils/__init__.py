import os
import re
import typing
from pathlib import Path


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
