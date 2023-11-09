import atexit
import os
import sys
from pathlib import Path
from typing import List

from git import GitCommandError
from prompt_toolkit import HTML

from utils import find_stash_with_message, clear_console
from utils.command import FixCommand, ExitCommand, CommandInterface, FixCommandOneBranch
from utils.constant import NO_WATCHER, NO_SESSION_CLOSURE, AUTO_BRANCH, CONFIG_FILE_NAME, DATA_FILE_NAME, \
    IDENTITY_FILE_NAME, AUTH_CONFIG_FILE_NAME, NO_AUTO_BRANCH
from utils.data_file_manager import PickleDataFileManager, DataFileManagerInterface
from utils.file_manager import FileManagerGlob
from utils.file_watcher import FileWatcherWatchdog, FileWatcherInterface, FileWatcherWatchdogOneBranch
from utils.git_manager import GitManagerPython, GitManagerInterface
from utils.prompt import PromptAutocomplete
from utils.identity_file_manager import IdentityCreatorDialog
from utils.config_file_manager import YAMLConfigFileManager, \
    ConfigFileManagerInterface


def stash_untracked_files(git_manager: GitManagerInterface, auth_file_path: str):
    try:
        git_manager.add(auth_file_path, force=True)
        git_manager.stash(target=auth_file_path, message="auth")
        git_manager.stash(all=True, message="auto")
    except GitCommandError as stash_error:
        pass


def restore_auth_file(git_manager: GitManagerInterface, auth_file_path: str):
    try:
        stash_list = git_manager.stash(command="list")
        auth_stash = find_stash_with_message(stash_list, "auth")
        if auth_stash:
            git_manager.stash(command="pop", target=auth_stash)
            git_manager.restore(auth_file_path, staged=True)
    except GitCommandError as stash_error:
        pass


def restore_all_untracked_files(git_manager: GitManagerInterface):
    try:
        stash_list = git_manager.stash(command="list")
        auto_stash = find_stash_with_message(stash_list, "auto")
        if auto_stash:
            git_manager.stash(command="pop", target=auto_stash)
    except GitCommandError as stash_error:
        pass


def open_session(git_manager: GitManagerInterface, __file__, data_file_manager: DataFileManagerInterface):
    cross_close = data_file_manager.cross_close

    if not cross_close:
        git_manager.reset("HEAD", hard=True)

    restore_all_untracked_files(git_manager)

    try:
        code = git_manager.pull()
    except GitCommandError as pull_error:
        print("An error as occurred when pulling, aborting the merge...")
        git_manager.merge(abort=True)
        print("The program will be stop, please contact your supervisor to handle the problem manually.")
        raise

    update_gitignore(Path(config.repo_path) / ".gitignore")
    commit_message = f"Resume"
    if NO_AUTO_BRANCH:
        git_manager.add_all()
        git_manager.commit(commit_message, allow_empty=True)
        git_manager.push(all=True)
    else:
        git_manager.duplicate_commit(commit_message, AUTO_BRANCH, allow_empty=True)
    data_file_manager.set_cross_close(True)


def close_session(git_manager: GitManagerInterface, file_manager: FileManagerGlob, folder_to_watch, __file__, data_file_manager: DataFileManagerInterface):
    commit_message = f"Pause"
    if NO_AUTO_BRANCH:
        git_manager.add_all()
        git_manager.commit(commit_message, allow_empty=True)
        git_manager.push(all=True)
    else:
        git_manager.duplicate_commit(commit_message, AUTO_BRANCH, allow_empty=True)

    if not NO_SESSION_CLOSURE:
        auth_file_path = str((Path(folder_to_watch)/AUTH_CONFIG_FILE_NAME).relative_to(folder_to_watch))
        stash_untracked_files(git_manager, auth_file_path)

        if getattr(sys, 'frozen', False):
            application_path = Path(sys.executable).relative_to(Path(folder_to_watch).absolute())
        elif __file__:
            application_path = Path(__file__)
        else:
            raise RuntimeError("For some unknown reason, the type of the currently executed file "
                               "is not recognized.")

        file_manager.delete_all(Path(folder_to_watch), [Path(folder_to_watch) / ".git/",
                                                        Path(folder_to_watch) / CONFIG_FILE_NAME,
                                                        Path(folder_to_watch) / AUTH_CONFIG_FILE_NAME,
                                                        Path(folder_to_watch) / DATA_FILE_NAME,
                                                        Path(folder_to_watch) / IDENTITY_FILE_NAME,
                                                        Path(folder_to_watch) / ".gitignore",
                                                        Path(application_path)])

    data_file_manager.set_cross_close(False)


