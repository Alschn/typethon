from typing import Optional

from src.errors.error import LexerError
from src.lexer.position import Position
from src.lexer.token import Token
from src.lexer.token_type import TokenType, KEYWORDS, ETX_VALUE, ONE_CHAR_OPS, TWO_CHAR_OPS
from src.source import Source


class Lexer:
    MAX_IDENTIFIER_LENGTH = 255
    MAX_STRING_LENGTH = 10000

    def __init__(self, source: Source):
        self.token: Optional[Token] = None
        self.source = source

    def build_next_token(self) -> Token:
        """Builds token or raises LexerError otherwise."""

        self._skip_whitespace()

        position = Position(self.source)

        for try_build_token in [
            self._try_build_comment,
            self._try_build_identifier,
            self._try_build_one_or_two_char_token,
            self._try_build_number,
            self._try_build_string,
            self._try_build_etx,
        ]:
            if token := try_build_token():
                token.position = position
                self.token = token
                return token

        raise LexerError('Failed to build token!', position=position)

    def _skip_whitespace(self) -> None:
        """Gets next character until current character is not whitespace"""

        while self.source.current_char.isspace():
            self.source.get_next_character()

    def _try_build_number(self) -> Optional[Token]:
        """Tries to build either int or float, accepts scientific notation."""

        if not self.source.current_char.isdigit():
            return

        collected_chars = []

        self.__collect_integer_part(collected_chars)

        if token := self.__try_build_decimal_part(collected_chars):
            return token

        # failed to build float, but there were no errors, so it is a valid integer
        result = ''.join(collected_chars)
        return Token(
            typ=TokenType.INT_VALUE,
            value=int(result),
        )

    def __collect_integer_part(self, collected_chars: list[str]) -> None:
        """Collects characters that can appear before `.`"""

        if self.source.current_char == '0':
            # check if number is 0 or starts with 0
            collected_chars.append(self.source.current_char)
            self.source.get_next_character()

            # 0 cannot be followed by another digit
            if self.source.current_char.isdigit():
                raise LexerError(
                    "Failed to build number. Leading 0 cannot be followed by another 0.", Position(self.source)
                )
        else:
            # number did not start with 0, next characters can either be `.` or digits
            while self.source.current_char.isdigit():
                collected_chars.append(self.source.current_char)
                self.source.get_next_character()

    def __try_build_decimal_part(self, collected_chars: list[str]) -> Optional[Token]:
        """Tries to build a float based on already collected integer part
        and characters collected after `.`"""

        if self.source.current_char != ".":
            return

        collected_chars.append(self.source.current_char)
        self.source.get_next_character()

        # if next character is not a digit, then it cannot be a valid number
        if not self.source.current_char.isdigit():
            raise LexerError(
                "Failed to build number. Received `.` which was not followed by digit.",
                Position(self.source)
            )

        # else collect all digits after `.`
        while self.source.current_char.isdigit():
            collected_chars.append(self.source.current_char)
            self.source.get_next_character()

        # there had to be at least one number after dot e.g `1.2`
        # so scientific notation can be handled e.g `1.2e1` or `1.2E-10`
        self.__collect_scientific_notation(collected_chars)

        # managed to build valid float
        result = ''.join(collected_chars)
        return Token(
            typ=TokenType.FLOAT_VALUE,
            value=float(result),
        )

    def __collect_scientific_notation(self, collected_chars: list[str]) -> None:
        """Handles scientific notation while trying to build a float"""

        if self.source.current_char == 'e' or self.source.current_char == 'E':
            collected_chars.append(self.source.current_char)
            self.source.get_next_character()

            if self.source.current_char == '-':
                collected_chars.append(self.source.current_char)
                self.source.get_next_character()

            # expected digit after `e` or `e-`
            if not self.source.current_char.isdigit():
                raise LexerError(
                    "Failed to build number. Received `e` which was not followed by exponent.",
                    Position(self.source)
                )

            # collect remaining digits
            while self.source.current_char.isdigit():
                collected_chars.append(self.source.current_char)
                self.source.get_next_character()

    def _try_build_identifier(self) -> Optional[Token]:
        """Tries to build an identifier which is either:
        1. keyword
        2. variable name
        """
        if not self.source.current_char.isalpha() and not self.source.current_char == "_":
            return

        collected_chars = []

        while self.source.current_char.isalnum() or self.source.current_char == "_":
            collected_chars.append(self.source.current_char)

            if len(collected_chars) > self.MAX_IDENTIFIER_LENGTH:
                raise LexerError(
                    "Failed to build identifier!. Received content which is too long!", Position(self.source)
                )

            self.source.get_next_character()

        result = ''.join(collected_chars)

        token_type = KEYWORDS.get(result)

        # matched a reserved keyword
        if token_type is not None:
            return Token(typ=token_type)

        # else received a variable name
        return Token(
            typ=TokenType.ID,
            value=result
        )

    def _try_build_string(self) -> Optional[Token]:
        """Tries to build string either in single or double quotes"""

        if self.source.current_char not in ["\"", "\'"]:
            return

        # keep quotes consistent
        opening_quote = self.source.current_char
        collected_chars = []

        self.source.get_next_character()

        while self.source.current_char != opening_quote and len(collected_chars) <= self.MAX_STRING_LENGTH:
            # string was not closed and program ran into ETX
            if self.source.current_char == ETX_VALUE:
                raise LexerError(f"Failed to build string! Expected `{opening_quote}`, got ETX.", Position(self.source))

            if self.source.current_char == "\\":
                # if current character is `\`, then go ahead
                self.source.get_next_character()

                # prevent string ending or bare backslashes
                if self.source.current_char in [opening_quote, "\\"]:
                    collected_chars.append(self.source.current_char)
                else:
                    collected_chars.append(f"\\{self.source.current_char}")
            else:
                collected_chars.append(self.source.current_char)

            self.source.get_next_character()

        if len(collected_chars) > self.MAX_STRING_LENGTH:
            raise LexerError("Failed to build string!. Received content which is too long!", Position(self.source))

        # exit string quotes
        self.source.get_next_character()

        result = ''.join(collected_chars)

        return Token(
            typ=TokenType.STR_VALUE,
            value=result,
        )

    def _try_build_comment(self) -> Optional[Token]:
        """Tries to build a one line or multiline comment."""

        if self.source.current_char != "/":
            return

        self.source.get_next_character()

        # if next character is `*`, then it is a multiline comment
        if self.source.current_char == "*":
            return self.__try_build_multiline_comment()

        # if next character is not `/`, then previous character should be treated as division operator
        elif self.source.current_char != "/":
            return Token(typ=TokenType.DIV)

        # move into comment itself
        self.source.get_next_character()

        collected_chars = []

        # collect everything until found newline symbol or ETX
        while self.source.current_char != ETX_VALUE and self.source.current_char != "\n":
            # append everything including whitespaces
            collected_chars.append(self.source.current_char)
            self.source.get_next_character()

        result = "".join(collected_chars)
        return Token(
            typ=TokenType.COMMENT,
            value=result
        )

    def __try_build_multiline_comment(self) -> Optional[Token]:
        """Tries to build a multiline comment."""

        # move into comment itself
        self.source.get_next_character()

        collected_chars = []
        comment_closed = False

        # comment will either be closed or lexer will reach end of text (which will result in an error)
        while not comment_closed:
            if self.source.current_char == ETX_VALUE:
                raise LexerError("Multiline was not closed! Reached end of text!", Position(self.source))

            if self.source.current_char == "*":
                self.source.get_next_character()

                # check if comment is being closed
                if self.source.current_char == "/":
                    comment_closed = True
                else:
                    # add `*` only if it was not followed by `/`
                    collected_chars.append("*")
            else:
                collected_chars.append(self.source.current_char)
                self.source.get_next_character()

        result = "".join(collected_chars)

        # leave multiline comment
        self.source.get_next_character()

        return Token(
            typ=TokenType.COMMENT,
            value=result
        )

    def _try_build_one_or_two_char_token(self) -> Optional[Token]:
        """Tries to build token which consists of 1 or 2 characters (mostly operators)."""

        current = self.source.current_char
        if current not in [*ONE_CHAR_OPS.keys(), "!", "?"]:
            return

        # check if we can build operator with two characters
        self.source.get_next_character()
        two_chars = "".join([current, self.source.current_char])

        if two_char_op := TWO_CHAR_OPS.get(two_chars):
            self.source.get_next_character()
            return Token(typ=two_char_op)

        # neither does the first character start two char operator nor is a one char operator itself
        if not (one_char_op := ONE_CHAR_OPS.get(current)):
            raise LexerError(f"Failed to build an operator: `{current}`", Position(self.source))

        return Token(typ=one_char_op)

    def _try_build_etx(self) -> Optional[Token]:
        """Tries to build an ETX token upon reaching special end of text value."""

        if self.source.current_char == ETX_VALUE:
            return Token(typ=TokenType.ETX)
