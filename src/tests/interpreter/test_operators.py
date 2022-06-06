import unittest

from parameterized import parameterized

from src.tests.utils import setup_interpreter


class InterpreterOperatorAllowedTypesTests(unittest.TestCase):

    @parameterized.expand([
        ("1 + 1", 2),
        ("\"hello\" + \"world\"", "helloworld"),
        ("1 + 0.5", 1.5),
        ("0.5 + 1", 1.5),
        ("1.25 + 1.3", 2.55),
    ])
    def test_plus(self, text, expected):
        text = f"""
        print({text});
        """
        setup_interpreter(text).interpret()

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
        text = f"""
        print({text});
        """
        with self.assertRaises(Exception):
            setup_interpreter(text).interpret()

    def test_minus(self):
        pass

    def test_minus_type_mismatch(self):
        pass

    def test_mul(self):
        pass

    def test_mul_type_mismatch(self):
        pass

    def test_div(self):
        pass

    def test_div_zero_division(self):
        pass

    def test_div_type_mismatch(self):
        pass

    def test_modulo(self):
        pass

    def test_modulo_zero_division(self):
        pass

    def test_modulo_type_mismatch(self):
        pass

    def test_negation_minus(self):
        pass

    def test_negation_minus_type_mismatch(self):
        pass

    def test_negation_not(self):
        pass

    def test_negation_not_type_mismatch(self):
        pass

    def test_logic_or(self):
        pass

    def test_logic_or_type_mismatch(self):
        pass

    def test_logic_and(self):
        pass

    def test_logic_and_type_mismatch(self):
        pass

    def test_lt(self):
        pass

    def test_lt_type_mismatch(self):
        pass

    def test_lte(self):
        pass

    def test_lte_type_mismatch(self):
        pass

    def test_gt(self):
        pass

    def test_gt_type_mismatch(self):
        pass

    def test_gte(self):
        pass

    def test_gte_type_mismatch(self):
        pass

    def test_eq(self):
        pass

    def test_eq_type_mismatch(self):
        pass

    def test_neq(self):
        pass

    def test_neq_type_mismatch(self):
        pass

    def test_null_coalesce(self):
        pass

    def test_null_coalesce_null_left_side_right_not_null(self):
        pass

    def test_null_coalesce_null_right_side_left_not_null(self):
        pass

    def test_null_coalesce_null_both_sides(self):
        pass


if __name__ == '__main__':
    unittest.main()
