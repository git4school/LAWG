import json
from abc import ABC, abstractmethod
from pathlib import Path


from utils import ok_dialog, radiolist_dialog


class IdentityCreatorInterface(ABC):
    def __init__(self):
        pass

    def create_identity_file(self, repo_path: Path, groups: list):
        identity_file_path = Path(repo_path) / "IDENTITY.json"

        if not identity_file_path.exists():
            first_name = self.ask_first_name()
            last_name = self.ask_last_name()
            group = self.ask_group(groups)

            identity = {
                "first_name": first_name,
                "last_name": last_name,
                "group": group
            }

            with open(identity_file_path, 'w') as identity_file:
                json.dump(identity, identity_file, indent=4)

    @abstractmethod
    def ask_first_name(self) -> str:
        pass

    @abstractmethod
    def ask_last_name(self) -> str:
        pass

    @abstractmethod
    def ask_group(self, groups: list) -> str:
        pass


class IdentityCreatorDialog(IdentityCreatorInterface):
    def ask_first_name(self) -> str:
        first_name = ok_dialog(
            title='Creation of the identity file',
            text='Please enter your first name: ').run()

        return first_name

    def ask_last_name(self) -> str:
        last_name = ok_dialog(
            title='Creation of the identity file',
            text='Please enter your last name: ').run()

        return last_name

    def ask_group(self, groups: list) -> str:
        groupss = [(groups[i], groups[i]) for i in range(len(groups))] if len(groups) > 0 else [("1", "1"),
                                                                                                ("2", "2")]

        group = radiolist_dialog(
            title="Creation of the identity file",
            text="Please select your group : ",
            values=groupss
        ).run()

        return group
