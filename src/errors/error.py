from src.lexer.position import Position


class Error(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class LexerError(Error):
    def __init__(self, message: str, position: Position):
        super().__init__(message)
        self.message = message
        self.position = position

    def __str__(self) -> str:
        return f"{self.message} Line: {self.position.line} Column: {self.position.column}"


class ParserError(Error):
    def __init__(self, current_token):
        self.token = current_token

    def __str__(self) -> str:
        return f'Unexpected token {self.token.type} at {self.token.position}'


class UnexpectedTokenError(ParserError):

    def __init__(self, current_token, expected_token_type):
        self.actual = current_token
        self.expected_type = expected_token_type

    def __str__(self) -> str:
        return f"Expected {self.expected_type}. Got {self.actual.type} instead. {self.actual.position}"


class UninitializedConstError(ParserError):

    def __str__(self) -> str:
        return f"Missing initializer in const declaration. {self.token.position}"


class NotNullableError(ParserError):
    def __init__(self, operator_position):
        self.op_position = operator_position

    def __str__(self) -> str:
        return f"Cannot assign null to variable which is not nullable. Use `?:` instead of `:` at {self.op_position}."


class InvalidTypeError(ParserError):

    def __str__(self) -> str:
        return f"`{self.token.type}` is not a valid type. {self.token.position}"


class InvalidReturnTypeError(ParserError):

    def __str__(self) -> str:
        return f"`{self.token.type}` is not a valid function return type. {self.token.position}"


class InvalidRightExpressionError(ParserError):

    def __str__(self) -> str:
        return f"Invalid right side of an expression. {self.token.position}"


class MissingParameterError(ParserError):

    def __str__(self) -> str:
        return f"Missing parameter in function definition. {self.token.position}"


class MissingArgumentError(ParserError):

    def __str__(self) -> str:
        return f"Missing argument in function call. {self.token.position}"


class MissingLambdaExpressionBody(ParserError):

    def __str__(self) -> str:
        return f"Missing body definition in lambda expression. {self.token.position}"


class InterpreterError(Error):
    def __init__(self, message: str):
        super().__init__(message)
