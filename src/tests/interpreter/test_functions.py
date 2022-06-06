import unittest

from parameterized import parameterized

from src.errors.interpreter import RecursionLimitError
from src.tests.utils import mock_stdout, setup_interpreter


class InterpreterFunctionsTests(unittest.TestCase):
    """
    Defining functions, calling functions, calling variables with function type
    """

    def test_function_return_argument(self):
        text = """
        def function(a: int): int => {
            return a;
        }
        """

    def test_function_returns_function(self):
        text = """
        def function(): func(() => void) => {
            return (): void => {};
        }
        """

    def test_function_return_empty(self):
        pass

    def test_function_return_expression(self):
        pass

    def test_function_return_literal(self):
        pass

    def test_function_return_too_many_arguments(self):
        pass

    def test_functions_too_little_arguments(self):
        pass

    def test_functions_too_many_arguments(self):
        pass

    def test_function_arguments_types_mismatch(self):
        pass

    def test_function_return_type_mismatch(self):
        pass

    def test_function_argument_func_type(self):
        pass

    def test_function_argument_func_type_invalid_operation(self):
        pass

    def test_function_call(self):
        pass

    def test_function_call_variable_not_callable(self):
        pass

    def test_function_call_variable_callable(self):
        pass

    def test_function_call_chained(self):
        pass

    def test_function_call_chained_object_not_callable(self):
        pass

    def test_function_call_function_does_not_exist(self):
        pass

    def test_function_call_function_defined_below_code(self):
        text = """
        f();
        
        def f(): void => {}
        """

    def test_recursive_function_call(self):
        text = """
        def factorial(n: int): int => {
            if (n == 1) {
                return n;
            }
            return n * factorial(n - 1);
        }

        print(factorial(5));
        """

    def test_recursive_function_call_recurrence_error(self):
        text = """
        def factorial(n: int): int => {
            if (n == 1) {
                return n;
            }
            return n * factorial(n - 1);
        }

        print(factorial(120));
        """

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
        ("\"hello!\"", "\"hello!\"\n"),
        ("null", "null\n"),
    ])
    def test_builtin_print(self, argument, expected):
        text = f"print({argument});"
        setup_interpreter(text).interpret()

    @mock_stdout
    def test_builtin_print_multiple_arguments(self, stdout):
        text = "print(1, \"Hello world\", true, false, null);"
        setup_interpreter(text).interpret()

    def test_builtin_print_function(self):
        pass

    def test_builtin_string(self):
        pass

    def test_builtin_string_too_many_arguments(self):
        pass

    def test_builtin_string_no_arguments(self):
        pass

    def test_builtin_integer(self):
        pass

    def test_builtin_integer_too_many_arguments(self):
        pass

    def test_builtin_integer_no_arguments(self):
        pass

    def test_builtin_float(self):
        pass

    def test_builtin_float_too_many_arguments(self):
        pass

    def test_builtin_float_no_arguments(self):
        pass

    def test_builtin_boolean(self):
        pass

    def test_builtin_boolean_too_many_arguments(self):
        pass

    def test_builtin_boolean_no_arguments(self):
        pass

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


if __name__ == '__main__':
    unittest.main()
