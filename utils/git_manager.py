from abc import ABC, abstractmethod
from pathlib import Path

from git import Repo


class GitManagerInterface(ABC):
    def __init__(self, repo_path, ssh_path):
        self.repo_path = repo_path
        self.ssh_path = ssh_path

    @abstractmethod
    def checkout(self, branch: str):
        pass

    @abstractmethod
    def reset(self, ref: str, soft: bool, mixed: bool, hard: bool):
        pass

    @abstractmethod
    def read_tree(self, branch: str):
        pass

    @abstractmethod
    def checkout_index(self):
        pass

    @abstractmethod
    def commit(self, message: str, amend: bool):
        pass

    @abstractmethod
    def push(self, all: bool):
        pass

    @abstractmethod
    def add(self, file_path, intent_to_add: bool):
        pass

    @abstractmethod
    def add_all(self):
        pass

    @abstractmethod
    def branch(self, branch: str, force: bool):
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
    def get_diff(self, ref: str):
        pass


class GitManagerPython(GitManagerInterface):
    def __init__(self, repo_path, ssh_path):
        super().__init__(repo_path, ssh_path)
        self.repo = Repo(repo_path)
        self.origin = self.repo.remote(name="origin")

    def checkout(self, branch: str):
        return self.repo.git.checkout(branch)

    def reset(self, ref: str, soft=False, mixed=True, hard=False):
        return self.repo.head.reset(ref, index=not soft, working_tree=hard)

    def read_tree(self, branch: str):
        return self.repo.git.read_tree(branch)

    def checkout_index(self):
        return self.repo.git.checkout_index(f=True, a=True)

    def commit(self, message: str, amend=False):
        return self.repo.git.commit(message=message, amend=amend)

    def push(self, all=False):
        try:
            ssh_cmd = f'ssh -v -i {self.ssh_path}'
            with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                return self.origin.push(all=all)  # progress=MyProgressPrinter())
        except Exception as e:
            print(e)

    def add(self, file_path, intent_to_add=False):
        path = Path(file_path)
        return self.repo.git.add(str(path.resolve()), intent_to_add=intent_to_add)

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

