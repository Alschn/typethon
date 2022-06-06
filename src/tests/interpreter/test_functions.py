import unittest
from io import StringIO
from unittest.mock import patch

from parameterized import parameterized

from src.errors.interpreter import RecursionLimitError, ReturnOutsideOfFunctionError, ReturnTypeMismatchError, \
    ArgumentsError, UnexpectedTypeError, UndefinedNameError, NotCallableError, ArgumentTypeError
from src.errors.parser import UnexpectedTokenError
from src.parser.types import Func, Void, Null, Integer, String, Float, Bool
from src.tests.utils import mock_stdout, setup_interpreter


# noinspection PyMethodMayBeStatic
class InterpreterFunctionsTests(unittest.TestCase):
    """
    Defining functions, calling functions, calling variables with function type
    """

    def test_function_return_argument(self):
        text = """
        def f(a: int): int => {
            return a;
        }
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        func_def = interpreter.env.get_fun_def('f')
        self.assertEqual(func_def.return_type, Integer())

    def test_function_returns_function(self):
        text = """
        def f(): func(() => void) => {
            return (): void => {};
        }
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        func_def = interpreter.env.get_fun_def('f')
        self.assertEqual(func_def.type, Func([], Func([], Void())))

    def test_function_return_empty(self):
        text = """
        def f(): void => {
            return;
        }
        
        let a?: int = f();
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        func_def = interpreter.env.get_fun_def('f')
        a = interpreter.env.get_variable('a')
        self.assertEqual(func_def.type, Func([], Void()))
        self.assertEqual(a.value.value, None)
        self.assertEqual(a.value.type, Null())

    def test_function_return_expression(self):
        text = """
        def f(a: int, b: int): bool => {
            return (a * b - 100) % 15 > 30 or a * a < -15 ?? 6;
        }
        const b: bool = f(15, 16);
        """
        setup_interpreter(text).interpret()

    def test_function_return_literal(self):
        text = """
        def f(): int => 1
        const a: int = f();
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        f = interpreter.env.get_fun_def('f')
        a = interpreter.env.get_variable('a')
        self.assertEqual(f.return_type, Integer())
        self.assertEqual(a.value.value, 1)
        self.assertEqual(a.value.type, Integer())

    def test_function_return_too_many_arguments(self):
        text = """
        def f(i: int): int => {
            return i, 2;
        }
        """
        # parser error
        with self.assertRaises(UnexpectedTokenError):
            setup_interpreter(text).interpret()

    def test_function_call_arguments_types_mismatch(self):
        text = """
        def f(a: int, b: str): void => {}
        let a: int = 0;
        f(a, a);
        """
        with self.assertRaises(ArgumentTypeError):
            setup_interpreter(text).interpret()

    def test_function_call_too_little_arguments(self):
        text = """
        def f(a: int, b: str): void => {}
        let a: int = 0;
        f(a);
        """
        with self.assertRaises(ArgumentsError):
            setup_interpreter(text).interpret()

    def test_function_call_too_many_arguments(self):
        text = """
        def f(a: int, b: str, c: bool): void => {}
        let a: int = 0;
        f(a, a, a, a);
        """
        with self.assertRaises(ArgumentsError):
            setup_interpreter(text).interpret()

    @mock_stdout
    def test_function_argument_func_type(self, stdout):
        text = """
        def f(a: int, lambda: func((a: int) => int)): void => {
            print(lambda(a));
        }
        
        const power: func((a: int) => int) = (a: int): int => a * a;
        
        f(15, power);
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        self.assertEqual(stdout.getvalue(), "225\n")

    def test_function_argument_func_type_invalid_operation(self):
        text = """
        def f(a: int, b: str): int => a * b
        f(1, "hello world");
        """
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('int', 'false'),
        ('float', '\"\"'),
        ('str', "2"),
        ('func(() => void)', "{}")
    ])
    def test_function_return_type_mismatch(self, return_type, return_value):
        text = f"""
        def f(): {return_type} => {return_value}
        f();
        """
        with self.assertRaises(ReturnTypeMismatchError):
            setup_interpreter(text).interpret()

    def test_function_call(self):
        text = """
        def add(a: int, b: int): int => a + b
        const c: int = add(1, 2); 
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        c = interpreter.env.get_variable('c')
        self.assertEqual(c.value.value, 3)
        self.assertEqual(c.value.type, Integer())

    def test_function_call_variable_callable(self):
        text = """
        const a: func(() => void) = (): void => {};
        a();
        """
        setup_interpreter(text).interpret()

    @mock_stdout
    def test_function_call_chained(self, stdout):
        text = """
        def f(): func(() => void) => {
            print("1st call");
            return (): void => { print("2nd call"); };
        }
        
        f()();
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "1st call\n2nd call\n")

    def test_function_call_chained_object_not_callable(self):
        text = """
        def f(): func(() => int) => {
            return (): int => 1;
        }
        f()()();
        """
        with self.assertRaises(NotCallableError):
            setup_interpreter(text).interpret()

    def test_function_call_function_does_not_exist(self):
        text = "f();"
        with self.assertRaises(UndefinedNameError):
            setup_interpreter(text).interpret()

    def test_function_call_function_defined_below_code(self):
        text = """
        f();
        def f(): void => {}
        """
        with self.assertRaises(UndefinedNameError):
            setup_interpreter(text).interpret()

    def test_function_call_not_a_callable(self):
        text = "let a: int = 0; a();"
        with self.assertRaises(NotCallableError):
            setup_interpreter(text).interpret()

    @mock_stdout
    def test_recursive_function_call(self, stdout):
        text = """
        def factorial(n: int): int => {
            if (n == 1) {
                return n;
            }
            return n * factorial(n - 1);
        }

        const result: int = factorial(5);
        print(result);
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        result = interpreter.env.get_variable('result')
        self.assertEqual(result.value.value, 120)
        self.assertEqual(result.value.type, Integer())
        self.assertEqual(stdout.getvalue(), "120\n")

    @mock_stdout
    def test_recursive_function_call_recurrence_error(self, stdout):
        text = """
        def factorial(n: int): int => {
            if (n == 1) {
                return n;
            }
            return n * factorial(n - 1);
        }

        print(factorial(120));
        """
        with self.assertRaises(RecursionLimitError):
            setup_interpreter(text).interpret()

    def test_recursive_self_call(self):
        text = """
        def f(): void => {
            f();
        }
        
        f();
        """
        with self.assertRaises(RecursionLimitError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ("true", "true\n"),
        ("false", "false\n"),
        ("1", "1\n"),
        ("\"hello!\"", "hello!\n"),
        ("null", "null\n"),
    ])
    def test_builtin_print(self, argument, expected):
        text = f"print({argument});"
        with patch('sys.stdout', new_callable=StringIO) as sout:
            setup_interpreter(text).interpret()
            self.assertEqual(sout.getvalue(), expected)

    @mock_stdout
    def test_builtin_print_function_type(self, stdout):
        text = """
        def f(): func(() => void) => (): void => {}
        print(f());
        """
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    @mock_stdout
    def test_builtin_print_multiple_arguments(self, stdout):
        text = "print(1, \"Hello world\", true, false, null);"
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue().strip(), "1 Hello world true false null")

    @parameterized.expand([
        ("true", "true", String()),
        ("false", "false", String()),
        ("1", "1", String()),
        ("\"hello!\"", "hello!", String()),
        ("null", "null", String()),
    ])
    def test_builtin_string(self, arg, value, typ):
        text = f"const a: str = String({arg});"
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        a = interpreter.env.get_variable('a')
        self.assertEqual(a.value.value, value)
        self.assertEqual(a.value.type, typ)

    @parameterized.expand([
        ("true", "false"),
        ("1", "2", "3"),
        ("false", "3.0", "\"\"", "null"),
    ])
    def test_builtin_string_too_many_arguments(self, *args):
        arguments = ", ".join(args)
        text = f"const a: str = String({arguments});"
        with self.assertRaises(ArgumentsError):
            setup_interpreter(text).interpret()

    def test_builtin_string_no_arguments(self):
        text = "const t: str = String();"
        with self.assertRaises(ArgumentsError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('1', 1),
        ('1.2', 1),
        ('2.0', 2),
    ])
    def test_builtin_integer(self, text, value):
        text = f"const i: int = Integer({text});"
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        i = interpreter.env.get_variable('i')
        self.assertEqual(i.value.value, value)
        self.assertEqual(i.value.type, Integer())

    @parameterized.expand([
        ("true", "false"),
        ("1", "2", "3"),
        ("false", "3.0", "\"\"", "null"),
    ])
    def test_builtin_integer_too_many_arguments(self, *args):
        arguments = ", ".join(args)
        text = f"const a: str = String({arguments});"
        with self.assertRaises(ArgumentsError):
            setup_interpreter(text).interpret()

    def test_builtin_integer_no_arguments(self):
        text = "const i: int = Integer();"
        with self.assertRaises(ArgumentsError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('1', 1.0),
        ('2.1', 2.1),
        ('6.0', 6.0),
    ])
    def test_builtin_float(self, text, value):
        text = f"const f: float = Float({text});"
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        f = interpreter.env.get_variable('f')
        self.assertEqual(f.value.value, value)
        self.assertEqual(f.value.type, Float())

    @parameterized.expand([
        ("true", "false"),
        ("1", "2", "3"),
        ("false", "3.0", "\"\"", "null"),
    ])
    def test_builtin_float_too_many_arguments(self, *args):
        arguments = ", ".join(args)
        text = f"const a: str = String({arguments});"
        with self.assertRaises(ArgumentsError):
            setup_interpreter(text).interpret()

    def test_builtin_float_no_arguments(self):
        text = "const f: float = Float();"
        with self.assertRaises(ArgumentsError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ("true", True),
        ("false", False),
        ("null", False),
    ])
    def test_builtin_boolean(self, text, value):
        text = f"const b: bool = Boolean({text});"
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        b = interpreter.env.get_variable('b')
        self.assertEqual(b.value.value, value)
        self.assertEqual(b.value.type, Bool())

    @parameterized.expand([
        ("true", "false"),
        ("1", "2", "3"),
        ("false", "3.0", "\"\"", "null"),
    ])
    def test_builtin_boolean_too_many_arguments(self, *args):
        arguments = ", ".join(args)
        text = f"const a: str = String({arguments});"
        with self.assertRaises(ArgumentsError):
            setup_interpreter(text).interpret()

    def test_builtin_boolean_no_arguments(self):
        text = "const a: bool = Boolean();"
        with self.assertRaises(ArgumentsError):
            setup_interpreter(text).interpret()

    @mock_stdout
    def test_overwrite_previously_declared_function(self, stdout):
        text = """
        def add(a: int, b: int): void => print(a + b)
        def add(text: str): void => print(text)
        add("Overwriting functions works");
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "Overwriting functions works\n")

    @mock_stdout
    def test_overwrite_builtin_function(self, stdout):
        text = """
        def print(a: int): void => {}
        print(1);
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "")

    @parameterized.expand([
        ('return;',),
        ('while(true) { return; }',),
        ('if(true) { return; }',),
    ])
    def test_return_outside_of_function(self, text):
        with self.assertRaises(ReturnOutsideOfFunctionError):
            setup_interpreter(text).interpret()


if __name__ == '__main__':
    unittest.main()
