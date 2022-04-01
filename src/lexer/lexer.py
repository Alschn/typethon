from typing import Optional

from src.errors.error import LexerError
from src.lexer.position import Position
from src.lexer.token import Token
from src.lexer.token_type import TokenType, RESERVED_KEYWORDS
from src.source import Source


class Lexer:
    MAX_IDENTIFIER_LENGTH = 127
    MAX_COMMENT_LENGTH = 255
    MAX_STRING_LENGTH = 1000
    MAX_MULTILINE_COMMENT_LENGTH = 10_024

    def __init__(self, source: Source):
        self.token: Optional[Token] = None
        self.source = source

    def build_next_token(self) -> Token:
        """Builds token or raises LexerError otherwise."""

        self.skip_whitespace()

        position = Position(self.source)

        # try each builder method
        for try_build_token in [
            self.try_build_identifier,
            self.try_build_comment,
            self.try_build_operator_or_reserved_character,
            self.try_build_number,
            self.try_build_string,
        ]:
            if token := try_build_token():
                token.position = position
                self.token = token
                return token

        # raise error if failed to build token
        raise LexerError('Failed to build token!')

    def skip_whitespace(self) -> None:
        """Gets next character until current character is not whitespace"""

        while self.source.current_char.isspace():
            self.source.get_next_character()

    def try_build_number(self) -> Optional[Token]:
        """Tries to build either int or float, accepts scientific notation."""

        if not self.source.current_char.isdigit():
            return

        collected_chars = []

        # handle integer part
        if self.source.current_char == '0':
            # check if number is 0 or starts with 0
            collected_chars.append(self.source.current_char)
            self.source.get_next_character()

            # 0 cannot be followed by another digit
            if self.source.current_char.isdigit():
                raise LexerError("Failed to build number. Leading 0 cannot be followed by another 0.")
        else:
            # number did not start with 0, next characters can either be `.` or digits
            while self.source.current_char.isdigit():
                collected_chars.append(self.source.current_char)
                self.source.get_next_character()

        # handle decimal part
        if self.source.current_char == '.':
            collected_chars.append(self.source.current_char)
            self.source.get_next_character()

            # if next character is not a digit, then it cannot be a valid number
            if not self.source.current_char.isdigit():
                raise LexerError("Failed to build number. Received `.` which was not followed by digit.")

            # else collect all digits after `.`
            while self.source.current_char.isdigit():
                collected_chars.append(self.source.current_char)
                self.source.get_next_character()

            # there had to be at least one number after dot e.g `1.2`
            # so scientific notation can be handled e.g `1.2e1` or `1.2E-10`
            if self.source.current_char == 'e' or self.source.current_char == 'E':
                collected_chars.append(self.source.current_char)
                self.source.get_next_character()

                if self.source.current_char == '-':
                    collected_chars.append(self.source.current_char)
                    self.source.get_next_character()

                # expected digit after `e` or `e-`
                if not self.source.current_char.isdigit():
                    raise LexerError("Failed to build number. Received `e` which was not followed by exponent.")

                # collect remaining digits
                while self.source.current_char.isdigit():
                    collected_chars.append(self.source.current_char)
                    self.source.get_next_character()

            # managed to build valid float
            result = ''.join(collected_chars)
            return Token(
                typ=TokenType.FLOAT_VALUE,
                value=float(result),
            )

        # if there was no `.` character and no error was raised, then managed to build a valid integer
        result = ''.join(collected_chars)
        return Token(
            typ=TokenType.INT_VALUE,
            value=int(result),
        )

    def try_build_identifier(self) -> Optional[Token]:
        """Tries to build an identifier which is either:

        1. keyword:
        (`const`, `let`,
        `int`, `float`, `str`, `bool`,
        `func`, `void`, `def`, `return`,
        `if`, `elif`, `else`, `while`,
        `not`, `or`, `and`)

        2. variable name
        """
        if not self.source.current_char.isalpha() and not self.source.current_char == "_":
            return None

        collected_chars = []

        while len(collected_chars) <= self.MAX_IDENTIFIER_LENGTH and (
                self.source.current_char.isalnum() or self.source.current_char == "_"):
            collected_chars.append(self.source.current_char)
            self.source.get_next_character()

        if len(collected_chars) > self.MAX_IDENTIFIER_LENGTH:
            raise LexerError("Too long identifier!")

        result = ''.join(collected_chars)

        if result == "true":
            return Token(
                typ=TokenType.BOOL_VALUE,
                value=True
            )

        elif result == "false":
            return Token(
                typ=TokenType.BOOL_VALUE,
                value=False
            )

        elif result == "null":
            return Token(
                typ=TokenType.NULL_VALUE,
                value=None
            )

        token_type = RESERVED_KEYWORDS.get(result)

        # matched a reserved keyword
        if token_type is not None:
            return Token(
                typ=token_type,
                value=result
            )

        # else received a variable name
        return Token(
            typ=TokenType.ID,
            value=result
        )

    def try_build_string(self) -> Optional[Token]:
        """Tries to build string either in single or double quotes"""

        if self.source.current_char not in ["\"", "\'"]:
            return None

        # keep quotes consistent
        opening_quote = self.source.current_char
        collected_chars = []

        self.source.get_next_character()

        while len(collected_chars) <= self.MAX_STRING_LENGTH and self.source.current_char != opening_quote:
            # string was not closed and program ran into ETX
            if self.source.current_char == TokenType.ETX:
                raise LexerError(f"Failed to build string! Expected `{opening_quote}`, got ETX.")

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
            raise LexerError("Failed to build string! Received content which is too long.")

        # exit string quotes
        self.source.get_next_character()

        result = ''.join(collected_chars)

        return Token(
            typ=TokenType.STR_VALUE,
            value=result,
        )

    def try_build_comment(self) -> Optional[Token]:
        """Tries to build a comment."""

        if self.source.current_char != "/":
            return None

        self.source.get_next_character()

        # if next character is `*`, then it is a multiline comment
        if self.source.current_char == "*":
            return self.__try_build_multiline_comment()

        # if next character is not `/`, then previous character should be treated as division operator
        elif self.source.current_char != "/":
            return Token(
                typ=TokenType.DIV,
                value=TokenType.DIV.value
            )

        # move into comment itself
        self.source.get_next_character()

        collected_chars = []

        # collect everything until found newline symbol or ETX
        while len(collected_chars) <= self.MAX_COMMENT_LENGTH and (
                self.source.current_char != TokenType.ETX and
                self.source.current_char != "\n"):
            # append everything including whitespaces
            collected_chars.append(self.source.current_char)
            self.source.get_next_character()

        if len(collected_chars) > self.MAX_COMMENT_LENGTH:
            raise LexerError("Too long comment!")

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

        # collect everything until found newline symbol
        while len(collected_chars) <= self.MAX_MULTILINE_COMMENT_LENGTH and (
                self.source.current_char != "*"):

            # to do better check
            if self.source.current_char == TokenType.ETX:
                raise LexerError("Multiline was not closed! Reached end of text!")

            # append everything including whitespaces
            collected_chars.append(self.source.current_char)
            self.source.get_next_character()

        if len(collected_chars) > self.MAX_MULTILINE_COMMENT_LENGTH:
            raise LexerError("Too long multiline comment!")

        if self.source.current_char == "*":
            self.source.get_next_character()

            if self.source.current_char != "/":
                raise LexerError("Multiline comment was not properly closed!")

        result = "".join(collected_chars)

        # escape multiline comment
        self.source.get_next_character()

        return Token(
            typ=TokenType.COMMENT,
            value=result
        )

    def try_build_operator_or_reserved_character(self) -> Optional[Token]:
        """Tries to build one or two character operator"""

        if self.source.current_char == "=":
            self.source.get_next_character()

            # `==`
            if self.source.current_char == "=":
                token = Token(
                    typ=TokenType.EQ,
                    value=TokenType.EQ
                )
                self.source.get_next_character()
                return token

            # `=>`
            elif self.source.current_char == ">":
                token = Token(
                    typ=TokenType.ARROW,
                    value=TokenType.ARROW
                )
                self.source.get_next_character()
                return token

            # `=`
            else:
                token = Token(
                    typ=TokenType.ASSIGN,
                    value=TokenType.ASSIGN
                )
                self.source.get_next_character()
                return token

        elif self.source.current_char == "!":
            self.source.get_next_character()

            # `!=`
            if self.source.current_char == "=":
                token = Token(
                    typ=TokenType.NEQ,
                    value=TokenType.NEQ
                )
                self.source.get_next_character()
                return token
            else:
                # character should be built with another method
                # or error
                return

        elif self.source.current_char == ">":
            self.source.get_next_character()

            # `>=`
            if self.source.current_char == "=":
                token = Token(
                    typ=TokenType.GTE,
                    value=TokenType.GTE
                )
                self.source.get_next_character()
                return token

            # `>`
            else:
                token = Token(
                    typ=TokenType.GT,
                    value=TokenType.GT
                )
                self.source.get_next_character()
                return token

        elif self.source.current_char == "<":
            self.source.get_next_character()

            # `<=`
            if self.source.current_char == "=":
                token = Token(
                    typ=TokenType.LTE,
                    value=TokenType.LTE
                )
                self.source.get_next_character()
                return token

            # `<`
            else:
                token = Token(
                    typ=TokenType.LT,
                    value=TokenType.LT
                )
                self.source.get_next_character()
                return token

        elif self.source.current_char == "?":
            self.source.get_next_character()

            # `?:`
            if self.source.current_char == ":":
                token = Token(
                    typ=TokenType.TYPE_ASSIGN_NULLABLE,
                    value=TokenType.TYPE_ASSIGN_NULLABLE
                )
                self.source.get_next_character()
                return token

            # `??`
            elif self.source.current_char == "?":
                token = Token(
                    typ=TokenType.NULL_COALESCE,
                    value=TokenType.NULL_COALESCE
                )
                self.source.get_next_character()
                return token

            else:
                # character should be built with another method
                # or error
                return

        else:
            try:
                token_type = TokenType(self.source.current_char)
                token = Token(
                    typ=token_type,
                    value=token_type
                )
                # get_next_character because only one letter was consumed
                self.source.get_next_character()
                return token

            except ValueError:
                # token type was not found in `TokenType` enum
                # character should be built with another method
                return
