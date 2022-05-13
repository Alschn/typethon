from typing import Optional, Sequence, Union

from src.errors.error import (
    UninitializedConstError, NotNullableError, UnexpectedTokenError,
    InvalidReturnTypeError, InvalidRightExpressionError,
    MissingParameterError, MissingArgumentError, MissingLambdaExpressionBody
)
from src.lexer.lexer import Lexer
from src.lexer.token import Token
from src.lexer.token_type import TokenType
from src.parser.objects.objects import (
    WhileLoopStatement, IfStatement, ElseStatement, ElifStatement, ReturnStatement,
    FunctionCall, FunctionDefinition, CompoundStatement, EmptyStatement, DeclarationStatement,
    AssignmentStatement, CompFactor, BinaryExpression, Expression, Parameter, Statement, Variable,
    NullCoalesceExpression, OrExpression, AndExpression, AdditiveExpression, MultiplicativeExpression, Literal, Factor,
    Identifier, EqualityExpression, LambdaExpression
)
from src.parser.objects.program import Program
from src.parser.types import TYPES_MAPPING, Type, Func

VAR_TYPES = {TokenType.STR, TokenType.INT, TokenType.FLOAT, TokenType.BOOL, TokenType.FUNC}
RETURN_TYPES = {*VAR_TYPES, TokenType.VOID}
ADD_OPERATORS = {}
MULT_OPERATORS = {}
COMP_OPERATORS = {}
EQ_OPERATORS = {}
LITERALS = [
    TokenType.INT_VALUE, TokenType.FLOAT_VALUE, TokenType.STR_VALUE,
    TokenType.TRUE_VALUE, TokenType.FALSE_VALUE, TokenType.NULL_VALUE
]


