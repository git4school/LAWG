from abc import ABC, abstractmethod
from pathlib import Path, PurePath

from git import Repo


class GitManagerInterface(ABC):
    def __init__(self, repo_path, ssh_path):
        self.repo_path = repo_path
        self.ssh_path = ssh_path

    @abstractmethod
    def checkout(self, branch: str):
        pass

    @abstractmethod
    def read_tree(self, branch: str):
        pass

    @abstractmethod
    def checkout_index(self):
        pass

    @abstractmethod
    def commit(self, message):
        pass

    @abstractmethod
    def push(self):
        pass

    @abstractmethod
    def add(self, file_path):
        pass

    @abstractmethod
    def add_all(self):
        pass


class GitManagerPython(GitManagerInterface):
    def __init__(self, repo_path, ssh_path):
        super().__init__(repo_path, ssh_path)
        self.repo = Repo(repo_path)
        self.origin = self.repo.remote(name="origin")

    def checkout(self, branch: str):
        self.repo.git.checkout(branch)

    def read_tree(self, branch: str):
        self.repo.git.read_tree(branch)

    def checkout_index(self):
        self.repo.git.checkout_index(f=True, a=True)

    def commit(self, message):
        self.repo.index.commit(message)

    def push(self):
        try:
            ssh_cmd = f'ssh -v -i {self.ssh_path}'
            with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                self.origin.push()  # progress=MyProgressPrinter())
        except Exception as e:
            print(e)

    def add(self, file_path):
        path = Path(file_path)
        self.repo.git.add(str(path.resolve()))

    def add_all(self):
        self.repo.git.add(A=True)
