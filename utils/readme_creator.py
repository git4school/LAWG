from abc import ABC, abstractmethod

from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog


class ReadmeCreatorInterface(ABC):
    def __init__(self):
        pass

    def create_readme(self):
        first_name = self.ask_first_name()
        last_name = self.ask_last_name()
        group = self.ask_group()

        readme = f"""
# README

### NOM : {last_name.upper()}
### Prénom : {first_name.capitalize()}
### Groupe de TP : {group}
- [ ] 11
- [x] 12
- [ ] 21
- [ ] 22
"""

        with open('READMEe.md', 'w') as readme_file:
            readme_file.write(readme
                              )

    @abstractmethod
    def ask_first_name(self) -> str:
        pass

    @abstractmethod
    def ask_last_name(self) -> str:
        pass

    @abstractmethod
    def ask_group(self) -> str:
        pass


class ReadmeCreatorDialog(ReadmeCreatorInterface):
    def ask_first_name(self) -> str:
        first_name = input_dialog(
            title='Initialisation du README',
            text='Entrez votre prénom : ').run()

        return first_name

    def ask_last_name(self) -> str:
        last_name = input_dialog(
            title='Initialisation du README',
            text='Entrez votre nom de famille : ').run()

        return last_name

    def ask_group(self) -> str:
        group = radiolist_dialog(
            title="Initialisation du README",
            text="Sélectionnez votre groupe de TP : ",
            values=[
                ("TP1", "TP1"),
                ("TP2", "TP2"),
                ("TP3", "TP3")
            ]
        ).run()

        return group
