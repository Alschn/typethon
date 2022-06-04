from src.errors.base import Error
from src.lexer.position import Position


class LexerError(Error):
    def __init__(self, message: str, position: Position):
        super().__init__(message)
        self.message = message
        self.position = position

    def __str__(self) -> str:
        return f"{self.message} Line: {self.position.line} Column: {self.position.column}"