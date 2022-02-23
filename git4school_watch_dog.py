import time

from utils.file_watcher import FileWatcherWatchdog
from utils.settings_file_reader import YAMLSettingsFileReader, SettingsFileReaderInterface


def read_settings(settings_manager: SettingsFileReaderInterface):
    try:
        settings_manager.read(".settings.yml")
    except FileNotFoundError as e:
        settings_manager.create_settings_file()
        input(
            "The file '.settings.yml' was created. "
            "Please fill it with the correct data and press enter to continue.")
        read_settings(settings_manager)
    except ValueError as e:
        print(e)
        input("Please correct the path '.settings.yml' and press enter to continue.")
        read_settings(settings_manager)
    except KeyError as e:
        print(e)
        input(
            "Please fill the file '.settings.yml' with the correct data "
            "and press enter to continue.")
        read_settings(settings_manager)


if __name__ == "__main__":

    # folder_path = Path('..') / 'test-gitpython'
    # repo_path = Path('..') / 'test-gitpython'
    # ssh_path = Path.home() / '.ssh' / 'id_ed25519'

    # file_watcher = FileWatcherWatchdog(folder_path, repo_path, ssh_path)
    settings_file_reader = YAMLSettingsFileReader()
    read_settings(settings_file_reader)
    file_watcher = FileWatcherWatchdog(settings_file_reader.folder_path,
                                       settings_file_reader.repo_path,
                                       settings_file_reader.ssh_path)
    file_watcher.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        file_watcher.stop()
