import os
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
