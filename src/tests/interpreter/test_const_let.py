import unittest

from parameterized import parameterized

from src.errors.interpreter import NotNullableError, TypeMismatchError, AssignmentTypeMismatchError, \
    ConstAssignmentError, ConstRedeclarationError, UndefinedNameError
from src.parser.types import Integer, Float, String, Bool, Null
from src.tests.utils import setup_interpreter, mock_stdout


class InterpreterConstLetAssignmentAndDeclarationTests(unittest.TestCase):

    @parameterized.expand([
        ('let a: int = 0;', 0, Integer()),
        ('let a: int = 15;', 15, Integer()),
        ('let a: float = 0.0;', 0, Float()),
        ('let a: float = 1;', 1, Float()),
        ('let a: str = "Hello world!";', "Hello world!", String()),
        ('let a: str = "";', "", String()),
        ('let a: bool = true;', True, Bool()),
        ('let a: bool = false;', False, Bool()),
    ])
    def test_declaration_let(self, text, value, typ):
        interpreter = setup_interpreter(text)
        var_name = text.split('let ')[1][0]
        interpreter.interpret()
        variable = interpreter.env.get_variable(var_name)
        literal = variable.value
        self.assertTrue(variable.mutable)
        self.assertFalse(variable.nullable)
        self.assertTrue(variable.type == literal.type)
        self.assertEqual(literal.value, value)
        self.assertEqual(literal.type, typ)

    @parameterized.expand([
        ('let a: int = null;',),
        ('let a: bool = null;',),
        ('def f(): void => {} let a: str = f();',),
    ])
    def test_declaration_let_not_nullable_right_side_nullable(self, text):
        with self.assertRaises(NotNullableError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('let a?: int = 0;', 0, Integer(), Integer()),
        ('let a?: int = null;', None, Integer(), Null()),
        ('def f(): void => {} let a?: int = f();', None, Integer(), Null()),

        ('let a?: float = 0.0;', 0, Float(), Float()),
        ('let a?: float = 0;', 0, Float(), Float()),
        ('let a?: float = null;', None, Float(), Null()),
        ('def f(): void => {} let a?: float = f();', None, Float(), Null()),

        ('let a?: str = "Hello world!";', "Hello world!", String(), String()),
        ('let a?: str = "";', "", String(), String()),
        ('let a?: str= null;', None, String(), Null()),
        ('def f(): void => {} let a?: str = f();', None, String(), Null()),

        ('let a?: bool = true;', True, Bool(), Bool()),
        ('let a?: bool = false;', False, Bool(), Bool()),
        ('let a?: bool = null;', None, Bool(), Null()),
        ('def f(): void => {} let a?: bool = f();', None, Bool(), Null()),
    ])
    def test_declaration_let_nullable(self, text, value, var_type, value_type):
        interpreter = setup_interpreter(text)
        var_name = text.split('let ')[1][0]
        interpreter.interpret()
        variable = interpreter.env.get_variable(var_name)
        literal = variable.value
        self.assertTrue(variable.mutable)
        self.assertTrue(variable.nullable)
        self.assertEqual(variable.type, var_type)
        self.assertEqual(literal.value, value)
        self.assertEqual(literal.type, value_type)

    @parameterized.expand([
        ('let a: int = "";',),
        ('let a: int = true;',),
        ('let a: int = 3.0;',),
        ('let b: float = "aaaa";',),
        ('let b: float = true;',),
        ('let b: float = false;',),
        ('let c: str = 1;',),
        ('let c: str = 1.0;',),
        ('let c: str = true;',),
        ('let c: str = false;',),
        ('let d: bool = 1;',),
        ('let d: bool = 0;',),
        ('let d: bool = "";',),
        ('let d: bool = "aaa";',),
        ('let d: bool = 1.0;',),
        ('let d: bool = 0.0;',),
    ])
    def test_declaration_let_type_mismatch(self, text):
        with self.assertRaises(TypeMismatchError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('const a: int = 0;', 0, Integer()),
        ('const a: float = 0.0;', 0, Float()),
        ('const a: float = 0;', 0, Float()),
        ('const a: str = "Hello world!";', "Hello world!", String()),
        ('const a: str = "";', "", String()),
        ('const a: bool = true;', True, Bool()),
        ('const a: bool = false;', False, Bool()),
    ])
    def test_declaration_const(self, text, value, typ):
        interpreter = setup_interpreter(text)
        var_name = text.split('const ')[1][0]
        interpreter.interpret()
        variable = interpreter.env.get_variable(var_name)
        literal = variable.value
        self.assertFalse(variable.mutable)
        self.assertFalse(variable.nullable)
        self.assertTrue(variable.type == literal.type)
        self.assertEqual(literal.value, value)
        self.assertEqual(literal.type, typ)

    @parameterized.expand([
        ('let a: int = 0; a = 1;', 1, Integer()),
        ('let a: int = 0; a = a + 2;', 2, Integer()),
        ('let a: float = 21; a = 4;', 4, Float()),
        ('let a: float = 37; a = 2.0;', 2.0, Float()),
        ('let a: str = "Hello"; a = a + " world!";', "Hello world!", String()),
        ('let a: bool = true; a = false;', False, Bool()),
        ('let a: bool = false; a = true;', True, Bool()),
    ])
    def test_reassignment_to_let(self, text, value, typ):
        interpreter = setup_interpreter(text)
        var_name = text.split('let ')[1][0]
        interpreter.interpret()
        variable = interpreter.env.get_variable(var_name)
        literal = variable.value
        self.assertTrue(variable.mutable)
        self.assertFalse(variable.nullable)
        self.assertTrue(variable.type == literal.type)
        self.assertEqual(literal.value, value)
        self.assertEqual(literal.type, typ)

    @parameterized.expand([
        ('let a: int = 0; a = "";',),
        ('let a: int = 0; a = false;',),
        ('let a: float = 21; a = true;',),
        ('let a: float = 37; a = "xd";',),
        ('let a: str = "Hello"; a = 1;',),
        ('let a: bool = true; a = "aaaaa";',),
        ('let a: bool = false; a = 6.9;',),
    ])
    def test_reassignment_to_let_type_mismatch(self, text):
        with self.assertRaises(AssignmentTypeMismatchError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('const a: int = 0; a = 15;',),
        ('const a: int = 0; a = "";',),
        ('const a: int = 0; a = false;',),
        ('const a: float = 21; a = 42.0;',),
        ('const a: float = 0; a = 37.88;',),
        ('const a: float = 6.9; a = "xd";',),
        ('const a: str = "Hello"; a = 1;',),
        ('const a: bool = true; a = "aaaaa";',),
        ('const a: bool = false; a = 6.9;',),
    ])
    def test_reassignment_to_const(self, text):
        with self.assertRaises(ConstAssignmentError):
            setup_interpreter(text).interpret()

    @parameterized.expand([
        ('let a: int = 0; let a: float = 15;', 15, Float()),
        ('let a: int = 0; let a: str = "";', "", String()),
        ('let a: int = 0; let a: bool = false;', False, Bool()),
        ('let a: float = 21; let a: int = 0;', 0, Integer()),
        ('let a: float = 0; let a: float = 12;', 12, Float()),
        ('let a: float = 6.9; let a: str = "xd";', "xd", String()),
        ('let a: str = "Hello"; let a: int = 1;', 1, Integer()),
        ('let a: bool = true; let a: str = "aaaaa";', "aaaaa", String()),
        ('let a: bool = false; let a: float = 6.9;', 6.9, Float()),
    ])
    def test_redeclaration_let(self, text, new_value, new_type):
        interpreter = setup_interpreter(text)
        var_name = text.split('let ')[1][0]
        interpreter.interpret()
        variable = interpreter.env.get_variable(var_name)
        literal = variable.value
        self.assertEqual(variable.type, new_type)
        self.assertEqual(literal.value, new_value)
        self.assertEqual(literal.type, new_type)

    @parameterized.expand([
        ('const a: int = 0; const a: float = 15;',),
        ('const a: int = 0; const a: str = "";',),
        ('const a: int = 0; const a: bool = false;',),
        ('const a: float = 21; const a: int = 0;',),
        ('const a: float = 0; const a: float = 12;',),
        ('const a: float = 6.9; const a: str = "xd";',),
        ('const a: str = "Hello"; const a: int = 1;',),
        ('const a: bool = true; const a: str = "aaaaa";',),
        ('const a: bool = false; const a: float = 6.9;',),
    ])
    def test_redeclaration_const(self, text):
        with self.assertRaises(ConstRedeclarationError):
            setup_interpreter(text).interpret()

    def test_assign_to_local_variable_from_global_scope(self):
        text = """
        if (true) {
            const a: int = 0;
        }
        a = 10;
        """
        with self.assertRaises(UndefinedNameError):
            setup_interpreter(text).interpret()

    @mock_stdout
    def test_redeclare_const_value_from_local_scope_in_global_scope(self, stdout):
        text = """
        if (true) {
            const a: int = 0;
        }
        const a: str = "Hello world!";
        print(a);
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        a = interpreter.env.get_variable('a')
        self.assertEqual(a.value.value, "Hello world!")
        self.assertEqual(a.value.type, String())
        self.assertEqual(stdout.getvalue(), "Hello world!\n")

    def test_assign_to_global_variable_from_local_scope(self):
        text = """
        let a: int = 0;
        while (a == 0) {
            a = 1;
        }
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        a = interpreter.env.get_variable('a')
        self.assertEqual(a.value.value, 1)
        self.assertEqual(a.value.type, Integer())

    def test_redeclare_global_const_variable_in_local_scope(self):
        text = """
        const a: int = 0;
        if (true) {
            const a: float = 100;
        }
        """
        with self.assertRaises(ConstRedeclarationError):
            setup_interpreter(text).interpret()

    def test_redeclare_global_const_variable_as_let_in_local_scope(self):
        text = """
        const a: int = 0;
        if (true) {
            let a: float = 100;
        }
        """
        with self.assertRaises(ConstRedeclarationError):
            setup_interpreter(text).interpret()

    def test_redeclare_global_let_variable_in_local_scope(self):
        text = """
        let a: int = 0;
        if (true) {
            let a: float = 100;
        }
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        a = interpreter.env.get_variable('a')
        self.assertTrue(a.mutable)
        self.assertEqual(a.value.value, 100)
        self.assertEqual(a.value.type, Float())

    def test_redeclare_global_let_variable_as_const_variable_in_local_scope(self):
        text = """
        let a: int = 0;
        if (true) {
            const a: float = 100;
        }
        """
        interpreter = setup_interpreter(text)
        interpreter.interpret()
        a = interpreter.env.get_variable('a')
        self.assertFalse(a.mutable)
        self.assertEqual(a.value.value, 100)
        self.assertEqual(a.value.type, Float())


if __name__ == '__main__':
    unittest.main()
