from abc import ABC, abstractmethod
from pathlib import Path

from git import Repo

from utils.constant import REMOTE_NAME
from utils import generate_authenticated_repo_uri


class GitManagerInterface(ABC):
    def __init__(self, repo_path, ssh_path):
        self.repo_path = repo_path
        self.ssh_path = ssh_path

    @abstractmethod
    def checkout(self, branch: str):
        pass

    @abstractmethod
    def reset(self, ref: str, soft=False, mixed=True, hard=False):
        pass

    @abstractmethod
    def read_tree(self, branch: str):
        pass

    @abstractmethod
    def checkout_index(self):
        pass

    @abstractmethod
    def commit(self, message: str, amend: bool = False, allow_empty: bool = False):
        pass

    @abstractmethod
    def duplicate_commit(self, message: str, branch: str, amend=False, allow_empty=False):
        pass

    @abstractmethod
    def pull(self):
        pass

    @abstractmethod
    def push(self, all: bool):
        pass

    @abstractmethod
    def add(self, file_path, intent_to_add: bool = False):
        pass

    @abstractmethod
    def add_all(self):
        pass

    @abstractmethod
    def branch(self, branch: str, force: bool = False):
        pass

    @abstractmethod
    def get_local_branches(self):
        pass

    @abstractmethod
    def get_remote_branches(self):
        pass

    @abstractmethod
    def get_current_branch(self):
        pass

    @abstractmethod
    def get_diff(self, ref: str = None):
        pass

    @abstractmethod
    def stash(self, pop: bool = False, all: bool = False, message: str = None):
        pass

    @abstractmethod
    def is_ignored(self, paths) -> bool:
        pass

    @abstractmethod
    def merge(self, abort=False):
        pass


class GitManagerPython(GitManagerInterface):
    def __init__(self, repo_path, ssh_path, nickname, pat):
        super().__init__(repo_path, ssh_path)
        self.repo = Repo(repo_path)
        self.remote = self.repo.remote(name=REMOTE_NAME)
        if pat is not None and nickname is not None:
            self.remote.set_url(generate_authenticated_repo_uri(nickname+":"+pat, self.remote.url), self.remote.url)

    def checkout(self, branch: str):
        return self.repo.git.checkout(branch)

    def reset(self, ref: str, soft=False, mixed=True, hard=False):
        return self.repo.head.reset(ref, index=not soft, working_tree=hard)

    def read_tree(self, branch: str):
        return self.repo.git.read_tree(branch)

    def checkout_index(self):
        return self.repo.git.checkout_index(f=True, a=True)

    def commit(self, message: str, amend=False, allow_empty=False):
        return self.repo.git.commit(message=message, amend=amend, allow_empty=allow_empty)

    def duplicate_commit(self, message: str, branch: str, amend=False, allow_empty=False):
        if branch not in self.get_local_branches():
            self.branch(branch)

        self.add_all()
        self.commit(message, allow_empty=True)
        self.reset(branch)
        self.commit(message, allow_empty=True)
        self.branch(branch, force=True)
        self.reset("HEAD@{2}")
        self.push(all=True)

    def pull(self):
        self.remote.pull()

    def push(self, all=False):
        try:
            ssh_cmd = f'ssh -v -i {self.ssh_path}'
            with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                return self.remote.push(all=all)  # progress=MyProgressPrinter())
        except Exception as e:
            print(e)

    def add(self, file_path, intent_to_add=False):
        path = Path(file_path)
        return self.repo.git.add(str(path.relative_to(self.repo_path)), intent_to_add=intent_to_add)

    def add_all(self):
        return self.repo.git.add(A=True)

    def branch(self, branch: str, force=False):
        return self.repo.git.branch(branch, force=force)

    def get_local_branches(self):
        return [branch.name for branch in self.repo.heads]

    def get_remote_branches(self):
        return [ref.name for ref in self.repo.remote().refs]

    def get_current_branch(self):
        return self.repo.head

    def get_diff(self, ref=None):
        return self.repo.git.diff(ref)

    def is_ignored(self, paths) -> bool:
        return bool(self.repo.ignored(paths))

    def stash(self, pop=False, all=False, message=None):
        if pop:
            return self.repo.git.stash("pop", all=all, message=message)
        else:
            return self.repo.git.stash(all=all, message=message)

    def merge(self, abort=False):
        self.repo.git.merge(abort=abort)
