import unittest

from src.errors.interpreter import UnexpectedTypeError
from src.parser.types import Bool
from src.tests.utils import setup_interpreter, mock_stdout


# noinspection PyMethodMayBeStatic
class InterpreterWhileLoopTests(unittest.TestCase):

    @mock_stdout
    def test_while_loop_condition_true(self, stdout):
        text = """
        let i: int = 0;
        while (i < 5) {
            print(i);
            i = i + 1;
        }
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "0\n1\n2\n3\n4\n")

    @mock_stdout
    def test_while_loop_condition_false(self, stdout):
        text = """
        while (false) {
            print("test");
        }
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "")

    def test_while_loop_condition_function_call(self):
        text = """
        def f(i: float): bool => i > 2
        let a: float = 1;
        while (f(a) or false) { 
            a = a + 1.0; 
        }
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        var = interpreter.env.get_variable('a')
        self.assertEqual(var.value.value, 1)

    def test_while_loop_complex_condition(self):
        text = """
        let b: float = 2.13;
        let c: int = 7;
        def f(): int => 2
        const cond: bool = (9 * ((11 - b) / b - c) % 2 * f() < 0);
        
        while (cond) { }
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        condition = interpreter.env.get_variable('cond')
        self.assertEqual(condition.value.value, False)
        self.assertEqual(condition.value.type, Bool())

    def test_while_loop_condition_not_bool(self):
        text = """
        while (1) {}
        """
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()

    def test_while_loop_nested(self):
        text = """
        let i: int = 0;
        while (i < 10) {
            while (i < 5) {
                i = i + 1;
            }
            i = i + 1;
        }
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        i = interpreter.env.get_variable('i')
        self.assertEqual(i.value.value, 10)

    def test_while_loop_with_mixed_statements(self):
        text = """
        let a: bool = true;
        while (a) {
            if (0 > 10) print("haha");
            let i: int = 0;
            if (i == 0) {
                a = false;
            } else {
                while (false) { print("ups"); }
            }
        }
        """
        setup_interpreter(text).interpret()

    def test_while_loop_break_condition_deeply_nested(self):
        text = """
        let a: int = 0;
        while (a < 1000) {
            if (a == 0) {
                if (true) {
                    if (true) {
                        if (true) {
                            a = a + 100;
                        }
                        while (a <= 901) { a = a + 1; }
                    }
                }
            }
            while (a > 900 and a < 1000) {
                if (a == 999 and true and true) a = 1000;
                a = a + 1;
            }
        }
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()

    def test_while_loop_escape_with_return_in_function(self):
        text = """
        def f(): void => {
            while (true) {
                return;
            }
        }
        f();
        """
        setup_interpreter(text).interpret()

    def test_while_loop_escape_nested_loop_with_return_in_function(self):
        text = """
        def f(): void => {
            while (true) {
                while (true) {
                    return;
                }
            }
        }
        f();
        """
        setup_interpreter(text).interpret()


if __name__ == '__main__':
    unittest.main()
