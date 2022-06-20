import atexit
from pathlib import Path
from typing import List

from utils.command import FixCommand, CommandInterface, ExitCommand
from utils.file_watcher import FileWatcherWatchdog, FileWatcherInterface
from utils.git_manager import GitManagerPython, GitManagerInterface
from utils.prompt import PromptAutocomplete
from utils.readme_creator import IdentityCreatorDialog
from utils.settings_file_reader import YAMLSettingsFileReader, \
    SettingsFileReaderInterface


def exit_handler():
    file_watcher.stop()


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


def get_commands_list(questions: List[str],
                      file_watcher_manager: FileWatcherInterface,
                      git_service: GitManagerInterface,
                      setting_file_reader: SettingsFileReaderInterface) \
        -> List[CommandInterface]:
    fix_command = FixCommand(questions, git_service, setting_file_reader,
                             file_watcher_manager)
    exit_command = ExitCommand(file_watcher_manager)
    return [fix_command, exit_command]


def update_gitignore(gitignore_path: Path) -> None:
    exe_wildcard = "git4school_watch_dog*"
    with open(gitignore_path, "a+") as gitignore_file:
        gitignore_file.seek(0)
        if exe_wildcard not in gitignore_file.read():
            gitignore_file.write(f"\n{exe_wildcard}")


if __name__ == "__main__":
    settings_file_reader = YAMLSettingsFileReader()
    read_settings_until_correct(settings_file_reader)
    git_manager = GitManagerPython(settings_file_reader.repo_path,
                                   settings_file_reader.ssh_path)
    file_watcher = FileWatcherWatchdog(settings_file_reader.folder_path,
                                       git_manager)
    identity_creator = IdentityCreatorDialog()

    update_gitignore(Path(settings_file_reader.repo_path) / ".gitignore")

    identity_creator.create_identity_file(settings_file_reader.repo_path,
                                          settings_file_reader.groups)

    if not settings_file_reader.no_watcher:
        print("Démarrage de l'observateur ...")
        file_watcher.start()
        atexit.register(exit_handler)

    commands = get_commands_list(settings_file_reader.questions, file_watcher,
                                 git_manager, settings_file_reader)
    command_prompt = PromptAutocomplete(commands)

    try:
        while True:
            command_prompt.prompt()
    except KeyboardInterrupt:
        pass
