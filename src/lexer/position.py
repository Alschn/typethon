from src.source import Source


class Position:
    """Class storing line, column, current_position of a given source."""

    def __init__(self, source: Source):
        self.line = source.line
        self.column = source.column
        self.current_position = source.current_position

    def __str__(self) -> str:
        return f"Line:{self.line} Column:{self.column} Pos:{self.current_position}"
