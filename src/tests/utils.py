from src.lexer.lexer import Lexer
from src.lexer.lexer import LexerSkippingComments
from src.parser import Parser
from src.source import StringSource


def setup_lexer(text: str) -> Lexer:
    source = StringSource(string=text)
    lexer = Lexer(source=source)
    return lexer


def setup_parser(text: str) -> Parser:
    source = StringSource(string=text)
    lexer = LexerSkippingComments(source=source)
    parser = Parser(lexer=lexer)
    return parser