def exit_script(git_manager: GitManagerInterface, file_watcher: FileWatcherInterface, file_manager: FileManagerGlob, folder_to_watch, __file__, data_file_manager: DataFileManagerInterface):
    file_watcher.stop()
    close_session(git_manager, file_manager, folder_to_watch, __file__, data_file_manager)


def exit_handler(git_manager: GitManagerInterface, file_watcher: FileWatcherInterface, file_manager: FileManagerGlob, folder_to_watch, __file__, data_file_manager: DataFileManagerInterface):
    exit_script(git_manager, file_watcher, file_manager, folder_to_watch, __file__, data_file_manager)


def read_settings(config_file_manager: ConfigFileManagerInterface):
    try:
        config_file_manager.load_settings(CONFIG_FILE_NAME)
    except ValueError as e:
        print(e)
        input(
            f"Please correct the path '{CONFIG_FILE_NAME}' and press enter to continue.")
        read_settings(config_file_manager)
    except KeyError as e:
        print(e)
        input(
            f"Please fill the file '{CONFIG_FILE_NAME}' with the correct data "
            "and press enter to continue.")
        read_settings(config_file_manager)


def read_auth_settings(config_file_manager: ConfigFileManagerInterface):
    config_file_manager.load_auth_settings(AUTH_CONFIG_FILE_NAME)


def get_commands_list(questions: List[str],
                      file_watcher_manager: FileWatcherInterface,
                      git_service: GitManagerInterface,
                      data_file_manager: DataFileManagerInterface) \
        -> List[CommandInterface]:
    fix_command = FixCommandOneBranch(questions, git_service, data_file_manager, file_watcher_manager) \
            if NO_AUTO_BRANCH else FixCommand(questions, git_service, data_file_manager, file_watcher_manager)
    exit_command = ExitCommand(file_watcher_manager)
    return [fix_command, exit_command]


def update_gitignore(gitignore_path: Path) -> None:
    wildcard = ".settings.auth.yml"
    with open(gitignore_path, "a+") as gitignore_file:
        gitignore_file.seek(0)
        if wildcard not in gitignore_file.read():
            gitignore_file.write(f"\n{wildcard}")


def bottom_toolbar():
    event = file_watcher.last_message.partition("\n")[0]
    return HTML(f'Last event: {event}')


if __name__ == "__main__":
    clear_console()
    if getattr(sys, 'frozen', False):
        os.chdir(Path(sys.executable).parent)

    last_message = ""

    file_manager = FileManagerGlob()
    config = YAMLConfigFileManager(file_manager)
    identity_file_manager = IdentityCreatorDialog()

    read_settings(config)
    git_manager = GitManagerPython(config.repo_path, config.ssh_path, config.nickname, config.pat)

    auth_file_path_str = str((Path(config.repo_path) / AUTH_CONFIG_FILE_NAME).relative_to(config.repo_path))
    restore_auth_file(git_manager, auth_file_path_str)

    read_auth_settings(config)
    data_file_manager = PickleDataFileManager(file_manager, Path(config.repo_path) / DATA_FILE_NAME, config.questions)
    identity_file_manager.create_identity_file(config.repo_path, config.groups)

    open_session(git_manager, __file__, data_file_manager)

    if NO_AUTO_BRANCH:
        file_watcher = FileWatcherWatchdogOneBranch(config.repo_path, git_manager, file_manager)
    else:
        file_watcher = FileWatcherWatchdog(config.repo_path, git_manager, file_manager)

    if not NO_WATCHER:
        print("Starting observer ...")
        file_watcher.start()

    atexit.register(exit_handler, git_manager, file_watcher, file_manager, config.repo_path, __file__, data_file_manager)

    commands = get_commands_list(config.questions, file_watcher, git_manager, data_file_manager)
    command_prompt = PromptAutocomplete(commands, bottom_toolbar)

    file = open(".variables.dat", "w")

    try:
        while True:
            clear_console()
            command_prompt.prompt()
    except KeyboardInterrupt:
        pass
