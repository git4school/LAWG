import atexit
import logging
import os
import signal
import sys
from functools import partial
from pathlib import Path
from typing import List

from git import GitCommandError
from prompt_toolkit import HTML
from prompt_toolkit.key_binding import bindings, KeyBindings
from prompt_toolkit.shortcuts import yes_no_dialog

from utils import find_stash_with_message, clear_console
from utils.command import FixCommand, ExitCommand, CommandInterface, FixCommandOneBranch, FinishCommand
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
from utils.session_manager import SessionManager, SessionManagerInterface

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
                      data_file_manager: DataFileManagerInterface,
                      session_manager: SessionManagerInterface,
                      repo_path,
                      __file__) -> List[CommandInterface]:
    fix_command = FixCommandOneBranch(questions, git_service, data_file_manager, file_watcher_manager) \
            if NO_AUTO_BRANCH else FixCommand(questions, git_service, data_file_manager, file_watcher_manager)
    finish_command = FinishCommand(git_service)
    exit_command = ExitCommand(file_watcher_manager, session_manager, repo_path, __file__)
    return [fix_command, finish_command, exit_command]


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

    data_file_manager = PickleDataFileManager(file_manager, Path(config.repo_path) / DATA_FILE_NAME, config.questions)
    identity_file_manager.create_identity_file(config.repo_path, config.groups)

    session_manager = SessionManager(git_manager, data_file_manager, file_manager)

    auth_file_path_str = str((Path(config.repo_path) / AUTH_CONFIG_FILE_NAME).relative_to(config.repo_path))
    session_manager.restore_auth_file(auth_file_path_str)

    read_auth_settings(config)

    session_manager.open_session(__file__, config.repo_path)

    if NO_AUTO_BRANCH:
        file_watcher = FileWatcherWatchdogOneBranch(config.repo_path, git_manager, file_manager)
    else:
        file_watcher = FileWatcherWatchdog(config.repo_path, git_manager, file_manager)
    session_manager.file_watcher = file_watcher

    if not NO_WATCHER:
        print("Starting observer ...")
        file_watcher.start()

    commands = get_commands_list(config.questions, file_watcher, git_manager, data_file_manager, session_manager,
                                 config.repo_path, __file__)
    command_prompt = PromptAutocomplete(commands, bottom_toolbar)

    file = open(".variables.dat", "w")

    while True:
        try:
            clear_console()
            command_prompt.prompt()
        except KeyboardInterrupt:
            response = yes_no_dialog(
                title='Quit & close session',
                text='Do you confirm you want to quit and close your workspace?').run()
            if response:
                session_manager.close_session(config.repo_path, __file__)
                sys.exit()
