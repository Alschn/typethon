import unittest

from parameterized import parameterized

from src.errors.parser import (
    UninitializedConstError, NotNullableError, UnexpectedTokenError, InvalidReturnTypeError,
    MissingParameterError, WhileLoopMissingCondition, MissingTypeAssignment, InvalidConditionalExpression,
)
from src.parser.objects.objects import (
    DeclarationStatement, Variable, CompFactor, Factor, Literal, FunctionCall,
    AdditiveExpression, MultiplicativeExpression, Identifier, AssignmentStatement,
    NullCoalesceExpression, EqualityExpression, WhileLoopStatement, EmptyStatement,
    ReturnStatement, CompoundStatement, LambdaExpression,
    InlineReturnStatement, Parameter, BinaryExpression, IfStatement, ElseStatement, FunctionDefinition, ElifStatement
)
from src.parser.objects.program import Program
from src.parser.types import (
    String, Integer, Float, ArithmeticOperator,
    LogicOperator, ComparisonOperator, Null, Bool,
    Func, Void, OtherOperator)
from src.tests.utils import setup_parser


def parse(text: str) -> Program:
    """Sets up parser and runs its main method"""
    return setup_parser(text).parse_program()


class DeclarationTests(unittest.TestCase):

    def test_uninitialized_const_declaration(self):
        text = "const a: int;"
        with self.assertRaises(UninitializedConstError):
            parse(text)

    def test_declaration_missing_nullable_type_assign(self):
        text = "let a: int;"
        with self.assertRaises(NotNullableError):
            parse(text)

    def test_nullable_declaration_without_initializing(self):
        text = "let a?: int;"
        program = parse(text)
        match program.objects:
            case [
                DeclarationStatement(
                    left_value=Variable(name='a', nullable=True, mutable=True),
                    right_value=None
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_nullable_declaration_with_initialization(self):
        text = "let a?: str = 'Hello world!';"
        program = parse(text)
        match program.objects:
            case [
                DeclarationStatement(
                    left_value=Variable(name='a', mutable=True, nullable=True, type=String()),
                    right_value=CompFactor(
                        factor=Factor(
                            value=Literal(
                                value="Hello world!",
                                type=String()
                            ),
                            minus=False,
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_declaration_with_expression(self):
        text = "const a: int = f();"
        program = parse(text)
        match program.objects:
            case [
                DeclarationStatement(
                    left_value=Variable(name='a', type=Integer(), nullable=False, mutable=False),
                    right_value=CompFactor(
                        factor=Factor(
                            value=FunctionCall(name='f', arguments=[[]]),
                            minus=False
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_declaration_with_complex_expression(self):
        text = "const a: float = -1 * (a * 3) / 9 + f();"
        program = parse(text)
        match program.objects:
            case [
                DeclarationStatement(
                    left_value=Variable(name='a', type=Float(), nullable=False, mutable=False),
                    right_value=CompFactor(
                        factor=AdditiveExpression(
                            left_value=MultiplicativeExpression(
                                left_value=MultiplicativeExpression(
                                    left_value=Factor(
                                        value=Literal(value=1, type=Integer()),
                                        minus=True
                                    ),
                                    operator=ArithmeticOperator.MUL,
                                    right_value=Factor(
                                        value=CompFactor(
                                            factor=MultiplicativeExpression(
                                                left_value=Factor(
                                                    value=Identifier(name='a'),
                                                    minus=False
                                                ),
                                                operator=ArithmeticOperator.MUL,
                                                right_value=Factor(
                                                    value=Literal(value=3, type=Integer()),
                                                    minus=False
                                                )
                                            ),
                                            negation=False
                                        ),
                                        minus=False
                                    )
                                ),
                                operator=ArithmeticOperator.DIV,
                                right_value=Factor(
                                    value=Literal(value=9, type=Integer()),
                                    minus=False
                                )
                            ),
                            operator=ArithmeticOperator.PLUS,
                            right_value=Factor(
                                value=FunctionCall(name='f', arguments=[[]]),
                                minus=False
                            )
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')


class AssignmentTests(unittest.TestCase):

    def test_assignment(self):
        text = "a = 1;"
        program = parse(text)
        match program.objects:
            case [
                AssignmentStatement(
                    symbol='a',
                    right_value=CompFactor(
                        factor=Factor(
                            value=Literal(value=1, type=Integer()),
                            minus=False
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_assignment_simple_expression(self):
        text = "a = b + c;"
        program = parse(text)
        match program.objects:
            case [
                AssignmentStatement(
                    symbol='a',
                    right_value=CompFactor(
                        factor=AdditiveExpression(
                            left_value=Factor(
                                value=Identifier(name='b'),
                                minus=False
                            ),
                            operator=ArithmeticOperator.PLUS,
                            right_value=Factor(
                                value=Identifier(name='c'),
                                minus=False
                            )
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_assignment_mixed_expressions(self):
        text = "a = (b - -c) * d / e or 2;"
        program = parse(text)
        match program.objects:
            case [
                AssignmentStatement(
                    symbol='a',
                    right_value=NullCoalesceExpression(
                        left_value=CompFactor(
                            factor=MultiplicativeExpression(
                                left_value=MultiplicativeExpression(
                                    left_value=Factor(
                                        value=CompFactor(
                                            factor=AdditiveExpression(
                                                left_value=Factor(
                                                    value=Identifier(name='b'),
                                                    minus=False
                                                ),
                                                operator=ArithmeticOperator.MINUS,
                                                right_value=Factor(
                                                    value=Identifier(name='c'),
                                                    minus=True
                                                ),
                                            ),
                                            negation=False
                                        ),
                                        minus=False
                                    ),
                                    operator=ArithmeticOperator.MUL,
                                    right_value=Factor(
                                        value=Identifier(name='d'),
                                        minus=False
                                    )
                                ),
                                operator=ArithmeticOperator.DIV,
                                right_value=Factor(
                                    value=Identifier(name='e'),
                                    minus=False
                                )
                            ),
                            negation=False
                        ),
                        operator=LogicOperator.OR,
                        right_value=CompFactor(
                            factor=Factor(
                                value=Literal(value=2, type=Integer()),
                                minus=False
                            ),
                            negation=False
                        )
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_assignment_nested_expressions(self):
        text = "a = (b + c) * (12 % c());"
        program = parse(text)
        match program.objects:
            case [
                AssignmentStatement(
                    symbol='a',
                    right_value=CompFactor(
                        factor=MultiplicativeExpression(
                            left_value=Factor(
                                value=CompFactor(
                                    factor=AdditiveExpression(
                                        left_value=Factor(
                                            value=Identifier(name='b'),
                                            minus=False
                                        ),
                                        operator=ArithmeticOperator.PLUS,
                                        right_value=Factor(
                                            value=Identifier(name='c'),
                                            minus=False
                                        )
                                    )
                                ),
                                minus=False
                            ),
                            operator=ArithmeticOperator.MUL,
                            right_value=Factor(
                                value=CompFactor(
                                    factor=MultiplicativeExpression(
                                        left_value=Factor(
                                            value=Literal(value=12, type=Integer()),
                                            minus=False
                                        ),
                                        operator=ArithmeticOperator.MODULO,
                                        right_value=Factor(
                                            value=FunctionCall(name='c', arguments=[[]]),
                                            minus=False
                                        ),
                                    ),
                                    negation=False
                                ),
                                minus=False
                            ),
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_assignment_nested(self):
        # multiple assignments are not allowed
        text = "a = b = c"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)


class FuncCallTests(unittest.TestCase):

    def test_func_call_without_args(self):
        text = "f();"
        program = parse(text)
        match program.objects:
            case [
                FunctionCall(name='f', arguments=[[]])
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_call_with_args(self):
        text = "f(var1, var2);"
        program = parse(text)
        match program.objects:
            case [
                FunctionCall(name='f', arguments=[
                    [
                        CompFactor(
                            factor=Factor(
                                value=Identifier(name='var1'),
                                minus=False
                            ),
                            negation=False
                        ),
                        CompFactor(
                            factor=Factor(
                                value=Identifier(name='var2'),
                                minus=False
                            ),
                            negation=False
                        ),
                    ]
                ])
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_call_with_mixed_args(self):
        text = "f(not var1 * -3, 15 >= 100 < 10, null);"
        program = parse(text)
        match program.objects:
            case [
                FunctionCall(
                    name='f',
                    arguments=[
                        [
                            CompFactor(
                                factor=MultiplicativeExpression(
                                    left_value=Factor(
                                        value=Identifier(name='var1'),
                                        minus=False
                                    ),
                                    operator=ArithmeticOperator.MUL,
                                    right_value=Factor(
                                        value=Literal(value=3, type=Integer()),
                                        minus=True
                                    )
                                ),
                                negation=True
                            ),
                            EqualityExpression(
                                left_value=EqualityExpression(
                                    left_value=CompFactor(
                                        factor=Factor(
                                            value=Literal(value=15, type=Integer()),
                                            minus=False
                                        ),
                                        negation=False,
                                    ),
                                    operator=ComparisonOperator.GTE,
                                    right_value=CompFactor(
                                        factor=Factor(
                                            value=Literal(value=100, type=Integer()),
                                            minus=False
                                        ),
                                        negation=False
                                    ),
                                ),
                                operator=ComparisonOperator.LT,
                                right_value=CompFactor(
                                    factor=Factor(
                                        value=Literal(value=10, type=Integer()),
                                        minus=False
                                    ),
                                    negation=False
                                ),
                            ),
                            CompFactor(
                                factor=Factor(
                                    value=Literal(value=None, type=Null()),
                                    minus=False
                                ),
                                negation=False
                            )
                        ]])
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_call_with_nested_func_calls(self):
        text = "f(f(f()));"
        program = parse(text)
        match program.objects:
            case [
                FunctionCall(name='f', arguments=[
                    [
                        CompFactor(
                            factor=Factor(
                                value=FunctionCall(name='f', arguments=[
                                    [
                                        CompFactor(
                                            factor=Factor(
                                                value=FunctionCall(name='f', arguments=[
                                                    []
                                                ]),
                                                minus=False
                                            ),
                                            negation=False
                                        )
                                    ]
                                ]),
                                minus=False
                            ),
                            negation=False
                        )
                    ]
                ])
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_call_chained_calls(self):
        text = "f()();"
        program = parse(text)
        match program.objects:
            case [
                FunctionCall(name='f', arguments=[[], []])
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_call_chained_calls_with_args(self):
        text = "f(a + b, d())(15)(f);"
        program = parse(text)
        match program.objects:
            case [
                FunctionCall(name='f', arguments=[
                    [
                        CompFactor(
                            factor=AdditiveExpression(
                                left_value=Factor(
                                    value=Identifier(name='a'),
                                    minus=False
                                ),
                                operator=ArithmeticOperator.PLUS,
                                right_value=Factor(
                                    value=Identifier(name='b'),
                                    minus=False
                                ),

                            ),
                            negation=False
                        ),
                        CompFactor(
                            factor=Factor(
                                value=FunctionCall(name='d', arguments=[[]]),
                                minus=False
                            ),
                            negation=False
                        ),

                    ],
                    [
                        CompFactor(
                            factor=Factor(
                                value=Literal(value=15, type=Integer()),
                                minus=False,
                            ),
                            negation=False
                        ),
                    ],
                    [
                        CompFactor(
                            factor=Factor(
                                value=Identifier(name='f'),
                                minus=False
                            ),
                            negation=False
                        ),
                    ]
                ])
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_call_missing_parenthesis(self):
        text = "f("
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    def test_func_call_missing_second_argument(self):
        text = "f(, a)"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)


class WhileLoopTests(unittest.TestCase):

    def test_while_loop_statement(self):
        text = """while(true) { count = count + 1; }"""
        program = parse(text)
        match program.objects:
            case [
                WhileLoopStatement(
                    body=CompoundStatement(
                        statements=[
                            AssignmentStatement(
                                symbol='count',
                                right_value=CompFactor(
                                    factor=AdditiveExpression(
                                        left_value=Factor(
                                            value=Identifier(name='count'),
                                            minus=False
                                        ),
                                        operator=ArithmeticOperator.PLUS,
                                        right_value=Factor(
                                            value=Literal(value=1, type=Integer()),
                                            minus=False
                                        )
                                    ),
                                    negation=False
                                )
                            )
                        ]
                    ),
                    condition=CompFactor(

                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_while_loop_without_body(self):
        text = "while(true) {}"
        program = parse(text)
        match program.objects:
            case [
                WhileLoopStatement(
                    body=EmptyStatement(),
                    condition=CompFactor(
                        factor=Factor(
                            value=Literal(value=True, type=Bool()),
                            minus=False
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_while_loop_no_statement_in_body(self):
        text = "while (True) { 1 > 1 }"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    def test_while_loop_nested(self):
        text = """
        while(a > b) {
            while(true) {
                while(false) {}
            }
        }
        """
        program = parse(text)
        match program.objects:
            case [
                WhileLoopStatement(
                    body=CompoundStatement(
                        statements=[
                            WhileLoopStatement(
                                body=CompoundStatement(
                                    statements=[
                                        WhileLoopStatement(
                                            body=EmptyStatement(),
                                            condition=CompFactor(
                                                factor=Factor(
                                                    value=Literal(value=False, type=Bool()),
                                                    minus=False
                                                ),
                                                negation=False
                                            )
                                        )
                                    ]
                                ),
                                condition=CompFactor(
                                    factor=Factor(
                                        value=Literal(value=True, type=Bool()),
                                        minus=False
                                    ),
                                    negation=False
                                )
                            )
                        ]
                    ),
                    condition=EqualityExpression(
                        left_value=CompFactor(

                        ),
                        operator=ComparisonOperator.GT,
                        right_value=CompFactor(

                        )
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_while_loop_complex_condition(self):
        text = """
        while ((a() * 15) or true ?? f()()) {}
        """
        program = parse(text)
        match program.objects:
            case [
                WhileLoopStatement(
                    body=EmptyStatement(),
                    condition=BinaryExpression(
                        left_value=NullCoalesceExpression(
                            left_value=CompFactor(
                                factor=Factor(
                                    value=CompFactor(
                                        factor=MultiplicativeExpression(
                                            left_value=Factor(
                                                value=FunctionCall(name='a', arguments=[[]]),
                                                minus=False
                                            ),
                                            operator=ArithmeticOperator.MUL,
                                            right_value=Factor(
                                                value=Literal(value=15, type=Integer()),
                                                minus=False
                                            )
                                        ),
                                        negation=False
                                    ),
                                    minus=False
                                ),
                                negation=False
                            ),
                            operator=LogicOperator.OR,
                            right_value=CompFactor(
                                factor=Factor(
                                    value=Literal(value=True, type=Bool()),
                                    minus=False
                                ),
                                negation=False
                            )
                        ),
                        operator=OtherOperator.NULL_COALESCE,
                        right_value=CompFactor(
                            factor=Factor(
                                value=FunctionCall(name='f', arguments=[[], []]),
                                minus=False
                            ),
                            negation=False
                        )
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_while_loop_multiple_statements(self):
        text = """
        while (True) {
            const a: int = 5;
            let a?: bool;
        }
        """
        program = parse(text)
        match program.objects:
            case [
                WhileLoopStatement(
                    body=CompoundStatement(
                        statements=[
                            DeclarationStatement(
                                left_value=Variable(name='a', nullable=False, mutable=False, type=Integer()),
                                right_value=CompFactor(
                                    factor=Factor(
                                        value=Literal(value=5, type=Integer()),
                                        minus=False
                                    ),
                                    negation=False
                                )
                            ),
                            DeclarationStatement(
                                left_value=Variable(name='a', nullable=True, mutable=True, type=Bool()),
                                right_value=None
                            )
                        ]
                    ),
                    condition=CompFactor(

                    ),
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_while_loop_nested_mixed_statements(self):
        text = """while (i < 1000) {
            if (a) { 
                i = i + 1; 
            }
            
            else {
                while (False) {
                    const a: int = 5;
                    i = a * -(-5);
                }
            }
        }
        """
        program = parse(text)
        match program.objects:
            case [
                WhileLoopStatement(
                    body=CompoundStatement(
                        statements=[
                            IfStatement(
                                condition=CompFactor(
                                    factor=Factor(
                                        value=Identifier(name='a'),
                                        minus=False
                                    ),
                                    negation=False
                                ),
                                elif_statements=[],
                                else_statement=ElseStatement(
                                    statement=CompoundStatement(
                                        statements=[
                                            WhileLoopStatement(
                                                body=CompoundStatement(
                                                    statements=[
                                                        DeclarationStatement(
                                                            left_value=Variable(name='a', type=Integer(), mutable=False,
                                                                                nullable=False),
                                                            right_value=CompFactor(
                                                                factor=Factor(
                                                                    value=Literal(value=5, type=Integer()),
                                                                    minus=False
                                                                ),
                                                                negation=False
                                                            )
                                                        ),
                                                        AssignmentStatement(
                                                            symbol='i',
                                                            right_value=CompFactor(
                                                                factor=MultiplicativeExpression(
                                                                    left_value=Factor(
                                                                        value=Identifier(name='a'),
                                                                        minus=False
                                                                    ),
                                                                    operator=ArithmeticOperator.MUL,
                                                                    right_value=Factor(
                                                                        value=CompFactor(
                                                                            factor=Factor(
                                                                                value=Literal(value=5, type=Integer()),
                                                                                minus=True
                                                                            ),
                                                                            negation=False
                                                                        ),
                                                                        minus=True
                                                                    ),
                                                                )
                                                            )
                                                        )
                                                    ]
                                                ),
                                                condition=CompFactor(
                                                    factor=Factor(
                                                        value=Identifier(name='False'),
                                                        minus=False
                                                    ),
                                                    negation=False
                                                )
                                            )
                                        ]
                                    )
                                )
                            )
                        ]
                    ),
                    condition=EqualityExpression(
                        left_value=CompFactor(
                            factor=Factor(
                                value=Identifier(name='i'),
                                minus=False
                            ),
                            negation=False
                        ),
                        operator=ComparisonOperator.LT,
                        right_value=CompFactor(
                            factor=Factor(
                                value=Literal(value=1000, type=Integer()),
                                minus=False
                            ),
                            negation=False
                        )
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_while_loop_missing_parentheses(self):
        text = "while true"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    def test_while_loop_condition_parentheses_not_closed(self):
        text = "while (true"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    def test_while_loop_missing_condition(self):
        text = "while () {}"
        with self.assertRaises(WhileLoopMissingCondition):
            parse(text)


class IfStatementTests(unittest.TestCase):

    def test_if_statement(self):
        text = "if (true) { const a: int = 10; }"
        program = parse(text)
        match program.objects:
            case [
                IfStatement(
                    condition=CompFactor(
                        factor=Factor(
                            value=Literal(value=True, type=Bool()),
                            minus=False
                        ),
                        negation=False
                    ),
                    elif_statements=[],
                    else_statement=None,
                    statement=CompoundStatement(
                        statements=[
                            DeclarationStatement(
                                left_value=Variable(name='a', mutable=False, nullable=False, type=Integer()),
                                right_value=CompFactor(
                                    factor=Factor(
                                        value=Literal(value=10, type=Integer()),
                                        minus=False
                                    ),
                                    negation=False
                                )
                            )
                        ]
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_if_statement_without_body(self):
        text = "if (1 < 0) {}"
        program = parse(text)
        match program.objects:
            case [
                IfStatement(
                    condition=EqualityExpression(
                        left_value=CompFactor(
                            factor=Factor(
                                value=Literal(value=1, type=Integer()),
                                minus=False
                            ),
                            negation=False
                        ),
                        operator=ComparisonOperator.LT,
                        right_value=CompFactor(
                            factor=Factor(
                                value=Literal(value=0, type=Integer()),
                                minus=False
                            ),
                            negation=False
                        )
                    ),
                    elif_statements=[],
                    else_statement=None,
                    statement=EmptyStatement()
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_if_statement_without_condition(self):
        text = "if ()"
        with self.assertRaises(InvalidConditionalExpression):
            parse(text)

    def test_if_statement_missing_condition_in_elif(self):
        text = "if (a) {} elif () {}"
        with self.assertRaises(InvalidConditionalExpression):
            parse(text)

    def test_if_statement_condition_not_in_parentheses(self):
        text = "if True"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    def test_if_statement_no_statement(self):
        text = "if (True) 1 + 1;"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    def test_if_statement_with_elif(self):
        text = """
        if (true) {}
        elif (false) {}
        """
        program = parse(text)
        match program.objects:
            case [
                IfStatement(
                    condition=CompFactor(
                        factor=Factor(
                            value=Literal(value=True, type=Bool()),
                            minus=False
                        ),
                        negation=False
                    ),
                    elif_statements=[
                        ElifStatement(
                            statement=EmptyStatement()
                        )
                    ],
                    else_statement=None,
                    statement=EmptyStatement()
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_if_statement_with_multiple_elif(self):
        text = """
        if (true) {}
        elif (true) {}
        elif (false) {}
        """
        program = parse(text)
        match program.objects:
            case [
                IfStatement(
                    condition=CompFactor(
                        factor=Factor(
                            value=Literal(value=True, type=Bool()),
                            minus=False
                        ),
                        negation=False
                    ),
                    elif_statements=[
                        ElifStatement(
                            condition=CompFactor(
                                factor=Factor(
                                    value=Literal(value=True, type=Bool()),
                                    minus=False
                                ),
                                negation=False
                            ),
                            statement=EmptyStatement()
                        ),
                        ElifStatement(
                            condition=CompFactor(
                                factor=Factor(
                                    value=Literal(value=False, type=Bool()),
                                    minus=False
                                ),
                                negation=False
                            ),
                            statement=EmptyStatement()
                        )
                    ],
                    else_statement=None,
                    statement=EmptyStatement()
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_if_statement_with_else(self):
        text = """
        if (a + b) { print("if"); }
        else { print("else"); }
        """
        program = parse(text)
        match program.objects:
            case [
                IfStatement(

                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_if_statement_with_elif_else(self):
        text = """
        if (true) {}
        elif (false) {}
        else {}
        """
        program = parse(text)
        match program.objects:
            case [
                IfStatement(
                    condition=CompFactor(
                        factor=Factor(
                            value=Literal(value=True, type=Bool()),
                            minus=False
                        ),
                        negation=False
                    ),
                    elif_statements=[
                        ElifStatement(
                            condition=CompFactor(
                                factor=Factor(
                                    value=Literal(value=False, type=Bool()),
                                    minus=False
                                ),
                                negation=False
                            ),
                            statement=EmptyStatement()
                        )
                    ],
                    else_statement=ElseStatement(
                        statement=EmptyStatement()
                    ),
                    statement=EmptyStatement()
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_if_statement_complex_condition(self):
        text = "if (not a * c - -15 / (d())) {}"
        program = parse(text)
        match program.objects:
            case [
                IfStatement(
                    condition=CompFactor(
                        factor=AdditiveExpression(
                            left_value=MultiplicativeExpression(
                                left_value=Factor(
                                    value=Identifier(name='a'),
                                    minus=False
                                ),
                                operator=ArithmeticOperator.MUL,
                                right_value=Factor(
                                    value=Identifier(name='c'),
                                    minus=False
                                )
                            ),
                            operator=ArithmeticOperator.MINUS,
                            right_value=MultiplicativeExpression(
                                left_value=Factor(
                                    value=Literal(value=15, type=Integer()),
                                    minus=True
                                ),
                                operator=ArithmeticOperator.DIV,
                                right_value=Factor(
                                    value=CompFactor(
                                        factor=Factor(
                                            value=FunctionCall(name='d', arguments=[[]]),
                                            minus=False
                                        ),
                                        negation=False
                                    ),
                                    minus=False
                                ),
                            )
                        ),
                        negation=True
                    ),
                    elif_statements=[],
                    else_statement=None,
                    statement=EmptyStatement()
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_if_statement_function_call_condition(self):
        text = """
        if (f()) {}
        """
        program = parse(text)
        match program.objects:
            case [
                IfStatement(
                    condition=CompFactor(
                        factor=Factor(
                            value=FunctionCall(name='f', arguments=[[]]),
                            minus=False
                        ),
                        negation=False
                    ),
                    elif_statements=[],
                    else_statement=None,
                    statement=EmptyStatement()
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_if_statement_nested(self):
        text = """
        
        """
        program = parse(text)
        match program.objects:
            case [

            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_if_statement_complex_body(self):
        text = """
        
        """
        program = parse(text)


class FuncDefTests(unittest.TestCase):

    def test_func_def(self):
        text = """
        def function(arg1: int, arg2: bool): int => {
            if (arg2) {
                return arg1 * 3;            
            }
            return arg1;
        }
        """
        program = parse(text)
        match program.objects:
            case [
                FunctionDefinition(
                    name='function',
                    return_type=Integer(),
                    arguments=[
                        Parameter(symbol='arg1', type=Integer(), nullable=False, mutable=False),
                        Parameter(symbol='arg2', type=Bool(), nullable=False, mutable=False)
                    ],
                    body=CompoundStatement(
                        statements=[
                            IfStatement(
                                condition=CompFactor(
                                    factor=Factor(
                                        value=Identifier(name='arg2'),
                                        minus=False
                                    ),
                                    negation=False
                                ),
                                elif_statements=[],
                                else_statement=None,
                                statement=CompoundStatement(
                                    statements=[
                                        ReturnStatement(
                                            expression=CompFactor(
                                                factor=MultiplicativeExpression(
                                                    left_value=Factor(
                                                        value=Identifier(name='arg1'),
                                                        minus=False
                                                    ),
                                                    operator=ArithmeticOperator.MUL,
                                                    right_value=Factor(
                                                        value=Literal(value=3, type=Integer()),
                                                        minus=False
                                                    )
                                                ),
                                                negation=False
                                            )
                                        )
                                    ]
                                )
                            ),
                            ReturnStatement(
                                expression=CompFactor(
                                    factor=Factor(
                                        value=Identifier(name='arg1')
                                    ),
                                    negation=False
                                )
                            )
                        ]
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_def_no_parameters(self):
        text = """
        def function(): int => {
            return 1 + 2;
        }
        """
        program = parse(text)
        match program.objects:
            case [
                FunctionDefinition(
                    name='function',
                    return_type=Integer(),
                    arguments=[],
                    body=CompoundStatement(
                        statements=[
                            ReturnStatement(
                                expression=CompFactor(
                                    factor=AdditiveExpression(
                                        left_value=Factor(
                                            value=Literal(value=1, type=Integer()),
                                            minus=False
                                        ),
                                        operator=ArithmeticOperator.PLUS,
                                        right_value=Factor(
                                            value=Literal(value=2, type=Integer()),
                                            minus=False
                                        )
                                    ),
                                    negation=False
                                )
                            )
                        ]
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_def_return_type_missing(self):
        text = "def function() => {}"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    def test_func_def_invalid_return_type(self):
        text = "def function(): double => {}"
        with self.assertRaises(InvalidReturnTypeError):
            parse(text)

    def test_func_def_one_parameter(self):
        text = "def function(arg1: bool): void => {}"
        program = parse(text)
        match program.objects:
            case [
                FunctionDefinition(
                    name='function',
                    arguments=[
                        Parameter(symbol='arg1', type=Bool(), mutable=False, nullable=False)
                    ],
                    return_type=Void(),
                    body=EmptyStatement()
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_def_multiple_parameters(self):
        text = "def function(arg1: bool, arg2: str): void => {}"
        program = parse(text)
        match program.objects:
            case [
                FunctionDefinition(
                    name='function',
                    arguments=[
                        Parameter(symbol='arg1', type=Bool(), mutable=False, nullable=False),
                        Parameter(symbol='arg2', type=String(), mutable=False, nullable=False)
                    ],
                    return_type=Void(),
                    body=EmptyStatement()
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_def_no_return(self):
        text = "def function(): void => {}"
        program = parse(text)
        match program.objects:
            case [
                FunctionDefinition(
                    name='function',
                    arguments=[],
                    return_type=Void(),
                    body=EmptyStatement()
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_def_bare_return(self):
        text = "def function(): void => { return; }"
        program = parse(text)
        match program.objects:
            case [
                FunctionDefinition(
                    name='function',
                    arguments=[],
                    return_type=Void(),
                    body=CompoundStatement(
                        statements=[
                            ReturnStatement(
                                expression=None
                            )
                        ]
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_func_def_function_name_keyword(self):
        text = "def func(): void => {}"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    def test_func_def_missing_parameter_type_declaration(self):
        text = "def f(a)"
        with self.assertRaises(MissingTypeAssignment):
            parse(text)

    @parameterized.expand([
        ('def f(a: int, )',),
        ('def f(a: int, b:str, )',),
    ])
    def test_func_def_parameters_trailing_comma(self, text: str):
        with self.assertRaises(MissingParameterError):
            parse(text)

    def test_func_def_return_lambda_function(self):
        text = """
        def f(): func((a: int) => int) => {
            return (a: int): func((a: int) => int) => a;
        }
        """
        program = parse(text)
        match program.objects:
            case [
                FunctionDefinition(
                    name='f',
                    return_type=Func(
                        input_types=[Parameter(symbol='a', type=Integer(), nullable=False, mutable=False)],
                        output_type=Integer()
                    ),
                    arguments=[],
                    body=CompoundStatement(
                        statements=[
                            ReturnStatement(
                                expression=CompFactor(
                                    factor=Factor(
                                        value=CompFactor(
                                            factor=Factor(
                                                value=LambdaExpression(
                                                    return_type=Func(
                                                        input_types=[
                                                            Parameter(
                                                                symbol='a', type=Integer(), nullable=False,
                                                                mutable=False
                                                            )
                                                        ],
                                                        output_type=Integer()
                                                    ),
                                                    arguments=[
                                                        Parameter(
                                                            symbol='a', type=Integer(), nullable=False, mutable=False
                                                        )
                                                    ],
                                                    body=InlineReturnStatement(
                                                        expression=CompFactor(
                                                            factor=Factor(
                                                                value=Identifier(name='a'),
                                                                minus=False
                                                            ),
                                                            negation=False
                                                        )
                                                    )
                                                ),
                                                minus=False
                                            ),
                                            negation=False
                                        ),
                                        minus=False
                                    ),
                                    negation=False
                                )
                            )
                        ]
                    )
                )
            ]:
                pass

            case _:
                self.fail()

    def test_func_def_return_nested_lambda_functions(self):
        text = """
        def f(a: int, b: int): func((a: int) => func((b: int) => int)) => {
            return (a: int): func((b: int) => int) => {
                return (b: int): int => a + b;
            };
        }
        """
        program = parse(text)
        self.assertIsNotNone(program)  # TODO asserts


class LambdaTests(unittest.TestCase):

    def test_lambda_function_declaration(self):
        text = """
        const a: func(() => void) = (b: int): str => { return ""; };
        """
        program = parse(text)
        match program.objects:
            case [
                DeclarationStatement(
                    left_value=Variable(name='a', type=Func(), nullable=False, mutable=False),
                    right_value=CompFactor(
                        factor=Factor(
                            value=CompFactor(
                                factor=Factor(
                                    value=LambdaExpression(
                                        arguments=[
                                            Parameter(symbol='b', type=Integer(), nullable=False, mutable=False)
                                        ],
                                        body=CompoundStatement(
                                            statements=[
                                                ReturnStatement(
                                                    expression=CompFactor(
                                                        factor=Factor(
                                                            value=Literal(value="", type=String()),
                                                            minus=False
                                                        ),
                                                        negation=False
                                                    )
                                                )
                                            ]
                                        ),
                                        return_type=String()
                                    ),
                                    minus=False
                                ),
                                negation=False
                            ),
                            minus=False
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_lambda_function_assignment(self):
        text = "a = (b: int): str => { return ''; };"
        program = parse(text)
        match program.objects:
            case [
                AssignmentStatement(
                    symbol='a',
                    right_value=CompFactor(
                        factor=Factor(
                            value=CompFactor(
                                factor=Factor(
                                    value=LambdaExpression(
                                        body=CompoundStatement(
                                            statements=[
                                                ReturnStatement(
                                                    expression=CompFactor(
                                                        factor=Factor(
                                                            value=Literal(value="", type=String()),
                                                            minus=False
                                                        ),
                                                        negation=False
                                                    )
                                                )
                                            ]
                                        ),
                                        arguments=[Parameter(
                                            symbol='b',
                                            type=Integer(),
                                            mutable=False,
                                            nullable=False
                                        )]
                                    ),
                                    minus=False
                                ),
                                negation=False
                            ),
                            minus=False
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_lambda_trailing_comma_in_args(self):
        text = "a = (a: int,) => {}"
        with self.assertRaises(MissingParameterError):
            parse(text)

    def test_lambda_return_type_missing(self):
        text = "a = () => {}"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    def test_lambda_invalid_return_type(self):
        text = "a = (): double"
        with self.assertRaises(InvalidReturnTypeError):
            parse(text)

    def test_lambda_return_type_func(self):
        text = """
        const a: func(() => func(() => void)) = (): func(() => void) => { 
            return (): void => {}; 
        };
        """
        program = parse(text)
        self.assertIsNotNone(program)  # TODO asserts

    def test_lambda_return_type_inline_func(self):
        text = """
        const a: int = (): func((a: int) => int) => (a: int): int => a;
        """
        program = parse(text)
        self.assertIsNotNone(program)  # TODO asserts

    def test_lambda_empty_args(self):
        text = "a = (): void => {};"
        program = parse(text)
        match program.objects:
            case [
                AssignmentStatement(
                    symbol='a',
                    right_value=CompFactor(
                        factor=Factor(
                            value=LambdaExpression(
                                arguments=[],
                                body=EmptyStatement(),
                                return_type=Void()
                            ),
                            minus=False
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_lambda_func_return_type_invalid_definition(self):
        text = """a = (): double => {};"""
        with self.assertRaises(InvalidReturnTypeError):
            parse(text)

    def test_lambda_func_return_type_nested(self):
        text = """
        const a: int = (): func((a: int) => func((b: int) => int)) => (a: int): func((b: int) => int) => a + b;
        """
        program = parse(text)
        self.assertIsNotNone(program)  # TODO asserts

    def test_lambda_func_return_type_missing_paren_around_args(self):
        text = "a = (a: int, b: str): func(c: float, d: float => void) => {};"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    def test_lambda_func_return_type_without_func_keyword(self):
        text = "a = (text: str): (() => void) => {}"
        with self.assertRaises(InvalidReturnTypeError):
            parse(text)

    def test_lambda_shortened_return_syntax(self):
        text = """
        const a: func(() => int) = (): int => a + b;
        """
        program = parse(text)
        match program.objects:
            case [
                DeclarationStatement(
                    left_value=Variable(name='a', type=Func(), nullable=False, mutable=False),
                    right_value=CompFactor(
                        factor=Factor(
                            value=LambdaExpression(
                                body=InlineReturnStatement(
                                    expression=CompFactor(
                                        factor=AdditiveExpression(
                                            left_value=Factor(
                                                value=Identifier(name='a'),
                                                minus=False
                                            ),
                                            operator=ArithmeticOperator.PLUS,
                                            right_value=Factor(
                                                value=Identifier(name='b'),
                                                minus=False
                                            )
                                        ),
                                        negation=False
                                    )
                                ),
                                return_type=Integer(),
                            ),
                            minus=False
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')


class ReturnStatementTests(unittest.TestCase):

    def test_bare_return(self):
        text = "return;"
        program = parse(text)
        match program.objects:
            case [ReturnStatement(expression=None)]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_return_literal(self):
        text = "return null;"
        program = parse(text)
        match program.objects:
            case [
                ReturnStatement(
                    expression=CompFactor(
                        factor=Factor(
                            value=Literal(value=None, type=Null()),
                            minus=False
                        ),
                        negation=False
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_return_with_expression(self):
        text = "return (a + b) or not 35;"
        program = parse(text)
        match program.objects:
            case [
                ReturnStatement(
                    expression=NullCoalesceExpression(
                        left_value=CompFactor(
                            factor=Factor(
                                value=CompFactor(
                                    factor=AdditiveExpression(
                                        left_value=Factor(
                                            value=Identifier(name='a'),
                                            minus=False
                                        ),
                                        operator=ArithmeticOperator.PLUS,
                                        right_value=Factor(
                                            value=Identifier(name='b'),
                                            minus=False
                                        )
                                    ),
                                    negation=False
                                ),
                                minus=False
                            ),
                            negation=False
                        ),
                        operator=LogicOperator.OR,
                        right_value=CompFactor(
                            factor=Factor(
                                value=Literal(value=35, type=Integer()),
                                minus=False
                            ),
                            negation=True
                        ),
                    )
                )
            ]:
                pass

            case _:
                self.fail('Objects do not match!')

    def test_return_without_semi(self):
        text = "return"
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    @parameterized.expand([
        ('return if;',),
        ('return void;',),
        ('return func;',),
        ('return while',),
    ])
    def test_return_keyword(self, text: str):
        with self.assertRaises(UnexpectedTokenError):
            parse(text)

    @parameterized.expand([
        ('return const a: int = 5;',),
        ('return a = 3;',),
        ('return while(True);',)
    ])
    def test_return_statement(self, text: str):
        with self.assertRaises(UnexpectedTokenError):
            parse(text)


class ExpressionsTests(unittest.TestCase):
    # TODO compare actual with expected object tree

    def test_null_coalesce_expression(self):
        text = "a ?? b"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_null_coalesce_expression_multiple_operands(self):
        text = "a ?? 15 ?? 100"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_or_expression(self):
        text = "a or b"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_or_expression_multiple_operands(self):
        text = "a or b or c"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_and_expression(self):
        text = "a and b"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_and_expression_multiple_operands(self):
        text = "a and b and c"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_equality_expression(self):
        text = "a == b"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_equality_expression_multiple_operands(self):
        text = "a == b != c"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_comp_factor_expr(self):
        text = "a + b"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_comp_factor_expr_negated(self):
        text = "not a"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_comp_factor_expr_multiple_negations(self):
        text = "not a or not b"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_additive_expression(self):
        text = "a + b"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_additive_expression_multiple_operands(self):
        text = "a - c + b - -d"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_multiplicative_expression(self):
        text = "a * b"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_multiplicative_expression_multiple_operands(self):
        text = "a / b % 4 * 2"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_factor_literal(self):
        text = "null"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_factor_literal_with_minus(self):
        text = "-3"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_factor_liter_with_minus_makes_no_sense(self):
        text = "-true"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_factor_identifier(self):
        text = "a"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_factor_identifier_with_minus(self):
        text = "-a"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_factor_func_call(self):
        text = "f()"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_factor_func_call_with_minus(self):
        text = "-f()"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_nested_expression(self):
        text = "(a - b)"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)

    def test_nested_expression_with_minus(self):
        text = "- (-a + b)"
        expr = setup_parser(text).try_parse_expression()
        self.assertIsNotNone(expr)


if __name__ == '__main__':
    unittest.main()
