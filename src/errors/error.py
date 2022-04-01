class Error(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class LexerError(Error):
    def __init__(self, message: str):
        super().__init__(message)


class ParserError(Error):
    def __init__(self, message: str):
        super().__init__(message)


class InterpreterError(Error):
    def __init__(self, message: str):
        super().__init__(message)
