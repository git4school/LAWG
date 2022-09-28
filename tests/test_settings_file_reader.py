import pytest

from utils.settings_file_reader import YAMLSettingsFileReader


@pytest.fixture
def yaml_sfr():
    return YAMLSettingsFileReader()


def test_set_valid_repo_path(yaml_sfr):
    yaml_sfr.repo_path = "./README.md"


def test_set_invalid_repo_path(yaml_sfr):
    with pytest.raises(ValueError):
        yaml_sfr.repo_path = "5:/ert/trgr/tgez/README.md"
