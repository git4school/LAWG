from typing import List

from git_manager import GitManagerPython
from prompt import PromptAutocomplete
from utils.command import FixCommand, CommandInterface, ExitCommand
from utils.file_watcher import FileWatcherWatchdog, FileWatcherInterface
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


def get_commands_list(questions: List[str], file_watcher_manager: FileWatcherInterface) \
        -> List[CommandInterface]:
    fix_command = FixCommand(questions)
    exit_command = ExitCommand(file_watcher_manager)
    return [fix_command, exit_command]


if __name__ == "__main__":
    settings_file_reader = YAMLSettingsFileReader()
    read_settings_until_correct(settings_file_reader)
    git_manager = GitManagerPython(settings_file_reader.repo_path, settings_file_reader.ssh_path)
    file_watcher = FileWatcherWatchdog(settings_file_reader.folder_path, git_manager)
    file_watcher.start()

    commands = get_commands_list(settings_file_reader.questions, file_watcher)
    command_prompt = PromptAutocomplete(commands)

    try:
        while True:
            command_prompt.prompt()
    except KeyboardInterrupt:
        print("stop")
        file_watcher.stop()
