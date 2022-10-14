import pytest

from utils.config_file_manager import YAMLConfigFileManager
from utils.file_manager import FileManagerGlob


@pytest.fixture
def yaml_sfr():
    fm = FileManagerGlob()
    return YAMLConfigFileManager(fm)


def test_set_valid_repo_path(yaml_sfr):
    yaml_sfr.repo_path = "./README.md"


def test_set_invalid_repo_path(yaml_sfr):
    with pytest.raises(ValueError):
        yaml_sfr.repo_path = "5:/ert/trgr/tgez/README.md"
