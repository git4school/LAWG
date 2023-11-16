import pickle
from abc import ABC, abstractmethod
from pathlib import Path

from utils.file_manager import FileManagerInterface


class Data:
    def __init__(self):
        self._completed_questions = []
        self._cross_close = False

    @property
    def cross_close(self):
        return self._cross_close

    @cross_close.setter
    def cross_close(self, value):
        self._cross_close = value

    @property
    def completed_questions(self):
        return self._completed_questions

    @completed_questions.setter
    def completed_questions(self, value):
        self._completed_questions = value


class DataFileManagerInterface(ABC):
    def __init__(self, file_manager: FileManagerInterface, data_file_path: Path, questions):
        self.data = Data()
        self.file_manager = file_manager
        self.questions = questions
        self.load(data_file_path)
        self.data_file_path = data_file_path

    @abstractmethod
    def load(self, path: Path):
        pass

    @abstractmethod
    def complete_question(self, question):
        pass

    @abstractmethod
    def set_cross_close(self, value: bool):
        pass

    @property
    def cross_close(self):
        return self.data.cross_close

    @cross_close.setter
    def cross_close(self, value):
        self.data.cross_close = value

    @property
    def completed_questions(self):
        return self.data.completed_questions

    @completed_questions.setter
    def completed_questions(self, value):
        self.data.completed_questions = value


class PickleDataFileManager(DataFileManagerInterface):
    def load(self, path: Path):
        try:
            with self.file_manager.open(path, "rb") as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            #print("No variables.dat found.")
            pass
        except EOFError:
            #print("Empty variables.dat.")
            pass

    def complete_question(self, question):
        if question in self.questions \
                and question not in self.completed_questions:
            self.completed_questions.append(question)
            self.update_data_file()

    def update_data_file(self):
        with self.file_manager.open(self.data_file_path, 'wb') as file:
            pickle.dump(self.data, file)

    def set_cross_close(self, value: bool):
        self.cross_close = value
        self.update_data_file()

    @property
    def completed_questions(self):
        return self.data.completed_questions

    @completed_questions.setter
    def completed_questions(self, value):
        self.data.completed_questions = value

    @property
    def cross_close(self):
        return self.data.cross_close

    @cross_close.setter
    def cross_close(self, value):
        self.data.cross_close = value
