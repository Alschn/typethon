import unittest

from parameterized import parameterized

from src.errors.interpreter import UnexpectedTypeError
from src.tests.utils import setup_interpreter, mock_stdout


# noinspection PyMethodMayBeStatic
class InterpreterConditionalsTests(unittest.TestCase):

    @mock_stdout
    def test_if_statement_true_condition(self, stdout):
        text = """
        if (true) {
            print("if");
        }
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "if\n")

    @mock_stdout
    def test_if_statement_false_condition(self, stdout):
        text = """
        if (false) {
            print("if");
        }
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "")

    @mock_stdout
    def test_if_statement_true_condition_with_elifs(self, stdout):
        text = """
        if (true or true or true or false) {
            const a: int = 0;
            print(a, "<- inside if");
        } elif (true) {
            print("this won't run");
        } elif (null) {
            print("this won't run as well");
        }
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue().strip(), "0 <- inside if")

    def test_if_statement_false_condition_one_of_elifs_true(self):
        text = """
        if (false) {
            const a: int = 11;
        } elif (null) {
            const a: int = 13;
        } elif (true) {
            const a: int = 15;
        } else { while(true) {} }
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        a = interpreter.env.get_variable('a')
        self.assertIsNone(a)  # variable exists in local scope, not in global scope

    @mock_stdout
    def test_if_statement_false_condition_all_elif_false_condition(self, stdout):
        text = """
        if (null) {
            while (true) {}
        } elif (false or not true) {
            while (true) {
                while (true) {}
            } 
        } elif (false or false) {
            while (true) {}
        } else {
            print("this will run");
        }
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "this will run\n")

    @mock_stdout
    def test_if_statement_true_condition_with_else(self, stdout):
        text = """
        if (true) {
            print("xd");
        } else () {
            while (true) {}
        }
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "xd\n")

    def test_if_statement_false_condition_with_else(self):
        text = """
        if (false) {
            while (true) {}
        } else {
            const a: func(() => void) = (): void => {};
            a();
        }
        """
        setup_interpreter(text).interpret()

    @mock_stdout
    def test_if_statement_false_condition_all_elif_false_condition_else_runs(self, stdout):
        text = """
        if ((12 % 2 + 3 - (2.25 / 5)) * 13 < 0) {   // false
            print("if");
        } elif (false or false or false) {          // false
            print("1st elif");
        } elif (false) {                            // false
            print("2nd elif");
        }
        else {                                      // this will run
            print("else");
        }
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "else\n")

    @mock_stdout
    def test_nested_if_statements(self, stdout):
        text = """
        if (true) {
            print("1");
            if (true) {
                print("2");
                if (false) {
                    print("3");
                }
            }
            elif (true) {
                print("4");
            }
        } else {
            if (false / null * true) { print(5); }
        }
        print(7);
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "1\n2\n7\n")

    @mock_stdout
    def test_if_statement_function_call_as_condition(self, stdout):
        text = """
        def f(): bool => true
        if (f()) { print("condition"); }
        """
        setup_interpreter(text).interpret()
        self.assertEqual(stdout.getvalue(), "condition\n")

    @parameterized.expand([
        ('1',),
        ('"1"',),
        ('0',),
        ('"0"',),
        ('1.0',),
        ('3 * 4',),
        ('5 - 0.5',),
        ('55 * 0',),
        ('12 / 34',),
        ('1 + 2 - 3 * 4 / 5 % 6 - -(7)',)
    ])
    def test_if_statement_condition_not_bool(self, invalid_condition: str):
        text = "if (" + invalid_condition + ") {}"
        with self.assertRaises(UnexpectedTypeError):
            setup_interpreter(text).interpret()


if __name__ == '__main__':
    unittest.main()