class Parser:

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.lexer.build_next_token()

    def parse_program(self) -> Program:
        """Parser's main method - tries to parse ProgramStatement in a loop"""

        top_level_objects = []

        while statement_object := self.try_parse_program_statement():
            top_level_objects.append(statement_object)

        self.expect_and_consume(TokenType.ETX)

        return Program(top_level_objects)

    def try_parse_program_statement(self):
        """Tries to parse either FunctionDefinition or Statement"""

        if func_def := self.try_parse_func_def():
            return func_def

        elif statement := self.try_parse_statement():
            return statement

        return None

    def try_parse_func_def(self) -> Optional[FunctionDefinition]:
        """Tries to parse FuncDef.
        Returns FunctionDefinition object if succeeds, else None"""

        if not self.check_and_consume(TokenType.DEF):
            return None

        id_token = self.expect_and_consume(TokenType.ID)
        self.expect_and_consume(TokenType.LPAREN)

        parameters = self.try_parse_parameters()

        self.expect_and_consume(TokenType.RPAREN)
        self.expect_and_consume(TokenType.TYPE_ASSIGN)

        return_type = self.try_parse_return_type()

        self.expect_and_consume(TokenType.ARROW)

        func_body = self.try_parse_func_body()

        return FunctionDefinition(
            name=id_token.value,
            arguments=parameters,
            return_type=return_type,
            body=func_body
        )

    def try_parse_return_type(self) -> Type:
        """"""

        if token := self.check_and_consume(TokenType.VOID):
            return TYPES_MAPPING[token.type]()

        if var_type := self.try_parse_var_type():
            return var_type

        raise InvalidReturnTypeError(token)

    def try_parse_func_body(self) -> Optional[Statement]:
        """"""

        if body := self.try_parse_body():
            return body

        # try_parse_expression  # TODO later

        raise MissingLambdaExpressionBody(self.lexer.token)

    def try_parse_parameters(self) -> list[Parameter]:
        """"""

        parameter = self.try_parse_parameter()
        if parameter is None:
            return []

        params = [parameter]
        while self.check_and_consume(TokenType.COMMA):

            if not (param := self.try_parse_parameter()):
                raise MissingParameterError(self.lexer.token)

            params.append(param)

        return params

    def try_parse_parameter(self) -> Optional[Parameter]:
        """"""

        if not (id_token := self.check_and_consume(TokenType.ID)):
            return None

        assign_token = self.expect_one_of_many_and_consume(
            [TokenType.TYPE_ASSIGN, TokenType.TYPE_ASSIGN_NULLABLE]
        )
        param_type = self.try_parse_var_type()
        nullable = assign_token == TokenType.TYPE_ASSIGN_NULLABLE

        return Parameter(
            symbol=id_token.value, typ=param_type,
            nullable=nullable, mutable=None
        )

    def try_parse_var_type(self) -> Type:
        """"""

        if func_type := self.try_parse_func_type():
            return func_type

        prev_token = self.expect_one_of_many_and_consume(
            [TokenType.STR, TokenType.INT, TokenType.FLOAT, TokenType.BOOL]
        )
        typ = TYPES_MAPPING[prev_token.type]
        return typ

    def try_parse_func_type(self) -> Optional[Func]:
        """"""
        if not self.check_and_consume(TokenType.FUNC):
            return None

        self.expect_and_consume(TokenType.LPAREN)
        self.expect_and_consume(TokenType.LPAREN)

        arguments_list = self.try_parse_parameters()

        self.expect_and_consume(TokenType.RPAREN)
        self.expect_and_consume(TokenType.ARROW)

        return_type = self.try_parse_return_type()

        self.expect_and_consume(TokenType.RPAREN)

        return Func(arguments_types=arguments_list, return_type=return_type)

    def try_parse_body(self) -> Union[None, EmptyStatement, CompoundStatement]:
        """"""

        if not self.check_and_consume(TokenType.LCURLY):
            return None

        if self.check_and_consume(TokenType.RCURLY):
            return EmptyStatement()

        statements = []
        while statement := self.try_parse_statement():
            statements.append(statement)

        self.expect_and_consume(TokenType.RCURLY)

        return CompoundStatement(statements=statements)

    def try_parse_statement(self):
        """"""

        for try_parse in [
            self.try_parse_conditional,
            self.try_parse_while_loop,
            self.try_parse_body,
            self.try_parse_declaration,
            self.try_parse_statement_short,
        ]:
            if statement := try_parse():
                return statement
        return None

    def try_parse_statement_short(self):
        """"""

        if return_statement := self.try_parse_return():
            return return_statement

        if id_operation := self.try_parse_id_operation():
            return id_operation

        return None

    def try_parse_id_operation(self):
        """"""

        if not (id_token := self.check_and_consume(TokenType.ID)):
            return None

        if assignment := self.try_parse_assignment(id_token.value):
            self.expect_and_consume(TokenType.SEMI)
            return assignment

        if func_call := self.try_parse_func_call(id_token.value):
            self.expect_and_consume(TokenType.SEMI)
            return func_call

        return None

    def try_parse_assignment(self, var_name: str) -> Optional[AssignmentStatement]:
        """"""

        if not self.check_and_consume(TokenType.ASSIGN):
            return None

        expression = self.try_parse_expression()

        return AssignmentStatement(var_name, expression)

    def try_parse_declaration(self) -> Optional[DeclarationStatement]:
        """"""

        if not (declare_token := self.check_one_of_many_and_consume([TokenType.CONST, TokenType.LET])):
            return None

        id_token = self.expect_and_consume(TokenType.ID)
        assign_token = self.expect_one_of_many_and_consume(
            [TokenType.TYPE_ASSIGN, TokenType.TYPE_ASSIGN_NULLABLE]
        )
        mutable = declare_token.type == TokenType.LET
        nullable = assign_token.type == TokenType.TYPE_ASSIGN_NULLABLE
        var_type = self.try_parse_var_type()

        variable = Variable(id_token.value, var_type, nullable, mutable)

        if self.check_and_consume(TokenType.ASSIGN):
            expression = self.try_parse_expression()
            statement = DeclarationStatement(variable, expression)
            self.expect_and_consume(TokenType.SEMI)
            return statement

        # variables can be uninitialized only if they are declared with `let`
        # and described as nullable with `?:`
        if not mutable:
            raise UninitializedConstError(current_token=self.lexer.token)

        if not nullable:
            raise NotNullableError(assign_token.position)

        self.expect_and_consume(TokenType.SEMI)
        return DeclarationStatement(variable, None)

    def try_parse_while_loop(self) -> Optional[WhileLoopStatement]:
        """"""

        if not self.check_and_consume(TokenType.WHILE):
            return None

        self.expect_and_consume(TokenType.LPAREN)

        expr = self.try_parse_expression()

        self.expect_and_consume(TokenType.RPAREN)

        body = self.try_parse_body()

        return WhileLoopStatement(condition=expr, body=body)

    def try_parse_func_call(self, func_name: str) -> Optional[FunctionCall]:
        """"""

        if not self.check_and_consume(TokenType.LPAREN):
            return None

        args = self.try_parse_arguments()
        arguments = [args]

        self.expect_and_consume(TokenType.RPAREN)

        while self.check_and_consume(TokenType.LPAREN):
            args = self.try_parse_arguments()
            self.expect_and_consume(TokenType.RPAREN)
            arguments.append(args)

        return FunctionCall(func_name, arguments)

    def try_parse_arguments(self):
        if not (expr := self.try_parse_expression()):
            return []

        expressions = [expr]
        while self.check_and_consume(TokenType.COMMA):

            if not (expr := self.try_parse_expression()):
                raise MissingArgumentError(self.lexer.token)

            expressions.append(expr)

        return expressions

    def try_parse_return(self) -> Optional[ReturnStatement]:
        """"""

        if not self.check_and_consume(TokenType.RETURN):
            return None

        if not (expression := self.try_parse_expression()):
            self.expect_and_consume(TokenType.SEMI)
            return ReturnStatement(return_expr=None)

        self.expect_and_consume(TokenType.SEMI)
        return ReturnStatement(return_expr=expression)

    def try_parse_conditional(self) -> Optional[IfStatement]:
        """ """

        if not self.check_and_consume(TokenType.IF):
            return None

        self.expect_and_consume(TokenType.LPAREN)

        expr = self.try_parse_expression()

        self.expect_and_consume(TokenType.RPAREN)

        if_statement = self.try_parse_statement()

        elif_statements = []
        while elif_statement := self.try_parse_elif_statement():
            elif_statements.append(elif_statement)

        else_statement = self.try_parse_else_statement()

        return IfStatement(
            condition_expr=expr, statement=if_statement,
            elif_statements=elif_statements,
            else_statement=else_statement
        )

    def try_parse_elif_statement(self) -> Optional[ElifStatement]:
        """"""

        if not self.check_and_consume(TokenType.ELIF):
            return None

        self.expect_and_consume(TokenType.LPAREN)

        expr = self.try_parse_expression()

        self.expect_and_consume(TokenType.RPAREN)

        statement = self.try_parse_statement()

        return ElifStatement(condition_expr=expr, statement=statement)

    def try_parse_else_statement(self) -> Optional[ElseStatement]:
        """"""

        if not self.check_and_consume(TokenType.ELSE):
            return None

        statement = self.try_parse_statement()

        return ElseStatement(statement=statement)

    def try_parse_expression(self) -> Optional[Expression]:
        """"""

        left_expr = self.try_parse_null_coalesce_expression()

        while operator := self.check_and_consume(TokenType.NULL_COALESCE):

            if not (expr := self.try_parse_null_coalesce_expression()):
                raise InvalidRightExpressionError(self.lexer.token)

            left_expr = BinaryExpression(
                left_expr, operator, expr
            )

        return left_expr

    def try_parse_null_coalesce_expression(self) -> Optional[Expression]:
        """"""

        left_expr = self.try_parse_or_expression()

        while operator := self.check_and_consume(TokenType.OR):

            if not (expr := self.try_parse_or_expression()):
                raise InvalidRightExpressionError(self.lexer.token)

            left_expr = NullCoalesceExpression(
                left_expr, operator, expr
            )

        return left_expr

    def try_parse_or_expression(self) -> Optional[Expression]:
        """"""

        left_expr = self.try_parse_and_expression()

        while operator := self.check_and_consume(TokenType.AND):

            if not (expr := self.try_parse_and_expression()):
                raise InvalidRightExpressionError(self.lexer.token)

            left_expr = OrExpression(
                left_expr, operator, expr
            )

        return left_expr

    def try_parse_and_expression(self) -> Optional[Expression]:
        """"""

        left_expr = self.try_parse_equality_expression()

        while operator := self.check_one_of_many_and_consume([
            TokenType.EQ, TokenType.NEQ
        ]):

            if not (expr := self.try_parse_equality_expression()):
                raise InvalidRightExpressionError(self.lexer.token)

            left_expr = AndExpression(
                left_expr, operator, expr
            )

        return left_expr

    def try_parse_equality_expression(self) -> Optional[Expression]:
        """"""

        left_expr = self.try_parse_comp_factor()

        while operator := self.check_one_of_many_and_consume([
            TokenType.GT, TokenType.GTE,
            TokenType.LT, TokenType.LTE,
        ]):

            if not (expr := self.try_parse_comp_factor()):
                raise InvalidRightExpressionError(self.lexer.token)

            left_expr = EqualityExpression(
                left_expr, operator, expr
            )

        return left_expr

    def try_parse_comp_factor(self) -> Optional[Expression]:
        """"""

        seen_not_token = self.check_and_consume(TokenType.NOT)

        if not (add_factor := self.try_parse_add_factor()):
            return None

        return CompFactor(add_factor, bool(seen_not_token))

    def try_parse_add_factor(self) -> Optional[Expression]:
        """"""

        left_expr = self.try_parse_mult_factor()

        while operator := self.check_one_of_many_and_consume([TokenType.PLUS, TokenType.MINUS]):

            if not (expr := self.try_parse_mult_factor()):
                raise InvalidRightExpressionError(self.lexer.token)

            left_expr = AdditiveExpression(
                left_expr, operator, expr
            )

        return left_expr

    def try_parse_mult_factor(self) -> Optional[Expression]:
        """"""

        left_expr = self.try_parse_factor()

        while operator := self.check_one_of_many_and_consume([TokenType.MUL, TokenType.DIV, TokenType.MODULO]):

            if not (expr := self.try_parse_factor()):
                raise InvalidRightExpressionError(self.lexer.token)

            left_expr = MultiplicativeExpression(
                left_expr, operator, expr
            )

        return left_expr

    def try_parse_factor(self) -> Optional[Factor]:
        """Tries to parse Factor which can be either:
        Literal, Identifier/FunctionCall, nested Expression in parentheses."""

        if literal := self.try_parse_literal():
            return literal

        if id_or_func_call := self.try_parse_identifier_or_func_call():
            return id_or_func_call

        if expr_in_parenthesis := self.try_parse_parenthesised_expression():
            return expr_in_parenthesis

        return None

    def try_parse_literal(self) -> Optional[Factor]:
        """"""

        seen_minus = self.check_and_consume(TokenType.MINUS)
        if not (prev_token := self.check_one_of_many_and_consume(LITERALS)):
            return None

        typ = TYPES_MAPPING[prev_token.type]()

        return Factor(
            Literal(typ),
            bool(seen_minus)
        )

    def try_parse_identifier_or_func_call(self) -> Optional[Factor]:
        """"""

        if not (token := self.check_and_consume(TokenType.ID)):
            return None

        if func_call := self.try_parse_func_call(func_name=token.value):
            return Factor(func_call, False)

        if lambda_expr := self.try_parse_rest_of_lambda_definition(token.value):
            return Factor(lambda_expr, False)

        return Factor(Identifier(token.value), False)

    def try_parse_rest_of_lambda_definition(self, first_argument_name: str):
        """"""

        if not self.check_and_consume(TokenType.TYPE_ASSIGN):
            return None

        typ = self.try_parse_var_type()
        parameter = Parameter(first_argument_name, typ, nullable=False, mutable=None)

        params = [parameter]
        while self.check_and_consume(TokenType.COMMA):

            if not (param := self.try_parse_parameter()):
                raise MissingParameterError(self.lexer.token)

            params.append(param)

        self.expect_and_consume(TokenType.RPAREN)
        self.expect_and_consume(TokenType.TYPE_ASSIGN)

        return_type = self.try_parse_return_type()

        self.expect_and_consume(TokenType.ARROW)

        func_body = self.try_parse_func_body()

        return LambdaExpression(
            return_type=return_type,
            arguments=params,
            body=func_body
        )

    def try_parse_parenthesised_expression(self) -> Optional[Factor]:
        """Tries to parse nested expression - in parentheses.
        It also handles empty lambda definition and call without arguments,
        because of its syntax similarity to expression in parentheses.
        """

        if not self.check_and_consume(TokenType.LPAREN):
            return None

        # lambda expression without arguments
        if self.check_and_consume(TokenType.RPAREN):

            # lambda expression with implicit return type - LambdaDefinition without arguments
            if self.check_and_consume(TokenType.TYPE_ASSIGN):
                return_type = self.try_parse_return_type()
                self.expect_and_consume(TokenType.ARROW)
                func_body = self.try_parse_func_body()
                return Factor(
                    LambdaExpression(
                        return_type=return_type,
                        arguments=[],
                        body=func_body
                    ),
                    False
                )

        expression = self.try_parse_expression()

        match expression:
            # lambda expression is handled as nested expression but does not have `)` at the end
            case CompFactor(factor=Factor(value=LambdaExpression())):
                pass

            case _:
                self.expect_and_consume(TokenType.RPAREN)

        return Factor(expression, False)

    def check_and_consume(self, token_type: TokenType) -> Optional[Token]:
        """If type is valid, asks lexer for a next token and returns current token,
         otherwise returns None."""

        current_token = self.lexer.token
        if self.lexer.token.type != token_type:
            return None

        self.lexer.build_next_token()
        return current_token

    def check_one_of_many_and_consume(self, token_types: Sequence[TokenType]) -> Optional[Token]:
        """If types are valid, asks lexer for a next token and returns current token,
         otherwise returns None."""

        current_token = self.lexer.token
        if current_token.type not in token_types:
            return None

        self.lexer.build_next_token()
        return current_token

    def expect_and_consume(self, token_type: TokenType) -> Token:
        """If type is valid, asks lexer for a next token and returns current token,
        otherwise throws UnexpectedTokenError"""

        current_token = self.lexer.token
        if current_token.type != token_type:
            raise UnexpectedTokenError(
                current_token=current_token,
                expected_token_type=token_type
            )

        self.lexer.build_next_token()
        return current_token

    def expect_one_of_many_and_consume(self, token_types: Sequence[TokenType]) -> Token:
        """If types are valid, asks lexer for a next token and returns current token,
        otherwise throws UnexpectedTokenError"""

        current_token = self.lexer.token
        if current_token.type not in token_types:
            raise UnexpectedTokenError(
                current_token=current_token,
                expected_token_type=token_types
            )

        self.lexer.build_next_token()
        return current_token
