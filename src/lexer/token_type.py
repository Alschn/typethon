from enum import Enum, auto

ETX_VALUE = "\x03"


class TokenType(Enum):
    ID = auto()
    # types
    INT = auto()
    FLOAT = auto()
    STR = auto()
    BOOL = auto()
    FUNC = auto()
    VOID = auto()
    # variable declaration
    CONST = auto()
    LET = auto()
    # reserved keywords
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    WHILE = auto()
    RETURN = auto()
    DEF = auto()
    # reserved characters
    LPAREN = auto()
    RPAREN = auto()
    LCURLY = auto()
    RCURLY = auto()
    COMMA = auto()
    SEMI = auto()
    # arithmetic operators
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    MODULO = auto()
    # comparison operators
    EQ = auto()
    NEQ = auto()
    GT = auto()
    LT = auto()
    GTE = auto()
    LTE = auto()
    # logical operators
    AND = auto()
    OR = auto()
    NOT = auto()
    # other operators
    ASSIGN = auto()
    ARROW = auto()
    NULL_COALESCE = auto()
    # type assignment
    TYPE_ASSIGN = auto()
    TYPE_ASSIGN_NULLABLE = auto()
    # VALUES
    INT_VALUE = auto()
    FLOAT_VALUE = auto()
    STR_VALUE = auto()
    # reserved values
    NULL_VALUE = auto()
    TRUE_VALUE = auto()
    FALSE_VALUE = auto()
    # comment
    COMMENT = auto()
    # End Of Text
    ETX = auto()


KEYWORDS = {
    "const": TokenType.CONST,
    "let": TokenType.LET,
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "str": TokenType.STR,
    "bool": TokenType.BOOL,
    "func": TokenType.FUNC,
    "void": TokenType.VOID,
    "def": TokenType.DEF,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "null": TokenType.NULL_VALUE,
    "true": TokenType.TRUE_VALUE,
    "false": TokenType.FALSE_VALUE
}

ONE_CHAR_OPS = {
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LCURLY,
    "}": TokenType.RCURLY,
    ",": TokenType.COMMA,
    ";": TokenType.SEMI,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MUL,
    "/": TokenType.DIV,
    "%": TokenType.MODULO,
    "=": TokenType.ASSIGN,
    ">": TokenType.GT,
    "<": TokenType.LT,
    ":": TokenType.TYPE_ASSIGN
}

TWO_CHAR_OPS = {
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
    ">=": TokenType.GTE,
    "<=": TokenType.LTE,
    "=>": TokenType.ARROW,
    "??": TokenType.NULL_COALESCE,
    "?:": TokenType.TYPE_ASSIGN_NULLABLE
}
