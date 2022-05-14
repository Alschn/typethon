from enum import Enum, auto
from typing import Union

from src.lexer.token_type import TokenType

Value = Union[str, int, float, bool]


class Type:
    pass


class Integer(Type):
    pass


class Float(Type):
    pass


class Bool(Type):
    pass


class String(Type):
    pass


class Null(Type):
    pass


class Void(Type):
    pass


class Func(Type):

    def __init__(self, arguments_types, return_type: Type):
        self.input_types = arguments_types
        self.output_type = return_type


TYPES_MAPPING = {
    TokenType.VOID: Void,
    TokenType.FLOAT_VALUE: Float,
    TokenType.FLOAT: Float,
    TokenType.INT_VALUE: Integer,
    TokenType.INT: Integer,
    TokenType.STR_VALUE: String,
    TokenType.STR: String,
    TokenType.NULL_VALUE: Null,
    TokenType.FUNC: Func,
    TokenType.BOOL: Bool,
    TokenType.TRUE_VALUE: Bool,
    TokenType.FALSE_VALUE: Bool,
}


class LogicOperator(Enum):
    AND = auto()
    OR = auto()
    # TODO rest


class ComparisonOperator(Enum):
    EQ = auto()
    NEQ = auto()
    GTE = auto()
    GT = auto()
    LTE = auto()
    LT = auto()
    # TODO rest

class ArithmeticOperator(Enum):
    PLUS = auto()
    MINUS = auto()
    DIV = auto()
    MODULO = auto()
    # TODO rest


OPERATORS = {
    TokenType.PLUS: ArithmeticOperator.PLUS,
    TokenType.MINUS: ArithmeticOperator.MINUS,
    TokenType.DIV: ArithmeticOperator.DIV,
    TokenType.MODULO: ArithmeticOperator.MODULO,

    TokenType.EQ: ComparisonOperator.EQ,
    TokenType.NEQ: ComparisonOperator.NEQ,
    TokenType.GTE: ComparisonOperator.GTE,
    TokenType.LTE: ComparisonOperator.LTE,
    TokenType.GT: ComparisonOperator.GT,
    TokenType.LT: ComparisonOperator.LT,
    # TODO rest
}