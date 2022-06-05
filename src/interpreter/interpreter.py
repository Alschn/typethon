from typing import Any

from src.errors.interpreter import DivisionByZeroError, UnexpectedTypeError, UndefinedNameError, NotCallableError, \
    ArgumentsError, RecursionLimitError, ReturnException, NotNullableError, UninitializedConstError, \
    ConstRedeclarationError, ReturnTypeMismatchError, TypeMismatchError, ConstAssignmentError
from src.interpreter.environment import Environment
from src.interpreter.visitor import Visitor
from src.parser import Parser
from src.parser.objects.objects import (
    FunctionDefinition, ReturnStatement, FunctionCall, CompFactor, NegFactor,
    Factor, Literal, Identifier, Parameter, WhileLoopStatement, BinaryExpression, IfStatement, InlineReturnStatement,
    LambdaExpression, CompoundStatement, EmptyStatement, AssignmentStatement,
    DeclarationStatement, Variable, OrExpression, AndExpression
)
from src.parser.objects.program import Program
from src.parser.types import (
    Integer, Float, Null, LogicOperator, ArithmeticOperator, ComparisonOperator,
    OtherOperator,
    Bool, String, Void, Type
)

MAX_RECURSION_DEPTH = 100


# TODO:
# - type checking (argument types)
# - overwriting variables in higher scope (from inside while, function etc.)
# - builtins (bool, string, float, integer)
# - documentation
# - fix parser tests
# - interpreter unit tests


