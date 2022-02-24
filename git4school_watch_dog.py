from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter

from utils.file_watcher import FileWatcherWatchdog
from utils.settings_file_reader import YAMLSettingsFileReader, \
    SettingsFileReaderInterface


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
        input(
            "Please correct the path '.settings.yml' and press enter to continue.")
        read_settings(settings_manager)
    except KeyError as e:
        print(e)
        input(
            "Please fill the file '.settings.yml' with the correct data "
            "and press enter to continue.")
        read_settings(settings_manager)


def prompt_fix(questions: list):
    command = NestedCompleter.from_nested_dict({
        'fix': {
            '#1': None,
            '#2': None,
            '#3': None
        }
    })
    print(prompt(completer=command))


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
            prompt_fix(settings_file_reader.questions)
            # time.sleep(1)
    except KeyboardInterrupt:
        file_watcher.stop()
