from abc import ABC, abstractmethod
from pathlib import Path

from git import Repo


class GitManagerInterface(ABC):
    def __init__(self, repo_path, ssh_path):
        self.repo_path = repo_path
        self.ssh_path = ssh_path

    @abstractmethod
    def commit(self, message):
        pass

    @abstractmethod
    def push(self):
        pass

    @abstractmethod
    def add(self, file_path):
        pass


class GitManagerPython(GitManagerInterface):
    def __init__(self, repo_path, ssh_path):
        super().__init__(repo_path, ssh_path)
        self.repo = Repo(repo_path)
        self.origin = self.repo.remote(name="origin")

    def commit(self, message):
        self.repo.index.commit(message)

    def push(self):
        try:
            ssh_cmd = f'ssh -v -i {self.ssh_path}'
            with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                self.origin.push()  # progress=MyProgressPrinter())
                print("Pushed !")
        except Exception as e:
            print(e)

    def add(self, file_path):
        path = Path(file_path)
        self.repo.index.add([str(path.resolve())])
