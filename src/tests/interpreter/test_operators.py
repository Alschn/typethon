import unittest
from io import StringIO
from unittest.mock import patch

from parameterized import parameterized

from src.errors.interpreter import UnexpectedTypeError, NotNullableError, DivisionByZeroError
from src.parser.types import Null
from src.tests.utils import setup_interpreter


class InterpreterOperatorAllowedTypesTests(unittest.TestCase):

    @parameterized.expand([
        ("1 + 1", "2"),
        ("\"hello\" + \"world\"", "helloworld"),
        ("1 + 0.5", "1.5"),
        ("0.5 + 1", "1.5"),
        ("1.25 + 1.3", "2.55"),
        ("1.25 + -0.25", "1.0"),
        ("-5 + 3", "-2")
    ])
    def test_plus(self, text, expected):
        text = f"print({text});"
        interpreter = setup_interpreter(text)
        with patch("sys.stdout", new_callable=StringIO) as sout:
            interpreter.interpret()
            self.assertEqual(sout.getvalue().strip(), expected)

    @parameterized.expand([
        ("1 + \"\"",),
        ("\"a\" + 2",),
        ("0.5 + \"\"",),
        ("true + 1",),
        ("false + 1",),
        ("true + 0.5",),
        ("false + 0.8",),
        ("true + true",),
    ])
    def test_plus_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('1 - 2', -1),
        ('13.5 - 10.5', 3.0),
        ('12 - 2.50', 9.5),
        ('12 - -3', 15),
        ('-12 - 3', -15),
        ('-12 - -3', -9)
    ])
    def test_minus(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), str(expected_value))

    @parameterized.expand([
        ("1 - \"\"",),
        ("\"a\" - 2",),
        ("0.5 - \"\"",),
        ("true - 1",),
        ("false - 1",),
        ("true - 0.5",),
        ("false - 0.8",),
        ("true - true",),
    ])
    def test_minus_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('1 * 2', 2),
        ('2 * 3.0', 6.0),
        ('12 * -4', -48),
        ('-4 * -4', 16),
        ('-4 * -(4)', 16),
        ('-4 * -(-4)', -16)
    ])
    def test_mul(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), str(expected_value))

    @parameterized.expand([
        ("1 * \"\"",),
        ("\"a\" * 2",),
        ("0.5 * \"\"",),
        ("true * 1",),
        ("false * 1",),
        ("true * 0.5",),
        ("false * 0.8",),
        ("true * true",),
        ("\"abc\" * 2",),
        ("\'abc\' * \"fgh\"",),
    ])
    def test_mul_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('1 / 1', 1.0),
        ('1 / 2', 0.5),
        ('2 / 4.0', 0.5),
        ('12 / -4', -3.0),
        ('-4 / -4', 1.0),
        ('-4 / -(4)', 1.0),
        ('-4 / -(-4)', -1.0)
    ])
    def test_div(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), str(expected_value))

    def test_div_zero_division(self):
        text = """const a: int = 3 / 0;"""
        with self.assertRaises(DivisionByZeroError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ("1 / \"\"",),
        ("\"a\" / 2",),
        ("0.5 / \"\"",),
        ("true / 1",),
        ("false / 1",),
        ("true / 0.5",),
        ("false / 0.8",),
        ("true / true",),
        ("\"abc\" / 2",),
        ("\"abc\" / \"fgh\"",),
    ])
    def test_div_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('1 % 1', 0),
        ('15 % 3', 0),
        ('2 % 3', 2),
    ])
    def test_modulo(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), str(expected_value))

    def test_modulo_zero_division(self):
        text = """const a: int = 3 % 0;"""
        with self.assertRaises(DivisionByZeroError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ("1 % \"\"",),
        ("\"a\" % 2",),
        ("0.5 % \"\"",),
        ("true % 1",),
        ("false % 1",),
        ("true % 0.5",),
        ("false % 0.8",),
        ("true % true",),
        ("'abc' % 2",),
        ("'abc' % 'fgh'",),
    ])
    def test_modulo_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ("-'a'",),
        ("-true",),
        ("-false",),
        ("-null",)
    ])
    def test_negation_minus_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('not true', "false"),
        ('not false', "true"),
        ('not false or not false', "true"),
        ('not true or false and not true', "false")
    ])
    def test_negation_not(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), expected_value)

    @parameterized.expand([
        ("not 'a'",),
        ("not 1",),
        ("not 1.5",),
    ])
    def test_negation_not_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('true or true', "true"),
        ('true or false', "true"),
        ('false or true', "true"),
        ('false or false', "false"),
        ('1 > 3 or true', "true"),
        ('2 % 3 == 0 or (1 + 2) * 3 == 9', "true"),
    ])
    def test_logic_or(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), expected_value)

    @parameterized.expand([
        ("1 or \"\"",),
        ("\"a\" or 2",),
        ("0.5 or \"\"",),
        ("true or 1",),
        ("false or 1",),
        ("true or 0.5",),
        ("false or 0.8",),
    ])
    def test_logic_or_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('true and true', "true"),
        ('true and false', "false"),
        ('false and true', "false"),
        ('false and false', "false"),
        ('1 > 3 and true', "false"),
        ('2 % 3 == 0 and (1 + 2) * 3 == 9', "false"),
    ])
    def test_logic_or(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), expected_value)

    @parameterized.expand([
        ("1 and \"\"",),
        ("\"a\" and 2",),
        ("0.5 and \"\"",),
        ("true and 1",),
        ("false and 1",),
        ("true and 0.5",),
        ("false and 0.8",),
    ])
    def test_logic_and_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('1 < 2', "true"),
        ('7 * 7 < 50', "true"),
        ('(1 * 2) * 3 / 3 < 1000', "true"),
    ])
    def test_lt(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), expected_value)

    @parameterized.expand([
        ("1 < \"\"",),
        ("\"a\" < 2",),
        ("0.5 < \"\"",),
        ("true < 1",),
        ("false < 1",),
        ("true < 0.5",),
        ("false < 0.8",),
    ])
    def test_lt_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('1 <= 2', "true"),
        ('2 <= 2', "true"),
        ('7 * 7 <= 49', "true"),
        ('(1 * 2) * 3 / 3 <= 1000', "true"),
    ])
    def test_lte(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), expected_value)

    @parameterized.expand([
        ("1 <= \"\"",),
        ("\"a\" <= 2",),
        ("0.5 <=\"\"",),
        ("true <= 1",),
        ("false <= 1",),
        ("true <= 0.5",),
        ("false <= 0.8",),
    ])
    def test_lte_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('1 > 2', "false"),
        ('1 > 1', "false"),
        ('7 * 7 > 50', "false"),
        ('(1 * 2) * 3 / 3 > 1000', "false"),
    ])
    def test_gt(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), expected_value)

    @parameterized.expand([
        ("1 > \"\"",),
        ("\"a\" > 2",),
        ("0.5 > \"\"",),
        ("true > 1",),
        ("false > 1",),
        ("true > 0.5",),
        ("false > 0.8",),
    ])
    def test_gt_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('1 >= 2', "false"),
        ('7 * 7 >= 50', "false"),
        ('1000 >= 1000', "true"),
    ])
    def test_gte(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), expected_value)

    @parameterized.expand([
        ("1 >= \"\"",),
        ("\"a\" >= 2",),
        ("0.5 >= \"\"",),
        ("true >= 1",),
        ("false >= 1",),
        ("true >= 0.5",),
        ("false >= 0.8",),
    ])
    def test_gte_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('true == true', "true"),
        ('false == false', "true"),
        ('true == false', "false"),
        ('false == true', "false"),
        ('null == \"123\"', "false"),
        ('null == null', "true"),
        ('null == false', "false"),
        ('null == true', "false")
    ])
    def test_eq(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), expected_value)

    @parameterized.expand([
        ("1 == \"\"",),
        ("\"a\" == 2",),
        ("0.5 == \"\"",),
        ("true == 1",),
        ("false == 1",),
        ("true == 0.5",),
        ("false == 0.8",),
    ])
    def test_eq_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('true != true', "false"),
        ('false != false', "false"),
        ('true != false', "true"),
        ('false != true', "true"),
        ('null != \"123\"', "true"),
        ('"abc" != "cde"', "true"),
        ('"a" != "a"', "false"),
        ('1 != 200', "true"),
        ('null != null', "false"),
        ('null != false', "true"),
        ('null != true', "true")
    ])
    def test_neq(self, value, expected_value):
        text = f"print({value});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue().strip(), expected_value)

    @parameterized.expand([
        ("1 != \"\"",),
        ("\"a\" != 2",),
        ("0.5 != \"\"",),
        ("true != 1",),
        ("false != 1",),
        ("true != 0.5",),
        ("false != 0.8",),
    ])
    def test_neq_type_mismatch(self, text):
        text = f"let a?: str = {text};"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    def test_null_coalesce(self):
        text = """
        const a: int = 15;
        const b: int = a ?? 30;
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        b = interpreter.env.get_variable('b')
        self.assertEqual(b.value.value, 15)

    def test_null_coalesce_null_left_side_right_not_null(self):
        text = """
        const a?: int = null;
        const b: int = a ?? 30;
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        b = interpreter.env.get_variable('b')
        self.assertEqual(b.value.value, 30)

    def test_null_coalesce_null_right_side_left_not_null(self):
        text = """
        const a?: int = 15;
        const b: int = a ?? null;
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        b = interpreter.env.get_variable('b')
        self.assertEqual(b.value.value, 15)

    def test_null_coalesce_null_both_sides(self):
        text = """
        const a?: int = null ?? null;
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        a = interpreter.env.get_variable('a')
        self.assertEqual(a.value.value, None)
        self.assertEqual(a.value.type, Null())

    def test_null_coalesce_null_both_sides_assignment_to_not_nullable(self):
        text = """
        const a: int = null ?? null;
        """
        with self.assertRaises(NotNullableError):
            setup_interpreter(text).interpret()


if __name__ == '__main__':
    unittest.main()
