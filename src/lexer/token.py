from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Union

from src.lexer.token_type import TokenType

if TYPE_CHECKING:
    from src.lexer.position import Position

TRUNC_TO_LENGTH = 20


class Token:

    def __init__(self, typ: TokenType, value: Union[str, int, float, bool] = None, position: Position = None):
        self.type = typ
        self.value = value
        self.position = position

    def __str__(self) -> str:
        if self.type == TokenType.STR or self.type == TokenType.COMMENT:
            # strip and truncate representational string value
            stripped = self.value.strip()
            value = (stripped[:TRUNC_TO_LENGTH] + '...') if len(stripped) > TRUNC_TO_LENGTH else stripped
            return f"<Token {self.type} {value.strip()} {self.position}>"

        return f"<Token {self.type} {self.value} {self.position}>"
