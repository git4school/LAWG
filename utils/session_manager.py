import sys
from abc import ABC, abstractmethod
from pathlib import Path

from git import GitCommandError

from utils import find_stash_with_message
from utils.constant import NO_AUTO_BRANCH, AUTO_BRANCH, NO_SESSION_CLOSURE, AUTH_CONFIG_FILE_NAME, CONFIG_FILE_NAME, \
    DATA_FILE_NAME, IDENTITY_FILE_NAME
from utils.data_file_manager import DataFileManagerInterface
from utils.file_manager import FileManagerInterface
from utils.file_watcher import FileWatcherInterface
from utils.git_manager import GitManagerInterface


def update_gitignore(gitignore_path: Path) -> None:
    wildcard = ".settings.auth.yml"
    with open(gitignore_path, "a+") as gitignore_file:
        gitignore_file.seek(0)
        if wildcard not in gitignore_file.read():
            gitignore_file.write(f"\n{wildcard}")


class SessionManagerInterface(ABC):
    def __init__(self, git_manager: GitManagerInterface,
                 data_file_manager: DataFileManagerInterface,
                 file_manager: FileManagerInterface,
                 file_watcher: FileWatcherInterface = None):
        self.git_manager = git_manager
        self.data_file_manager = data_file_manager
        self.file_manager = file_manager
        self.file_watcher = file_watcher

    @abstractmethod
    def restore_auth_file(self, auth_file_path: str):
        pass

    @abstractmethod
    def open_session(self, __file__):
        pass

    @abstractmethod
    def close_session(self, folder_to_watch, __file__):
        pass


class SessionManager(SessionManagerInterface):
    def stash_untracked_files(self, auth_file_path: str):
        try:
            self.git_manager.add(auth_file_path, force=True)
            self.git_manager.stash(target=auth_file_path, message="auth")
            self.git_manager.stash(all=True, message="auto")
        except GitCommandError as stash_error:
            pass

    def restore_auth_file(self, auth_file_path: str):
        try:
            stash_list = self.git_manager.stash(command="list")
            auth_stash = find_stash_with_message(stash_list, "auth")
            if auth_stash:
                self.git_manager.stash(command="pop", target=auth_stash)
                self.git_manager.restore(auth_file_path, staged=True)
        except GitCommandError as stash_error:
            pass

    def restore_all_untracked_files(self):
        try:
            stash_list = self.git_manager.stash(command="list")
            auto_stash = find_stash_with_message(stash_list, "auto")
            if auto_stash:
                self.git_manager.stash(command="pop", target=auto_stash)
        except GitCommandError as stash_error:
            pass

    def open_session(self, __file__, repo_path):
        cross_close = self.data_file_manager.cross_close

        if not cross_close:
            self.git_manager.reset("HEAD", hard=True)

        self.restore_all_untracked_files()

        try:
            code = self.git_manager.pull()
        except GitCommandError as pull_error:
            print("An error as occurred when pulling, aborting the merge...")
            self.git_manager.merge(abort=True)
            print("The program will be stop, please contact your supervisor to handle the problem manually.")
            raise

        update_gitignore(Path(repo_path) / ".gitignore")
        commit_message = f"Resume"
        if NO_AUTO_BRANCH:
            self.git_manager.add_all()
            self.git_manager.commit(commit_message, allow_empty=True)
            self.git_manager.push(all=True)
        else:
            self.git_manager.duplicate_commit(commit_message, AUTO_BRANCH, allow_empty=True)
        self.data_file_manager.set_cross_close(True)

    def close_session(self, folder_to_watch, __file__):
        self.file_watcher.stop()
        commit_message = f"Pause"
        if NO_AUTO_BRANCH:
            self.git_manager.add_all()
            self.git_manager.commit(commit_message, allow_empty=True)
            self.git_manager.push(all=True)
        else:
            self.git_manager.duplicate_commit(commit_message, AUTO_BRANCH, allow_empty=True)

        if not NO_SESSION_CLOSURE:
            auth_file_path = str((Path(folder_to_watch) / AUTH_CONFIG_FILE_NAME).relative_to(folder_to_watch))
            self.stash_untracked_files(auth_file_path)

            if getattr(sys, 'frozen', False):
                application_path = Path(sys.executable).relative_to(Path(folder_to_watch).absolute())
            elif __file__:
                application_path = Path(__file__)
            else:
                raise RuntimeError("For some unknown reason, the type of the currently executed file "
                                   "is not recognized.")

            self.file_manager.delete_all(Path(folder_to_watch), [Path(folder_to_watch) / ".git/",
                                                            Path(folder_to_watch) / CONFIG_FILE_NAME,
                                                            Path(folder_to_watch) / AUTH_CONFIG_FILE_NAME,
                                                            Path(folder_to_watch) / DATA_FILE_NAME,
                                                            Path(folder_to_watch) / IDENTITY_FILE_NAME,
                                                            Path(folder_to_watch) / ".gitignore",
                                                            Path(application_path)])

        self.data_file_manager.set_cross_close(False)