import random
import unittest
from string import ascii_lowercase as letters

from src.errors.error import LexerError
from src.lexer import Lexer
from src.lexer.token_type import TokenType, RESERVED_KEYWORDS
from src.source import StringSource


def setup_lexer(text: str) -> Lexer:
    source = StringSource(string=text)
    lexer = Lexer(source=source)
    return lexer


class LexerTests(unittest.TestCase):

    def test_skip_whitespaces(self):
        text = "            3"
        lexer = setup_lexer(text)
        lexer.skip_whitespace()
        self.assertEqual(lexer.source.current_char, "3")

    def test_skip_whitespaces_multiline(self):
        text = """       
          4   

        """
        lexer = setup_lexer(text)
        lexer.skip_whitespace()
        self.assertEqual(lexer.source.current_char, "4")

    def test_skip_whitespaces_empty_source(self):
        text = ""
        lexer = setup_lexer(text)
        self.assertEqual(lexer.source.current_char, TokenType.ETX)

    def test_build_token_empty_source(self):
        text = ""
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.ETX)
        self.assertEqual(token.value, "\x03")

    def test_build_valid_id(self):
        text = "variable"
        lexer = setup_lexer(text)
        token = lexer.try_build_identifier()
        self.assertEqual(token.type, TokenType.ID)
        self.assertEqual(token.value, text)

    def test_build_id_reserved_keywords(self):
        # const, let, int, float, str, bool, func, void,
        # def, return, if, elif, else, or, and, not
        keywords = RESERVED_KEYWORDS.keys()
        for keyword in keywords:
            lexer = setup_lexer(keyword)
            token = lexer.try_build_identifier()
            self.assertEqual(token.type, keyword)
            self.assertEqual(token.value, keyword)

    def test_build_id_characters_not_alpha_or_underscore(self):
        text = "a_b|"
        lexer = setup_lexer(text)
        token = lexer.try_build_identifier()
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
            lexer.try_build_identifier()

    def test_build_reserved_values(self):
        text = "true false null"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.BOOL_VALUE)
        self.assertEqual(token.value, True)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.BOOL_VALUE)
        self.assertEqual(token.value, False)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.NULL_VALUE)
        self.assertEqual(token.value, None)

    def test_build_int_single_digit(self):
        text = "1"
        lexer = setup_lexer(text)
        token = lexer.try_build_number()
        self.assertEqual(token.type, TokenType.INT_VALUE)
        self.assertEqual(token.value, 1)

    def test_build_int_larger(self):
        text = "123124124124"
        lexer = setup_lexer(text)
        token = lexer.try_build_number()
        self.assertEqual(token.type, TokenType.INT_VALUE)
        self.assertEqual(token.value, 123124124124)

    def test_build_int_negative(self):
        text = "-1"
        lexer = setup_lexer(text)

        lexer.build_next_token()
        self.assertEqual(lexer.token.type, TokenType.MINUS)
        self.assertEqual(lexer.token.value, "-")

        lexer.build_next_token()
        self.assertEqual(lexer.token.type, TokenType.INT_VALUE)
        self.assertEqual(lexer.token.value, 1)

    def test_build_int_zero(self):
        text = "0"
        lexer = setup_lexer(text)
        token = lexer.try_build_number()
        self.assertEqual(token.type, TokenType.INT_VALUE)
        self.assertEqual(token.value, 0)

    def test_build_int_zero_next_char_digit(self):
        text = "01"
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.try_build_number()

    def test_build_float_valid(self):
        text = "1.2345678"
        lexer = setup_lexer(text)
        token = lexer.try_build_number()
        self.assertEqual(token.type, TokenType.FLOAT_VALUE)
        self.assertEqual(token.value, 1.2345678)

    def test_build_float_negative(self):
        text = "-2.137"
        lexer = setup_lexer(text)

        lexer.build_next_token()
        self.assertEqual(lexer.token.type, TokenType.MINUS)
        self.assertEqual(lexer.token.value, "-")

        lexer.build_next_token()
        self.assertEqual(lexer.token.type, TokenType.FLOAT_VALUE)
        self.assertEqual(lexer.token.value, 2.137)

    def test_build_float_without_leading_digit(self):
        text = ".2"
        lexer = setup_lexer(text)
        self.assertIsNone(lexer.try_build_number())
        with self.assertRaises(LexerError):
            lexer.build_next_token()

    def test_build_float_starts_with_zero(self):
        text = "0.25"
        lexer = setup_lexer(text)
        token = lexer.try_build_number()
        self.assertEqual(token.type, TokenType.FLOAT_VALUE)
        self.assertEqual(token.value, 0.25)

    def test_build_float_scientific_notation(self):
        text = "2.5e3"
        lexer = setup_lexer(text)
        token = lexer.try_build_number()
        self.assertEqual(token.type, TokenType.FLOAT_VALUE)
        self.assertEqual(token.value, 2.5e3)

    def test_build_float_scientific_notation_minus_exponent(self):
        text = "1.23e-1"
        lexer = setup_lexer(text)
        token = lexer.try_build_number()
        self.assertEqual(token.type, TokenType.FLOAT_VALUE)
        self.assertEqual(token.value, 1.23e-1)

    def test_build_float_scientific_notation_missing_exponent(self):
        text = "1.23eeeeeee"
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.try_build_number()

    def test_build_str(self):
        text = "\"wielki test stringa\""
        lexer = setup_lexer(text)
        token = lexer.try_build_string()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "wielki test stringa")

    def test_build_str_empty(self):
        text = "\"\""
        lexer = setup_lexer(text)
        token = lexer.try_build_string()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "")

    def test_build_str_with_numbers(self):
        text = "\"a1b2c3\""
        lexer = setup_lexer(text)
        token = lexer.try_build_string()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "a1b2c3")

    def test_build_str_with_random_characters(self):
        text = "\"!@#$%^&*()_-+=[{]}\\|;:,<.>/?\""
        lexer = setup_lexer(text)
        token = lexer.try_build_string()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "!@#$%^&*()_-+=[{]}\\|;:,<.>/?")

    def test_build_str_with_escaping(self):
        content = "\t\\n\\t"
        text = "\"" + content + "\""
        lexer = setup_lexer(text)
        token = lexer.try_build_string()
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
        token = lexer.try_build_string()
        self.assertEqual(token.type, TokenType.STR_VALUE)
        self.assertEqual(token.value, "\"")

    def test_build_str_found_etx(self):
        text = "\""
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.try_build_string()

    def test_build_str_too_long(self):
        text = "\"" + ''.join(random.choice(letters) for _ in range(Lexer.MAX_STRING_LENGTH + 1)) + "\""
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.try_build_string()

    def test_build_comment(self):
        text = "// hello world!"
        lexer = setup_lexer(text)
        token = lexer.try_build_comment()
        self.assertEqual(token.type, TokenType.COMMENT)
        self.assertEqual(token.value, " hello world!")

    def test_build_comment_only_one_slash(self):
        text = "/ haha nice try"
        lexer = setup_lexer(text)
        token = lexer.try_build_comment()
        self.assertEqual(token.type, TokenType.DIV)

    def test_build_comment_three_slashes(self):
        text = "///"
        lexer = setup_lexer(text)
        token = lexer.try_build_comment()
        self.assertEqual(token.type, TokenType.COMMENT)
        self.assertEqual(token.value, "/")

    def test_build_comment_empty(self):
        text = "//"
        lexer = setup_lexer(text)
        token = lexer.try_build_comment()
        self.assertEqual(token.type, TokenType.COMMENT)
        self.assertEqual(token.value, "")

    def test_build_too_long_comment(self):
        text = "//" + ''.join(random.choice(letters) for _ in range(Lexer.MAX_COMMENT_LENGTH + 1))
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.try_build_comment()

    def test_build_multiline_comment(self):
        content = "\nhello"
        text = f"/*{content}*/"
        lexer = setup_lexer(text)
        token = lexer.try_build_comment()
        self.assertEqual(token.type, TokenType.COMMENT)
        self.assertEqual(token.value, content)

    def test_build_multiline_comment_empty(self):
        text = "/**/"
        lexer = setup_lexer(text)
        token = lexer.try_build_comment()
        self.assertEqual(token.type, TokenType.COMMENT)
        self.assertEqual(token.value, "")

    def test_build_multiline_comment_too_long(self):
        text = "/*" + ''.join(random.choice(letters) for _ in range(Lexer.MAX_MULTILINE_COMMENT_LENGTH + 1)) + "*/"
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.try_build_comment()

    def test_build_multiline_comment_not_closed(self):
        text = """/*
        """
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.try_build_comment()

    def test_build_multiline_comment_improperly_closed(self):
        text = """/*

        * /
        """
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.try_build_comment()

    def test_build_multiline_comment_asterisk_inside(self):
        text = """/*
        *
        */
        """
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.try_build_comment()

    def test_build_multiline_comment_nested(self):
        text = """/*
        /**/
        */
        """
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.try_build_comment()

    def test_build_operator_single_char(self):
        text = "+ - / * %"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.PLUS)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.MINUS)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.DIV)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.MUL)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.MODULO)

    def test_build_operator_two_characters(self):
        text = "== != >= <= => ?: ??"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.EQ)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.NEQ)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.GTE)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.LTE)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.ARROW)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.TYPE_ASSIGN_NULLABLE)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.NULL_COALESCE)

    def test_build_reserved_characters(self):
        text = "( ) { } , ;"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.LPAREN)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.RPAREN)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.LCURLY)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.RCURLY)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.COMMA)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.SEMI)

    def test_build_similar_operators_next_to_each_other(self):
        text = "==="
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.EQ)
        self.assertEqual(token.value, TokenType.EQ)

        token = lexer.build_next_token()
        self.assertEqual(token.type, TokenType.ASSIGN)
        self.assertEqual(token.value, TokenType.ASSIGN)

    def test_build_similar_operators_next_to_each_other_2(self):
        text = "=>="
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertNotEqual(token.type, TokenType.ASSIGN)
        self.assertEqual(token.type, TokenType.ARROW)

        token = lexer.build_next_token()
        self.assertEqual(token.value, TokenType.ASSIGN)

    def test_build_similar_operators_next_to_each_other_3(self):
        text = "?:??:"
        lexer = setup_lexer(text)
        token = lexer.build_next_token()
        self.assertEqual(token.value, TokenType.TYPE_ASSIGN_NULLABLE)

        token = lexer.build_next_token()
        self.assertEqual(token.value, TokenType.NULL_COALESCE)

        token = lexer.build_next_token()
        self.assertEqual(token.value, TokenType.TYPE_ASSIGN)

    def test_build_unknown_operator(self):
        text = "!!"
        lexer = setup_lexer(text)
        with self.assertRaises(LexerError):
            lexer.build_next_token()

        text2 = "?a"
        lexer2 = setup_lexer(text2)
        with self.assertRaises(LexerError):
            lexer2.build_next_token()


if __name__ == '__main__':
    unittest.main()