# noinspection PyMethodMayBeStatic
class Interpreter(Visitor):

    def __init__(self, parser: Parser):
        self.parser = parser
        self.env = None

    def interpret(self):
        """Interpreter's entrypoint. Prepares environment,
        asks parser to parse the program and then starts visiting it."""

        self.env = Environment()
        program = self.parser.parse_program()
        return self.visit(program)

    @property
    def binary_operations(self):
        """Operators mapped to method handling their behaviour."""

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

    def visit_Program(self, program: Program):
        """Visits all nodes in program."""

        for node in program.objects:
            self.visit(node)

    def visit_FunctionDefinition(self, func_def: FunctionDefinition):
        """Adds function definition to func table. Allows overwriting functions and shadowing builtins."""

        self.env.add_fun_def(func_def)

    def visit_WhileLoopStatement(self, while_loop_statement: WhileLoopStatement):
        """While condition is true, keeps visiting while loop's statement."""

        while cond := self.visit(while_loop_statement.condition):
            if cond.type != Bool() and cond.type != Null():
                raise UnexpectedTypeError(f'Expected condition to be type Bool or Null. Got {cond.type} instead.')

            if cond.value is False:
                break

            self.visit(while_loop_statement.body)

    def visit_IfStatement(self, if_statement: IfStatement):
        """Visits if statement node and its 'branches'. First it visits `if` condition. If it is true, visits a
        statement. Then visits all elifs the same way. Finally visits else statement if both if and all elif
        condition are false. Methods `visit_ElifStatement` and `visit_ElseStatement` are redundant."""

        if cond := self.visit(if_statement.condition):
            # condition has to be bool, otherwise it is a semantic error
            if cond.type != Bool() and cond.type != Null():
                raise UnexpectedTypeError(f'Expected condition to be type Bool or Null. Got {cond.type} instead.')

            if cond.value is True:
                self.visit(if_statement.statement)
                return

        # check if there are any elif statements, if so execute their conditions one by one
        # if condition happens to be true, then do not execute further
        # condition has to be bool, otherwise it is a semantic error
        for elif_stmt in if_statement.elif_statements:
            if cond := self.visit(elif_stmt.condition):
                if cond.type != Bool() and cond.type != Null():
                    raise UnexpectedTypeError(f'Expected condition to be type Bool or Null. Got {cond.type} instead.')

                if cond.value is True:
                    self.visit(elif_stmt.statement)
                    return

        # if there is an else statement, then it has to be executed unconditionally
        if if_statement.else_statement is not None:
            self.visit(if_statement.else_statement.statement)

    def visit_ReturnStatement(self, return_statement: ReturnStatement):
        """Visits return statement's expression and raises special exception, which is caught further in code."""

        if return_statement.expression is None:
            # empty return statement means that function returned void
            return_value = Literal(typ=Null(), value=None)
            raise ReturnException(return_value)

        return_value = self.visit(return_statement.expression)
        raise ReturnException(return_value)

    def visit_InlineReturnStatement(self, inline_return_statement: InlineReturnStatement):
        """Visits inline return statement's expression - same as normal return."""

        return_value = self.visit(inline_return_statement.expression)
        raise ReturnException(return_value)

    def visit_LambdaExpression(self, lambda_expr: LambdaExpression):
        """Visits LambdaExpression and returns expression itself."""
        return lambda_expr

    def visit_FunctionCall(self, func_call: FunctionCall):
        """Visits FunctionCall and executes a function or callable variable. Supports chained function calls."""

        fn_name = func_call.name
        func_def = self.env.get_fun_def(fn_name)
        lambda_var = self.env.get_variable(fn_name)

        if not func_def and not lambda_var:
            raise UndefinedNameError(fn_name)

        if lambda_var is not None and str(lambda_var.type) != "Func":
            raise NotCallableError(fn_name, lambda_var.type)

        if lambda_var:
            func_def = lambda_var.value

        return_type = getattr(func_def, 'return_type', 'type')

        # get arguments for function call from arguments stack
        index = 0
        args = func_call.arguments[index]
        # visit every argument from the list
        arguments = [self.visit(arg) for arg in args]

        if not (params := func_def.parameters):
            params = func_def.build_generic_parameters(arguments)

        if len(arguments) != len(params):
            raise ArgumentsError(fn_name, len(params), len(arguments))

        if self.env.fun_call_nesting >= MAX_RECURSION_DEPTH:
            raise RecursionLimitError()

        self.env.create_new_fun_scope(params, arguments)

        try:
            return_value = self.visit(func_def.body)

        except ReturnException as re:
            return_value = re.value_to_return
            # check if return_value is callable
            # and call it if there are more arguments on stack
            if new_return_value := self.chained_func_call_helper(return_value, index, func_call):
                return_value = new_return_value

        self.env.destroy_fun_scope()

        return self.type_check_return_type(fn_name, return_value, return_type)

    def type_check_return_type(self, fn_name: str, return_value: Any, return_type: Type):
        """Raises error if return_value is None but return type was not Void/Null,
        if types generally do not match. If error was not raised then type is valid."""

        if return_value is None and return_type != Null():
            raise ReturnTypeMismatchError(fn_name, return_type, Null())

        if return_value is None and return_type == Null():
            return Literal(typ=Null(), value=None)

        if return_value.type == Float() and return_type == Integer():
            # print(f"Warning casting float to integer in {fn_name}")
            return return_value

        if return_value.type != return_type:
            raise ReturnTypeMismatchError(fn_name, return_type, return_value.type)

        return return_value

    def chained_func_call_helper(self, return_value: Literal | LambdaExpression, index: int, func_call: FunctionCall):
        """Helper functions to keep on checking if returned value is callable
        and calling it if there are more arguments from original func_call arguments stack."""

        while index < len(func_call.arguments) - 1:
            match return_value:
                case LambdaExpression() | FunctionDefinition():
                    arguments = [self.visit(arg) for arg in func_call.arguments[index]]
                    generic_parameters = return_value.build_generic_parameters(return_value.parameters)
                    self.env.create_new_fun_scope(generic_parameters, arguments)
                    prev = return_value

                    try:
                        return_value = self.visit(return_value.body)
                        if new_ret := self.chained_func_call_helper(return_value, index + 1, func_call):
                            return self.type_check_return_type(
                                func_call.name + f"_inner_{index}",
                                new_ret,
                                return_value.return_type
                            )

                    except ReturnException as re:
                        return_value = re.value_to_return
                        if new_ret := self.chained_func_call_helper(return_value, index + 1, func_call):
                            return self.type_check_return_type(
                                func_call.name + f"_inner_{index}",
                                new_ret,
                                return_value.return_type
                            )

                    self.env.destroy_fun_scope()
                    return self.type_check_return_type(
                        func_call.name + f"_inner_{index}",
                        return_value,
                        prev.return_type
                    )

                case _:
                    raise NotCallableError('returned in function', typ=return_value.type)

    def visit_AssignmentStatement(self, assignment_statement: AssignmentStatement):
        """"""

        var_name = assignment_statement.name
        # TODO nullability, const/let
        if not (var := self.env.get_variable(var_name)):  # TODO assigning function
            raise Exception('Could not find variable to assign to.')

        # if variable is const, then there is no way to reassign value to it
        if not var.mutable:
            raise ConstAssignmentError(var_name)

        rvalue = self.visit(assignment_statement.right_value)

        # if variable not is nullable and rvalue is null
        if not var.nullable and rvalue.type == Null():
            raise NotNullableError(var_name)

        var.value = rvalue
        self.env.set_variable(assignment_statement.name, var)

    def visit_EmptyStatement(self, empty_statement: EmptyStatement):
        """Visits EmptyStatement and immediately returns None since there are no instructions to be run."""
        return

    def visit_CompoundStatement(self, compound_statement: CompoundStatement):
        """Visits CompoundStatement, which a list of statements, creating new local scope."""
        self.env.create_new_local_scope()

        for statement in compound_statement.statements:
            self.visit(statement)

        self.env.destroy_local_scope()

    def visit_DeclarationStatement(self, declaration_statement: DeclarationStatement):
        """Visits DeclarationStatement by visiting its left side with is always a Variable,
        and its right_side which can either be an expression reduced to literal/lambda or None."""

        variable = self.visit(declaration_statement.left_value)

        if rvalue := declaration_statement.right_value:

            value = self.visit(rvalue)
            match value.type:
                # Invalid cases:
                # const/let a: int = f();   // where f returns void
                # const/let a: int = null;
                # const/let a: int = nullable expression;
                case Null() | Void() if not variable.nullable:
                    raise NotNullableError(variable.name)

                # if there already is an immutable variable with the same name, cannot reassign value
                case _ if not variable.mutable and self.env.get_variable(variable.name):
                    raise ConstRedeclarationError(variable.name)

                case _:
                    # types match, or conversion from integer to float
                    if variable.type == value.type or (variable.type == Float() and value.type == Integer()):
                        variable.value = value
                        self.env.set_variable(variable.name, variable)
                        return

                    if variable.type != value.type:
                        raise TypeMismatchError(variable.name, variable.type, value.type)

        # const a?: int / const a: int;    <- const variable has to be initialized
        if not variable.mutable:
            raise UninitializedConstError(variable.name)

        # let a?: int;      <- mutable and nullable variable can be uninitialized
        if variable.nullable:
            variable.value = Literal(typ=Null(), value=None)
            self.env.set_variable(variable.name, variable)
            return

        # let a: int;       <- mutable variable has to be marked as nullable, otherwise lack of rvalue is an error
        raise NotNullableError(variable.name)

    def visit_BinaryExpression(self, expression: BinaryExpression):
        """Visits left and right sides, performs operation based on operator."""

        lvalue = self.visit(expression.left_value)
        operator = expression.operator
        rvalue = self.visit(expression.right_value)
        return self.binary_operations[operator](lvalue, rvalue)

    def visit_NullCoalesceExpression(self, expression):
        """"""
        return self.visit_BinaryExpression(expression)

    def visit_OrExpression(self, expression: OrExpression):
        """Visits OrExpression with the same logic as visit_BinaryExpression"""
        return self.visit_BinaryExpression(expression)

    def visit_AndExpression(self, expression: AndExpression):
        """Visits AndExpression with the same logic as visit_BinaryExpression"""
        return self.visit_BinaryExpression(expression)

    def visit_EqualityExpression(self, expression):
        """Visits EqualityExpression with the same logic as visit_BinaryExpression"""
        return self.visit_BinaryExpression(expression)

    def visit_AdditiveExpression(self, expression):
        """Visits AdditiveExpression with the same logic as visit_BinaryExpression"""
        return self.visit_BinaryExpression(expression)

    def visit_MultiplicativeExpression(self, expression):
        """Visits MultiplicativeExpression with the same logic as visit_BinaryExpression"""
        return self.visit_BinaryExpression(expression)

    def visit_CompFactor(self, comp_factor: CompFactor):
        """Visits CompFactor and potentially negates a result of factor visitation with logical `not`."""

        literal = self.visit(comp_factor.factor)

        if not comp_factor.negation:
            return literal

        return self.logic_not(literal)

    def visit_NegFactor(self, neg_factor: NegFactor):
        """Visits NegFactor and potentially negates a result of factor visitation with arithmetic `-`."""

        literal = self.visit(neg_factor.factor)

        if not neg_factor.minus:
            return literal

        return self.unary_minus(literal)

    def visit_Factor(self, factor: Factor):
        """Visits Factor which cases visitation of its value."""
        return self.visit(factor.value)

    def visit_Literal(self, literal: Literal):
        """Visits Literal and returns it."""
        return literal

    def visit_Identifier(self, identifier: Identifier):
        """Visits Identifier and tries to return a variable by its name in current scope or above."""

        if not (var := self.env.get_variable(identifier.name)):
            raise UndefinedNameError(identifier.name)

        return var.value

    def visit_Parameter(self, parameter: Parameter):
        """Visits Parameter and returns it."""
        return parameter

    def visit_Variable(self, variable: Variable):
        """Visits Variable and returns it."""
        return variable

    def visit_Print(self, builtin):
        """Visits builtin `print` function which prints any number of arguments."""

        values = []
        for param in builtin.parameters_list:
            values.append(self.env.get_variable(param.name).value)
        print(*values)

        builtin.parameter_list = None

    def visit_String(self, builtin):
        """Visits builtin `String` function which casts an argument to string type."""
        # TODO

    def visit_Boolean(self, builtin):
        """Visits builtin `Boolean` function which casts an argument to bool type."""
        # TODO

    def visit_Float(self, builtin):
        """Visits builtin `Float` function which casts an argument to float type."""
        # TODO

    def visit_Integer(self, builtin):
        """Visits builtin `Integer` function which casts an argument to string type."""
        # TODO

    def unary_minus(self, factor):
        """Negates an integer/float. Not allowed for other types."""

        match factor:
            case Literal(type=Integer()) | Literal(type=Float()):
                factor.value *= -1
                return factor

            case _:
                raise Exception('Unsupported operation for operator `-`.')

    def logic_not(self, factor):
        """Does logic negation. Allowed only for booleans."""

        if factor.type != Bool():
            raise UnexpectedTypeError(f"Expected type Bool. Got {factor.type} instead.")

        return Literal(typ=Bool(), value=not factor.value)

    def logic_or(self, left_side: Any, right_side: Any):
        """Does logic alternative. Allowed only for booleans."""

        if left_side.type != Bool() and right_side.type != Bool():
            raise UnexpectedTypeError(f"Expected types Bool Bool. Got {left_side.type} {right_side.type} instead.")

        return Literal(typ=Bool(), value=left_side.value or right_side.value)

    def logic_and(self, left_side: Any, right_side: Any):
        """Does logic conjunction. Allowed only for booleans."""

        if left_side.type != Bool() and right_side.type != Bool():
            raise UnexpectedTypeError(f"Expected types Bool Bool. Got {left_side.type} {right_side.type} instead.")

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
                raise UnexpectedTypeError(f"Cannot add type {left_side.type} to type {right_side.type}")

    def sub(self, left_side: Any, right_side: Any) -> Literal:
        """Calculates difference of two sides. Allowed only for integers and floats."""

        match left_side.type:
            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Float(), value=left_side.value - right_side.value)

            case _:
                raise UnexpectedTypeError(f"Cannot subtract type {right_side.type} from type {left_side.type}")

    def mul(self, left_side: Any, right_side: Any):
        """Calculates product of two sides. Allowed only for integers and floats."""

        match left_side.type:
            case Integer() if right_side.type == Integer():
                return Literal(typ=Integer(), value=left_side.value * right_side.value)

            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Float(), value=left_side.value * right_side.value)

            case _:
                raise UnexpectedTypeError(f"Cannot multiply type {left_side.type} with type {right_side.type}")

    def div(self, left_side: Any, right_side: Any):
        """Calculates quotient of two sides. Allowed only for integers and floats."""

        if right_side.value == 0:
            raise DivisionByZeroError()

        match left_side.type:
            case Integer() if right_side.type == Integer():
                return Literal(typ=Integer(), value=left_side.value / right_side.value)

            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Float(), value=left_side.value / right_side.value)

            case _:
                raise UnexpectedTypeError(f"Cannot divide type {left_side.type} by type {right_side.type}")

    def modulo(self, left_side: Any, right_side: Any) -> Literal:
        """Calculates modulo of two sides. Allowed only for integers and floats."""

        if right_side.value == 0:
            raise DivisionByZeroError()

        match left_side.type:
            case Integer() if right_side.type == Integer():
                return Literal(typ=Integer(), value=left_side.value % right_side.value)

            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Float(), value=left_side.value % right_side.value)

            case _:
                raise UnexpectedTypeError(f"Cannot divide type {left_side.type} by type {right_side.type}")

    def less(self, left_side: Any, right_side: Any) -> Literal:
        """Checks if left_side is lesser than right_side. Allowed only for integers and floats."""

        match left_side.type:
            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Bool(), value=left_side.value < right_side.value)

            case _:
                raise UnexpectedTypeError(f'Cannot check if type {left_side.type} is less than type {right_side.type}')

    def greater(self, left_side: Any, right_side: Any) -> Literal:
        """Checks if left_side is greater than right_side. Allowed only for integers and floats."""

        match left_side.type:
            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Bool(), value=left_side.value > right_side.value)

            case _:
                raise UnexpectedTypeError(
                    f'Cannot check if type {left_side.type} is greater than type {right_side.type}')

    def less_or_equal(self, left_side: Any, right_side: Any) -> Literal:
        """Checks if left_side is lesser than or equal to right_side. Allowed only for integers and floats."""

        match left_side.type:
            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Bool(), value=left_side.value <= right_side.value)

            case _:
                raise UnexpectedTypeError(
                    f'Cannot check if type {left_side.type} is less than or equal type {right_side.type}')

    def greater_or_equal(self, left_side: Any, right_side: Any) -> Literal:
        """Checks if left_side is greater than or equal to right_side. Allowed only for integers and floats."""

        match left_side.type:
            case Integer() | Float() if right_side.type == Integer() or right_side.type == Float():
                return Literal(typ=Bool(), value=left_side.value >= right_side.value)

            case _:
                raise UnexpectedTypeError(
                    f'Cannot check if type {left_side.type} is greater than or equal type {right_side.type}')

    def equal(self, left_side: Any, right_side: Any) -> Literal:
        """Checks if left_side is equal to right_side. Allowed for string, integer, float, bool, null."""

        if str(left_side.type) == "Func" or str(right_side.type) == "Func":
            raise UnexpectedTypeError(f"Cannot check if type {left_side.type} equals type {right_side.type}")

        elif left_side.type == Null() and right_side.type != Null():
            return Literal(typ=Bool(), value=True)

        elif left_side.type != Null() and right_side.type == Null():
            return Literal(typ=Bool(), value=True)

        elif left_side.type == Null() and right_side.type == Null():
            return Literal(typ=Bool(), value=True)

        # elif left_side.type == Void() or right_side.type == Void():
        #     raise UnexpectedTypeError(f"Cannot check if type {left_side.type} equals type {right_side.type}")

        return Literal(typ=Bool(), value=left_side.value == right_side.value)

    def not_equal(self, left_side: Any, right_side: Any) -> Literal:
        """Checks if left_side is not equal to right_side. Allowed for string, integer, float, bool, null."""

        if str(left_side.type) == "Func" or str(right_side.type) == "Func":
            raise UnexpectedTypeError(f"Cannot check if type {left_side.type} doesn't equal type {right_side.type}")

        elif left_side.type == Null() and right_side.type == Null():
            return Literal(typ=Bool(), value=False)

        elif left_side.type != Null() and right_side.type == Null():
            return Literal(typ=Bool(), value=True)

        elif left_side.type == Null() and right_side.type != Null():
            return Literal(typ=Bool(), value=True)

        # elif left_side.type == Void() or right_side.type == Void():
        #     raise UnexpectedTypeError(f"Cannot check if type {left_side.type} doesn't equal type {right_side.type}")

        return Literal(typ=Bool(), value=left_side.value != right_side.value)

    def null_coalesce(self, left_side: Any, right_side: Any) -> Literal:
        """Returns left_side if it is not null, otherwise right_side."""

        match left_side.type:
            case Null() | Void():
                return right_side

            case _:
                return left_side
