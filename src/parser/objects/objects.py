import uuid
from typing import Any, Optional

from src.parser.types import Type, Value


class Statement:
    pass


class Expression:
    pass


class WhileLoopStatement(Statement):
    def __init__(self, condition: Expression, body: "CompoundStatement"):
        self.condition = condition
        self.body = body


class IfStatement(Statement):
    def __init__(
            self,
            condition_expr: Expression, statement: Any,
            elif_statements: list["ElifStatement"] = None,
            else_statement: "ElseStatement" = None
    ):
        self.condition = condition_expr
        self.statement = statement
        self.elif_statements = elif_statements or []
        self.else_statement = else_statement


class ElifStatement(Statement):
    def __init__(self, condition_expr: Expression, statement: Any):
        self.condition = condition_expr
        self.statement = statement


class ElseStatement(Statement):
    def __init__(self, statement: Any):
        self.statement = statement


class ReturnStatement(Statement):
    def __init__(self, return_expr: Optional[Expression]):
        self.expression = return_expr


class InlineReturnStatement(ReturnStatement):
    pass


class FunctionDefinition(Statement):
    def __init__(self, name: str, return_type: Any, arguments: list = None, body=None):
        self.name = name
        self.return_type = return_type
        self.arguments = arguments
        self.body = body


class LambdaExpression(Expression):

    def __init__(self, return_type: Any, arguments: list = None, body: Any = None):
        self.name = str(uuid.uuid4())
        self.return_type = return_type
        self.arguments = arguments
        self.body = body


class FunctionCall(Expression):

    def __init__(self, name: str, arguments: list):
        self.name = name
        self.arguments = arguments


class AssignmentStatement(Statement):

    def __init__(self, symbol: str, right_value: Expression):
        self.symbol = symbol
        self.right_value = right_value


class EmptyStatement(Statement):
    pass


class CompoundStatement(Statement):

    def __init__(self, statements: list[Statement]):
        self.statements = statements


class DeclarationStatement(Statement):

    def __init__(self, left_value: "Variable", right_value: Optional[Expression]):
        self.left_value = left_value
        self.right_value = right_value


class BinaryExpression(Expression):

    def __init__(self, left_value: Expression, operator: Any, right_value: Expression):
        self.left_value = left_value
        self.operator = operator
        self.right_value = right_value


class NullCoalesceExpression(BinaryExpression):
    pass


class OrExpression(BinaryExpression):
    pass


class AndExpression(BinaryExpression):
    pass


class EqualityExpression(BinaryExpression):
    pass


class CompFactor(Expression):

    def __init__(self, factor: Expression, negation: bool):
        self.factor = factor
        self.negation = negation


class AdditiveExpression(BinaryExpression):
    pass


class MultiplicativeExpression(BinaryExpression):
    pass


class Factor(Expression):
    def __init__(self, value: Expression, minus: bool):
        self.value = value
        self.minus = minus


class Variable(Expression):

    def __init__(self, name: str, typ: Type, nullable: bool = False, mutable: bool = True):
        self.name = name
        self.type = typ
        self.nullable = nullable
        self.mutable = mutable


class Identifier(Expression):

    def __init__(self, name: str):
        self.name = name


class Literal(Expression):

    def __init__(self, typ: Type, value: Value):
        self.type = typ
        self.value = value


class Parameter(Expression):

    def __init__(self, symbol: str, typ: Type, nullable: bool = False, mutable: Optional[bool] = None):
        self.symbol = symbol
        self.type = typ
        self.nullable = nullable
        # parameter's mutability is determined by variable's mutability
        self.mutable = mutable
