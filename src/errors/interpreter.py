from typing import Any

from src.errors.base import Error
from src.parser.types import Type


class InterpreterError(Error):

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message


class DivisionByZeroError(InterpreterError):

    def __str__(self):
        return f"Division by 0 is not allowed!"


class UndefinedNameError(InterpreterError):

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return f"{self.name} is not defined."


class NotCallableError(InterpreterError):

    def __init__(self, name: str, typ: Type):
        self.name = name
        self.typ = typ

    def __str__(self) -> str:
        return f"Variable {self.name} type {self.typ} is not callable."


class ArgumentsError(InterpreterError):

    def __init__(self, name: str, expected: int, actual: int):
        self.fn_name = name
        self.expected = expected
        self.actual = actual

    def __str__(self) -> str:
        return f"{self.fn_name} takes {self.expected} arguments but {self.actual} were given."


class ArgumentTypeError(InterpreterError):

    def __init__(self, fn_name: str, name: str, expected, actual):
        self.fn_name = fn_name
        self.name = name
        self.expected = expected
        self.actual = actual

    def __str__(self) -> str:
        return f"Parameter {self.name} of function {self.fn_name} should be type {self.expected}. Got type {self.actual} instead."


class RecursionLimitError(InterpreterError):

    def __str__(self) -> str:
        return f"Exceeded recursion limit."


class UninitializedConstError(InterpreterError):

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return f"Missing initializer in const declaration of variable {self.name}."


class NotNullableError(InterpreterError):

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return f"Cannot assign null to variable {self.name} which is not nullable."


class ConstRedeclarationError(InterpreterError):

    def __init__(self, name):
        self.name = name

    def __str__(self) -> str:
        return f"Cannot reassign variable {self.name} because there already exists one, which is a constant."


class ConstAssignmentError(InterpreterError):

    def __init__(self, name):
        self.name = name

    def __str__(self) -> str:
        return f"Cannot assign to {self.name} because it is a constant."


class UnexpectedTypeError(InterpreterError):

    def __str__(self) -> str:
        return self.message


class ReturnTypeMismatchError(InterpreterError):
    def __init__(self, name: str, expected: Type, actual: Type):
        self.fn_name = name
        self.expected = expected
        self.actual = actual

    def __str__(self) -> str:
        return f"Function {self.fn_name} returned type {self.actual} but expected type {self.expected}."


class TypeMismatchError(InterpreterError):

    def __init__(self, name: str, expected: Type, actual: Type):
        self.name = name
        self.expected = expected
        self.actual = actual

    def __str__(self) -> str:
        return f"Variable {self.name} was declared with type {self.expected} but received type {self.actual}."


class AssignmentTypeMismatchError(TypeMismatchError):

    def __str__(self) -> str:
        return f"Cannot assign type {self.actual} to variable {self.name} type {self.expected}."


class ReturnOutsideOfFunctionError(InterpreterError):

    def __str__(self) -> str:
        return f"Return statement is not allowed outside of a function."


class ReturnException(Exception):
    def __init__(self, value: Any):
        self.value_to_return = value
