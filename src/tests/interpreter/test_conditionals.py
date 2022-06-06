import unittest

from parameterized import parameterized

from src.errors.interpreter import UnexpectedTypeError
from src.tests.utils import setup_interpreter, mock_stdout


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

    def test_if_statement_true_condition_with_elifs(self):
        text = """
        if () {
        
        } elif () {
        
        } elif () {
        
        }
        """

    def test_if_statement_false_condition_one_of_elifs_true(self):
        text = """
        if () {
        
        } elif () {
        
        } elif () {
        
        } else () {
        
        }
        """

    def test_if_statement_false_condition_all_elif_false_condition(self):
        text = """
        if () {

        } elif () {

        } elif () {

        } else () {

        }
        """

    def test_if_statement_true_condition_with_else(self):
        text = """
        if () {

        } else () {

        }
        """

    def test_if_statement_false_condition_with_else(self):
        text = """
        if () {

        } else () {

        }
        """

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

    def test_nested_if_statements(self):
        text = """
        if (true) {
            if () {
                if () {
                
                }
            }
            elif () {
            
            }
        } else {
            if (false / null * true) {}
        }
        
        """

    def test_nested_if_statements_elif_else_in_wrong_places(self):
        text = """

        """

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
