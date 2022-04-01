from pathlib import Path
from typing import Generator

from src.lexer.token import TokenType


class Source:

    def __init__(self, text: Generator):
        self.iterator = iter(text)

        # check if source is not empty
        try:
            self.current_char: str = next(self.iterator)
        except StopIteration:
            self.current_char = TokenType.ETX

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
            self.current_char = TokenType.ETX


class FileSource(Source):

    def __init__(self, file_name: Path):
        self.file = open(file_name, 'r')
        generator = self.read_file_lazy()
        super().__init__(generator)

    def read_file_lazy(self, chunk_size: int = 1024):
        """Reads file in chunks and yields a character from a current chunk."""

        while True:
            chunk = self.file.read(chunk_size)

            if not chunk:
                break

            for char in chunk:
                yield char

    def __del__(self):
        self.file.close()


class StringSource(Source):

    def __init__(self, string: str):
        generator = (char for char in string)
        super().__init__(generator)
