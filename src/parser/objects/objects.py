import uuid
from typing import Any, Optional

from src.parser.types import Type, Value, Func


class Statement:
    pass


class Expression:
    pass


class Literal(Expression):

    def __init__(self, typ: Type, value: Value):
        self.type = typ
        self.value = value


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

    def __init__(self, name: str, return_type: Any, parameters: list = None, body=None, builtin=False):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters or []
        self.body = body
        self._builtin = builtin

        self.type = Func(return_type=return_type, arguments_types=parameters)

    def build_generic_parameters(self, arguments):
        parameters = []

        if self._builtin:
            self.body.parameters_list = parameters

        # chr(97) == 'a'
        for i, _ in enumerate(arguments):
            parameters.append(Identifier(chr(97 + i)))

        return parameters


class LambdaExpression(Expression):

    def __init__(self, return_type: Any, arguments: list = None, body: Any = None):
        self.name = str(uuid.uuid4())
        self.return_type = return_type
        self.parameters = arguments or []
        self.body = body

        self.type = Func(return_type=return_type, arguments_types=arguments)

    def build_generic_parameters(self, arguments):
        return arguments


class FunctionCall(Expression):

    def __init__(self, name: str, arguments: list):
        self.name = name
        self.arguments = arguments


class AssignmentStatement(Statement):

    def __init__(self, name: str, right_value: Expression):
        self.name = name
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

    def __init__(self, neg_factor: Expression, negation: bool):
        self.factor = neg_factor
        self.negation = negation


class AdditiveExpression(BinaryExpression):
    pass


class MultiplicativeExpression(BinaryExpression):
    pass


class NegFactor(Expression):

    def __init__(self, factor: Expression, minus: bool):
        self.factor = factor
        self.minus = minus


class Factor(Expression):

    def __init__(self, value: Expression):
        self.value = value


class Variable(Expression):

    def __init__(self, name: str, typ: Type, nullable: bool = False, mutable: bool = True):
        self.name = name
        self.type = typ

        # set by parser - controlled by interpreter
        self.nullable = nullable
        self.mutable = mutable

        # set and controlled by interpreter
        self.value = None


class Identifier(Expression):

    def __init__(self, name: str):
        self.name = name


class Parameter(Expression):

    def __init__(self, name: str, typ: Type, nullable: bool = False, mutable: bool = True):
        self.name = name
        self.type = typ
        self.nullable = nullable
        # parameter's mutability is determined by variable's mutability
        self.mutable = mutable
