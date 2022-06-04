from enum import Enum, auto
from typing import Union

from src.lexer.token_type import TokenType

Value = str | int | float | bool | None


class Type:

    def __eq__(self, other):
        return type(self) == type(other)

    def __str__(self):
        return self.__class__.__name__


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

    def __eq__(self, other):
        if not hasattr(other, 'input_types') or not hasattr(other, 'output_type'):
            return False

        return self.input_types == other.input_types and self.output_type == other.output_type


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
    NOT = auto()


class ComparisonOperator(Enum):
    EQ = auto()
    NEQ = auto()
    GTE = auto()
    GT = auto()
    LTE = auto()
    LT = auto()


class ArithmeticOperator(Enum):
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    MODULO = auto()


class OtherOperator(Enum):
    NULL_COALESCE = auto()


OPERATORS = {
    TokenType.PLUS: ArithmeticOperator.PLUS,
    TokenType.MINUS: ArithmeticOperator.MINUS,
    TokenType.MUL: ArithmeticOperator.MUL,
    TokenType.DIV: ArithmeticOperator.DIV,
    TokenType.MODULO: ArithmeticOperator.MODULO,

    TokenType.EQ: ComparisonOperator.EQ,
    TokenType.NEQ: ComparisonOperator.NEQ,
    TokenType.GTE: ComparisonOperator.GTE,
    TokenType.LTE: ComparisonOperator.LTE,
    TokenType.GT: ComparisonOperator.GT,
    TokenType.LT: ComparisonOperator.LT,

    TokenType.AND: LogicOperator.AND,
    TokenType.OR: LogicOperator.OR,

    TokenType.NULL_COALESCE: OtherOperator.NULL_COALESCE
}
