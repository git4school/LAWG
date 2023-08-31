import atexit
import os
import sys
from pathlib import Path
from typing import List

from git import GitCommandError

from utils.command import FixCommand, ExitCommand, CommandInterface
from utils.constant import NO_WATCHER, NO_SESSION_CLOSURE, AUTO_BRANCH, CONFIG_FILE_NAME, DATA_FILE_NAME, \
    IDENTITY_FILE_NAME
from utils.data_file_manager import PickleDataFileManager, DataFileManagerInterface
from utils.file_manager import FileManagerGlob
from utils.file_watcher import FileWatcherWatchdog, FileWatcherInterface
from utils.git_manager import GitManagerPython, GitManagerInterface
from utils.prompt import PromptAutocomplete
from utils.identity_file_manager import IdentityCreatorDialog
from utils.config_file_manager import YAMLConfigFileManager, \
    ConfigFileManagerInterface


def open_session(git_manager: GitManagerInterface, __file__, data_file_manager: DataFileManagerInterface):
    cross_close = data_file_manager.cross_close

    if not cross_close:
        git_manager.reset("HEAD", hard=True)

    try:
        git_manager.stash(pop=True)
    except GitCommandError as stash_error:
        print("No stash found!")

    try:
        code = git_manager.pull()
    except GitCommandError as pull_error:
        print("An error as occurred when pulling, aborting the merge...")
        git_manager.merge(abort=True)
        print("The program will be stop, please contact your supervisor to handle the problem manually.")
        raise

    commit_message = f"Resume"
    git_manager.duplicate_commit(commit_message, AUTO_BRANCH, allow_empty=True)
    data_file_manager.set_cross_close(True)


def close_session(git_manager: GitManagerInterface, file_manager: FileManagerGlob, folder_to_watch, __file__, data_file_manager: DataFileManagerInterface):
    commit_message = f"Pause"
    git_manager.duplicate_commit(commit_message, AUTO_BRANCH, allow_empty=True)

    if not NO_SESSION_CLOSURE:
        git_manager.stash(all=True, message=AUTO_BRANCH)

        if getattr(sys, 'frozen', False):
            application_path = Path(sys.executable)
        elif __file__:
            application_path = Path(__file__)
        else:
            raise RuntimeError("For some unknown reason, the type of the currently executed file "
                               "is not recognized.")

        file_manager.delete_all(Path(folder_to_watch), [Path(folder_to_watch) / ".git/",
                                                        Path(folder_to_watch) / CONFIG_FILE_NAME,
                                                        Path(folder_to_watch) / DATA_FILE_NAME,
                                                        Path(folder_to_watch) / IDENTITY_FILE_NAME,
                                                        Path(application_path)])

    data_file_manager.set_cross_close(False)


def exit_script(git_manager: GitManagerInterface, file_watcher: FileWatcherInterface, file_manager: FileManagerGlob, folder_to_watch, __file__, data_file_manager: DataFileManagerInterface):
    file_watcher.stop()
    close_session(git_manager, file_manager, folder_to_watch, __file__, data_file_manager)


def exit_handler(git_manager: GitManagerInterface, file_watcher: FileWatcherInterface, file_manager: FileManagerGlob, folder_to_watch, __file__, data_file_manager: DataFileManagerInterface):
    exit_script(git_manager, file_watcher, file_manager, folder_to_watch, __file__, data_file_manager)


def read_settings_until_correct(config_file_manager: ConfigFileManagerInterface):
    try:
        config_file_manager.load(CONFIG_FILE_NAME)
    except FileNotFoundError as e:
        config_file_manager.create_config_file()
        # input(
        #     f"The file '{CONFIG_FILE_NAME}' was created. "
        #     "Please fill it with the correct data and press enter to continue.")
        read_settings_until_correct(config_file_manager)
    except ValueError as e:
        print(e)
        input(
            f"Please correct the path '{CONFIG_FILE_NAME}' and press enter to continue.")
        read_settings_until_correct(config_file_manager)
    except KeyError as e:
        print(e)
        input(
            f"Please fill the file '{CONFIG_FILE_NAME}' with the correct data "
            "and press enter to continue.")
        read_settings_until_correct(config_file_manager)


def get_commands_list(questions: List[str],
                      file_watcher_manager: FileWatcherInterface,
                      git_service: GitManagerInterface,
                      data_file_manager: DataFileManagerInterface) \
        -> List[CommandInterface]:
    fix_command = FixCommand(questions, git_service, data_file_manager,
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
    if getattr(sys, 'frozen', False):
        os.chdir(Path(sys.executable).parent)

    file_manager = FileManagerGlob()
    config = YAMLConfigFileManager(file_manager)
    identity_file_manager = IdentityCreatorDialog()

    read_settings_until_correct(config)

    data_file_manager = PickleDataFileManager(file_manager, Path(config.repo_path) / DATA_FILE_NAME, config.questions)
    git_manager = GitManagerPython(config.repo_path, config.ssh_path, config.nickname, config.pat)

    open_session(git_manager, __file__, data_file_manager)

    file_watcher = FileWatcherWatchdog(config.repo_path, git_manager, file_manager)

    #update_gitignore(Path(config.repo_path) / ".gitignore")

    identity_file_manager.create_identity_file(config.repo_path,
                                               config.groups)

    if not NO_WATCHER:
        print("Démarrage de l'observateur ...")
        file_watcher.start()

    atexit.register(exit_handler, git_manager, file_watcher, file_manager, config.repo_path, __file__, data_file_manager)

    commands = get_commands_list(config.questions, file_watcher, git_manager, data_file_manager)
    command_prompt = PromptAutocomplete(commands)

    try:
        while True:
            command_prompt.prompt()
    except KeyboardInterrupt:
        pass
