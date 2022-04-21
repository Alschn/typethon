from pathlib import Path
from typing import Generator

from src.lexer.token_type import ETX_VALUE


class Source:

    def __init__(self, text: Generator):
        self.iterator = iter(text)

        try:
            self.current_char: str = next(self.iterator)
        except StopIteration:
            self.current_char = ETX_VALUE

        # start indexing from 1 - so that it is human readable
        self.line = 1
        self.column = 1

        self.current_position = 0  # position in source

    def get_next_character(self) -> None:
        """Tries to get next character from text iterator.
        Sets current_char and current position in text and in source.
        Upon reaching end of text, sets current character to ETX.
        """

        try:
            self.current_char = next(self.iterator)
            self.column += 1
            self.current_position += 1

            if self.current_char == "\n":
                self.line += 1
                self.column = 0

        except StopIteration:
            self.current_char = ETX_VALUE


class FileSource(Source):

    def __init__(self, file_name: Path):
        self._file = open(file_name, 'r')
        generator = self.read_file_lazy()
        super().__init__(generator)

    def read_file_lazy(self):
        """Reads single character from an open file"""

        while c := self._file.read(1):
            yield c

    def __del__(self):
        self._file.close()


class StringSource(Source):

    def __init__(self, string: str):
        generator = (char for char in string)
        super().__init__(generator)
