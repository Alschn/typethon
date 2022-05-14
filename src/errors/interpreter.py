from src.errors.base import Error


class InterpreterError(Error):

    def __init__(self, message: str):
        super().__init__(message)
