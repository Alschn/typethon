import random
import unittest
from string import ascii_lowercase as letters

from parameterized import parameterized

from src.errors.error import LexerError
from src.lexer.lexer import Lexer
from src.lexer.token_type import TokenType, KEYWORDS, ETX_VALUE
from src.tests.utils import setup_lexer


class LexerTests(unittest.TestCase):

    def test_skip_whitespaces(self):
        text = "            3"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.INT_VALUE)
        self.assertEqual(token.value, 3)

    def test_skip_whitespaces_multiline(self):
        text = """       
          
                    
          4   

        """
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.INT_VALUE)
        self.assertEqual(token.value, 4)

    def test_skip_whitespaces_empty_source(self):
        text = ""
        lexer = setup_lexer(text)
        self.assertEqual(lexer.source.current_char, ETX_VALUE)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.ETX)

    def test_build_token_empty_source(self):
        text = ""
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.ETX)

    def test_build_valid_id(self):
        text = "variable"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.ID)
        self.assertEqual(token.value, text)

    def test_build_id_reserved_keywords(self):
        for keyword, token_type in KEYWORDS.items():
            lexer = setup_lexer(keyword)
            token = lexer.build_next_token()
            self.assertEqual(token.type, token_type)

    @parameterized.expand([
        ("true", TokenType.TRUE_VALUE),
        ("false", TokenType.FALSE_VALUE),
        ("null", TokenType.NULL_VALUE)
    ])
    def test_build_id_reserved_values(self, literal: str, expected_type: TokenType):
        lexer = setup_lexer(literal)
        token = lexer.build_next_token()
        self.assertEqual(token.type, expected_type)

    def test_build_id_characters_not_alpha_or_underscore(self):
        text = "a_b|"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.ID)
        self.assertEqual(token.value, "a_b")
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_id_similar_to_keyword(self):
        text = "constt"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertNotEqual(token.type, TokenType.CONST)
        self.assertEqual(token.type, TokenType.ID)
        self.assertEqual(token.value, "constt")

    def test_build_id_too_long(self):
        text = ''.join(random.choice(letters) for _ in range(Lexer.MAX_IDENTIFIER_LENGTH + 1))
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_int_single_digit(self):
        text = "1"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.INT_VALUE)
        self.assertEqual(token.value, 1)

    def test_build_int_larger(self):
        text = "123124124124"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.INT_VALUE)
        self.assertEqual(token.value, 123124124124)

    def test_build_int_negative(self):
        text = "-1"
        lexer = setup_lexer(text)
        lexer.build_next_token()
        self.assertEqual(lexer.token.type, TokenType.MINUS)

        lexer.build_next_token()
        self.assertEqual(lexer.token.type, TokenType.INT_VALUE)
        self.assertEqual(lexer.token.value, 1)

    def test_build_int_zero(self):
        text = "0"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.INT_VALUE)
        self.assertEqual(token.value, 0)

    def test_build_int_zero_next_char_digit(self):
        text = "01"
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_float_valid(self):
        text = "1.2345678"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.FLOAT_VALUE)
        self.assertEqual(token.value, 1.2345678)

    def test_build_float_negative(self):
        text = "-2.137"
        lexer = setup_lexer(text)

        lexer.build_next_token()
        self.assertEqual(lexer.token.type, TokenType.MINUS)

        lexer.build_next_token()
        self.assertEqual(lexer.token.type, TokenType.FLOAT_VALUE)
        self.assertEqual(lexer.token.value, 2.137)

    def test_build_float_without_leading_digit(self):
        text = ".2"
        lexer = setup_lexer(text)
        self.assertIsNone(lexer._try_build_number())
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_float_starts_with_zero(self):
        text = "0.25"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.FLOAT_VALUE)
        self.assertEqual(token.value, 0.25)

    def test_build_float_nothing_after_dot(self):
        text = "1234."
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_float_scientific_notation(self):
        text = "2.5e3"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.FLOAT_VALUE)
        self.assertEqual(token.value, 2.5e3)

    def test_build_float_scientific_notation_minus_exponent(self):
        text = "1.23e-1"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.FLOAT_VALUE)
        self.assertEqual(token.value, 1.23e-1)

    def test_build_float_scientific_notation_missing_exponent(self):
        text = "1.23eeeeeee"
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_str(self):
        text = "\"wielki test stringa\""
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "wielki test stringa")

    def test_build_str_empty(self):
        text = "\"\""
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "")

    def test_build_str_with_numbers(self):
        text = "\"a1b2c3\""
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "a1b2c3")

    def test_build_str_with_random_characters(self):
        text = "\"!@#$%^&*()_-+=[{]}\\|;:,<.>/?\""
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "!@#$%^&*()_-+=[{]}\\|;:,<.>/?")

    def test_build_str_with_escaping(self):
        content = "\t\\n\\t"
        text = "\"" + content + "\""
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "\t\\n\\t")

    def test_build_str_unescaped_quotes(self):
        text = "\"\"\""
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "")

        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_str_only_backslash(self):
        content = "\\"  # literally "\" in text
        string = "\"" + content + "\""
        lexer = setup_lexer(string)
        # this will fail because `\"` was treated like a `"`
        # and closing quote was not found
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_str_mixed_quotes(self):
        content = "\""
        text = "\'" + content + "\'"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "\"")

    def test_build_str_found_etx(self):
        text = "\""
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_str_too_long(self):
        text = "\"" + ''.join(random.choice(letters) for _ in range(Lexer.MAX_STRING_LENGTH + 1)) + "\""
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_comment(self):
        text = "// hello world!"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.COMMENT)
        self.assertEqual(token.value, " hello world!")

    def test_build_comment_only_one_slash(self):
        text = "/ haha nice try"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.DIV)

    def test_build_comment_three_slashes(self):
        text = "///"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.COMMENT)
        self.assertEqual(token.value, "/")

    def test_build_comment_empty(self):
        text = "//"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.COMMENT)
        self.assertEqual(token.value, "")

    def test_build_multiline_comment(self):
        content = "\nhello"
        text = f"/*{content}*/"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.COMMENT)
        self.assertEqual(token.value, content)

    def test_build_multiline_comment_empty(self):
        text = "/**/"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.COMMENT)
        self.assertEqual(token.value, "")

    def test_build_multiline_comment_not_closed(self):
        text = """/*
        """
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_multiline_comment_improperly_closed(self):
        text = """/*
        * /
        """
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_multiline_comment_nested(self):
        text = """/*
        /**/
        */
        """
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.COMMENT)

    def test_build_multiline_comment_multiple_asterisks(self):
        text = "/*****/"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.COMMENT)
        self.assertEqual(token.value, "***")

    @parameterized.expand([
        ('(', TokenType.LPAREN),
        (')', TokenType.RPAREN),
        ('{', TokenType.LCURLY),
        ('}', TokenType.RCURLY),
        (',', TokenType.COMMA),
        (';', TokenType.SEMI),
        ('+', TokenType.PLUS),
        ('-', TokenType.MINUS),
        ('*', TokenType.MUL),
        ('/', TokenType.DIV),
        ('%', TokenType.MODULO),
        ('=', TokenType.ASSIGN),
        ('>', TokenType.GT),
        ('<', TokenType.LT),
        (':', TokenType.TYPE_ASSIGN)
    ])
    def test_build_token_single_char(self, literal: str, expected_type: TokenType):
        lexer = setup_lexer(literal)
        token = lexer.build_next_token()
        self.assertEqual(token.type, expected_type)

    @parameterized.expand([
        ('==', TokenType.EQ),
        ('!=', TokenType.NEQ),
        ('>=', TokenType.GTE),
        ('<=', TokenType.LTE),
        ('=>', TokenType.ARROW),
        ('??', TokenType.NULL_COALESCE),
        ('?:', TokenType.TYPE_ASSIGN_NULLABLE)
    ])
    def test_build_token_two_characters(self, literal: str, expected_type: TokenType):
        lexer = setup_lexer(literal)
        token = lexer.build_next_token()
        self.assertEqual(token.type, expected_type)

    def test_build_similar_operators_next_to_each_other(self):
        text = "==="
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.EQ)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.ASSIGN)

    def test_build_similar_operators_next_to_each_other_2(self):
        text = "=>="
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertNotEqual(token.type, TokenType.ASSIGN)
        self.assertEqual(token.type, TokenType.ARROW)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.ASSIGN)

    def test_build_similar_operators_next_to_each_other_3(self):
        text = "?:??:"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.TYPE_ASSIGN_NULLABLE)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.NULL_COALESCE)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.TYPE_ASSIGN)

    def test_build_similar_operators_next_to_each_other_4(self):
        text = "???"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.NULL_COALESCE)
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_unknown_operator(self):
        text = "!!"
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.build_next_token()

        text2 = "?"
        lexer2 = setup_lexer(text2)
        with self.assertRaises(LexerError):
            lexer2.build_next_token()


if __name__ == '__main__':
    unittest.main()
