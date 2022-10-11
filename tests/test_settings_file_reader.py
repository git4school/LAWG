import pytest

from utils.config_file_manager import YAMLConfigFileManager


@pytest.fixture
def yaml_sfr():
    return YAMLConfigFileManager()


def test_set_valid_repo_path(yaml_sfr):
    yaml_sfr.repo_path = "./README.md"


def test_set_invalid_repo_path(yaml_sfr):
    with pytest.raises(ValueError):
        yaml_sfr.repo_path = "5:/ert/trgr/tgez/README.md"
