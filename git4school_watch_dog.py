from prompt import PromptAutocomplete
from utils.file_watcher import FileWatcherWatchdog
from utils.settings_file_reader import YAMLSettingsFileReader, \
    SettingsFileReaderInterface


def read_settings_until_correct(settings_manager: SettingsFileReaderInterface):
    try:
        settings_manager.read(".settings.yml")
    except FileNotFoundError as e:
        settings_manager.create_settings_file()
        input(
            "The file '.settings.yml' was created. "
            "Please fill it with the correct data and press enter to continue.")
        read_settings_until_correct(settings_manager)
    except ValueError as e:
        print(e)
        input(
            "Please correct the path '.settings.yml' and press enter to continue.")
        read_settings_until_correct(settings_manager)
    except KeyError as e:
        print(e)
        input(
            "Please fill the file '.settings.yml' with the correct data "
            "and press enter to continue.")
        read_settings_until_correct(settings_manager)


if __name__ == "__main__":
    settings_file_reader = YAMLSettingsFileReader()
    read_settings_until_correct(settings_file_reader)
    file_watcher = FileWatcherWatchdog(settings_file_reader.folder_path,
                                       settings_file_reader.repo_path,
                                       settings_file_reader.ssh_path)
    file_watcher.start()

    command_prompt = PromptAutocomplete(settings_file_reader.questions)

    try:
        while True:
            command_prompt.prompt()
    except KeyboardInterrupt:
        print("stop")
        file_watcher.stop()
