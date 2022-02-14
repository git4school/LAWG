import pytest

from utils.settings_file_reader import YAMLSettingsFileReader


@pytest.fixture
def yaml_sfr():
    return YAMLSettingsFileReader()


def test_set_valid_folder_path(yaml_sfr):
    yaml_sfr.folder_path = "./README.md"


def test_set_invalid_folder_path(yaml_sfr):
    with pytest.raises(ValueError):
        yaml_sfr.folder_path = "C:/ert/trgr/tgez/README.md"
