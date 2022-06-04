from typing import Any

from src.interpreter.visitor import Visitor
from src.parser import Parser
from src.parser.objects.objects import (
    FunctionDefinition, ReturnStatement, FunctionCall, CompFactor, NegFactor,
    Factor, Literal, Identifier, Parameter, WhileLoopStatement, BinaryExpression, ElseStatement, ElifStatement,
    IfStatement, InlineReturnStatement, LambdaExpression
)
from src.parser.objects.program import Program
from src.parser.types import (
    Integer, Float, Null, LogicOperator, ArithmeticOperator, ComparisonOperator,
    OtherOperator,
    Bool, String, Void, Func
)


# noinspection PyMethodMayBeStatic
class Interpreter(Visitor):

    def __init__(self, parser: Parser):
        self.parser = parser

        self.func_defs = ["print"]

        self.binary_operations = self._get_binary_operation()
        self.unary_operations = self._get_unary_operation()

    def interpret(self):
        """Interpreter's entrypoint"""

        program = self.parser.parse_program()
        return self.visit(program)

    def _get_binary_operation(self):
        return {
            LogicOperator.AND: self.logic_and,
            LogicOperator.OR: self.logic_or,
            ArithmeticOperator.DIV: self.div,
            ArithmeticOperator.MODULO: self.modulo,
            ArithmeticOperator.PLUS: self.add,
            ArithmeticOperator.MINUS: self.sub,
            ArithmeticOperator.MUL: self.mul,
            ComparisonOperator.LT: self.less,
            ComparisonOperator.GT: self.greater,
            ComparisonOperator.LTE: self.less_or_equal,
            ComparisonOperator.GTE: self.greater_or_equal,
            ComparisonOperator.EQ: self.equal,
            ComparisonOperator.NEQ: self.not_equal,
            OtherOperator.NULL_COALESCE: self.null_coalesce
        }

    def _get_unary_operation(self):
        return {
            ArithmeticOperator.MINUS: self.unary_minus,
            LogicOperator.NOT: self.logic_not,
        }

    def visit_Program(self, program: Program):
        """Visits all nodes in program."""

        for node in program.objects:
            self.visit(node)

    def visit_FunctionDefinition(self, func_def: FunctionDefinition):
        """"""
        return

    def visit_WhileLoopStatement(self, while_loop_statement: WhileLoopStatement):
        """"""

        while self.visit(while_loop_statement.condition):
            self.visit(while_loop_statement.body)

    def visit_IfStatement(self, if_statement: IfStatement):
        """"""
        return

    def visit_ElifStatement(self, elif_statement: ElifStatement):
        """"""
        return

    def visit_ElseStatement(self, else_statement: ElseStatement):
        """"""
        return

    def visit_ReturnStatement(self, return_statement: ReturnStatement):
        """"""
        return

    def visit_InlineReturnStatement(self, inline_return_statement: InlineReturnStatement):
        """"""
        return

    def visit_LambdaExpression(self, lambda_expr: LambdaExpression):
        """"""
        return

    def visit_FunctionCall(self, func_call: FunctionCall):
        """"""

        func_name = func_call.name
        # todo: check if name is in function table
        #       or name in variables and variable is callable

        if func_name in self.func_defs:
            # get arguments for function call
            # visit every argument
            args = func_call.arguments.pop()
            arguments = [self.visit(arg) for arg in args]

            # cast_arguments = list(map(lambda x: str(x.value), arguments))
            returned_value = self.call_fn("print", arguments)

            # chained function call
            while len(func_call.arguments):
                match returned_value:
                    case None:
                        raise Exception('Object is not callable!')

                    case _:
                        args = func_call.arguments.pop()
                        # if returned_value.type != Func() then raise Error

                        arguments = [self.visit(arg) for arg in args]
                        # call function
                        returned_value = None

            return returned_value

    # remove later
    def call_fn(self, fn_name, args):
        if fn_name == "print":
            # string = " ".join(args)
            mapped = list(map(lambda x: (x.value, x.type), args))
            print(*mapped)
            return Literal(typ=Null(), value=None)

        return Func([], Void())

    def visit_AssignmentStatement(self, assignment_statement):
        """"""
        return

    def visit_EmptyStatement(self, empty_statement):
        """"""
        return

    def visit_CompoundStatement(self, compound_statement):
        """"""

        for statement in compound_statement:
            self.visit(statement)

    def visit_DeclarationStatement(self, declaration_statement):
        """"""
        return

    def visit_BinaryExpression(self, expression: BinaryExpression):
        """Visits left and right sides, performs operation based on operator."""

        lvalue = self.visit(expression.left_value)
        operator = expression.operator
        rvalue = self.visit(expression.right_value)
        return self.binary_operations[operator](lvalue, rvalue)

    def visit_NullCoalesceExpression(self, expression):
        """"""
        return self.visit_BinaryExpression(expression)

    def visit_OrExpression(self, expression):
        """"""
        return self.visit_BinaryExpression(expression)

    def visit_AndExpression(self, expression):
        """"""
        return self.visit_BinaryExpression(expression)

    def visit_EqualityExpression(self, expression):
        """"""
        return self.visit_BinaryExpression(expression)

    def visit_AdditiveExpression(self, expression):
        """"""
        return self.visit_BinaryExpression(expression)

    def visit_MultiplicativeExpression(self, expression):
        """"""
        return self.visit_BinaryExpression(expression)

    def visit_CompFactor(self, comp_factor: CompFactor):
        """"""
        negate_not = comp_factor.negation
        node = self.visit(comp_factor.factor)

        if not negate_not:
            return node

        return self.logic_not(node)

    def visit_NegFactor(self, neg_factor: NegFactor):
        """"""
        negate_minus = neg_factor.minus
        node = self.visit(neg_factor.factor)

        if not negate_minus:
            return node

        return self.unary_minus(node)

    def visit_Factor(self, factor: Factor):
        """"""
        return self.visit(factor.value)

    def visit_Literal(self, literal: Literal):
        """"""
        return literal

    def visit_Identifier(self, identifier: Identifier):
        # TODO find variable and return its value

        return identifier

    def visit_Parameter(self, parameter: Parameter):

        return parameter

    def unary_minus(self, factor):
        """Negates integer/float. Not allowed for other types."""

        match factor:
            case Literal(type=Integer()) | Literal(type=Float()):
                factor.value *= -1
                return factor

            case _:
                raise Exception('Unsupported operation for operator `-`.')

    def logic_not(self, factor):
        """Does logic negation. Allowed only for booleans."""

        if factor.type != Bool():
            raise Exception(f"Expected boolean")

        return Literal(typ=Bool(), value=not factor.value)

    def logic_or(self, left_side: Any, right_side: Any):
        """Does logic alternative. Allowed only for booleans."""

        if left_side.type != Bool() and right_side.type != Bool():
            raise Exception(f"Expected boolean")

        return Literal(typ=Bool(), value=left_side.value or right_side.value)

    def logic_and(self, left_side: Any, right_side: Any):
        """Does logic conjunction. Allowed only for booleans."""

        if left_side.type != Bool() and right_side.type != Bool():
            raise Exception(f"Expected boolean")

        return Literal(typ=Bool(), value=left_side.value and right_side.value)

    def add(self, left_side: Any, right_side: Any) -> Literal:
        """Adds two sides (sums numbers or concatenates strings).
        Allowed only for integers, floats, strings."""

        match left_side.type:
            case Integer() if right_side.type == Integer():
                return Literal(typ=Integer(), value=left_side.value + right_side.value)

            case Integer() if right_side.type == Float():
                return Literal(typ=Float(), value=left_side.value + right_side.value)

            case Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Float(), value=left_side.value + right_side.value)

            case String() if right_side.type == String():
                return Literal(typ=String(), value=left_side.value + right_side.value)

            case _:
                raise Exception(f"Cannot add type {left_side.type} to type {right_side.type}")

    def sub(self, left_side: Any, right_side: Any) -> Literal:
        """Calculates difference of two sides.
        Allowed only for integers and floats"""

        match left_side.type:
            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Float(), value=left_side.value - right_side.value)

            case _:
                raise Exception(f"Cannot subtract type {right_side.type} from type {left_side.type}")

    def mul(self, left_side: Any, right_side: Any):
        """Calculates product of two sides.
        Allowed only for integers and floats"""

        match left_side.type:
            case Integer() if right_side.type == Integer():
                return Literal(typ=Integer(), value=left_side.value * right_side.value)

            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Float(), value=left_side.value * right_side.value)

            case _:
                raise Exception(f"Cannot multiply type {left_side.type} with type {right_side.type}")

    def div(self, left_side: Any, right_side: Any):
        """Calculates quotient of two sides. Allowed only for integers and floats"""

        if right_side.value == 0:
            raise ZeroDivisionError()

        match left_side.type:
            case Integer() if right_side.type == Integer():
                return Literal(typ=Integer(), value=left_side.value / right_side.value)

            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Float(), value=left_side.value / right_side.value)

            case _:
                raise Exception(f"Cannot divide type {left_side.type} by type {right_side.type}")

    def modulo(self, left_side: Any, right_side: Any) -> Literal:
        """Calculates modulo of two sides. Allowed only for integers and floats"""

        if right_side.value == 0:
            raise ZeroDivisionError()

        match left_side.type:
            case Integer() if right_side.type == Integer():
                return Literal(typ=Integer(), value=left_side.value / right_side.value)

            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Float(), value=left_side.value / right_side.value)

            case _:
                raise Exception(f"Cannot divide type {left_side.type} by type {right_side.type}")

    def less(self, left_side: Any, right_side: Any) -> Literal:
        """"""

        match left_side.type:
            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Bool(), value=left_side.value < right_side.value)

            case _:
                raise Exception(f'Cannot check if type {left_side.type} is less than type {right_side.type}')

    def greater(self, left_side: Any, right_side: Any) -> Literal:
        """"""

        match left_side.type:
            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Bool(), value=left_side.value > right_side.value)

            case _:
                raise Exception(f'Cannot check if type {left_side.type} is greater than type {right_side.type}')

    def less_or_equal(self, left_side: Any, right_side: Any) -> Literal:
        """"""

        match left_side.type:
            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Bool(), value=left_side.value <= right_side.value)

            case _:
                raise Exception(f'Cannot check if type {left_side.type} is less than or equal type {right_side.type}')

    def greater_or_equal(self, left_side: Any, right_side: Any) -> Literal:
        """"""

        match left_side.type:
            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Bool(), value=left_side.value >= right_side.value)

            case _:
                raise Exception(
                    f'Cannot check if type {left_side.type} is greater than or equal type {right_side.type}')

    def equal(self, left_side: Any, right_side: Any) -> Literal:
        """Checks if left_side is equal to right_side.
        Allowed for string, integer, float, bool, null."""

        # todoo rewrite this condition
        if str(left_side.type) == "Func" or str(right_side.type) == "Func":
            raise Exception("Unsupported operation for type func")

        elif left_side.type == Void() or right_side.type == Void():
            raise Exception("Unsupported operation for type void")

        return Literal(typ=Bool(), value=left_side.value == right_side.value)

    def not_equal(self, left_side: Any, right_side: Any) -> Literal:
        """Checks if left_side is not equal to right_side.
        Allowed for string, integer, float, bool, null."""

        # todoo rewrite this condition
        if str(left_side.type) == "Func" or str(right_side.type) == "Func":
            raise Exception("Unsupported operation for type func")

        elif left_side.type == Void() or right_side.type == Void():
            raise Exception("Unsupported operation for type void")

        return Literal(typ=Bool(), value=left_side.value != right_side.value)

    def null_coalesce(self, left_side: Any, right_side: Any) -> Literal:
        """Returns left_side if it is not null, otherwise right_side"""

        match left_side:
            case Literal(type=Null()) | Literal(type=Void()):
                return right_side

            case _:
                return left_side
