from enum import Enum


class TokenType(str, Enum):
    ID = "ID"
    # types
    INT = "int"
    FLOAT = "float"
    STR = "str"
    BOOL = "bool"
    FUNC = "func"
    VOID = "void"  # function return
    # variable declaration
    CONST = "const"
    LET = "let"
    # reserved keywords
    IF = "if"
    ELIF = "elif"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"
    DEF = "def"
    # reserved characters
    LPAREN = "("
    RPAREN = ")"
    LCURLY = "{"
    RCURLY = "}"
    COMMA = ","
    SEMI = ";"
    # arithmetic operators
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    MODULO = "%"
    # comparison operators
    EQ = "=="
    NEQ = "!="
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    # logical operators
    AND = "and"
    OR = "or"
    NOT = "not"
    # other operators
    ASSIGN = "="
    ARROW = "=>"
    TYPE_ASSIGN = ":"
    TYPE_ASSIGN_NULLABLE = "?:"
    NULL_COALESCE = "??"
    # VALUES
    INT_VALUE = "INT_VALUE"
    FLOAT_VALUE = "FLOAT_VALUE"
    STR_VALUE = "STR_VALUE"
    BOOL_VALUE = "BOOL_VALUE"
    NULL_VALUE = "NULL_VALUE"
    COMMENT = "COMMENT"
    # End Of Text
    ETX = "\x03"


RESERVED_KEYWORDS = {
    # variable declaration
    TokenType.CONST: "const",
    TokenType.LET: "let",
    # typing
    TokenType.INT: "int",
    TokenType.FLOAT: "float",
    TokenType.STR: "str",
    TokenType.BOOL: "bool",
    # functions related (typing, definition, return)
    TokenType.FUNC: "func",
    TokenType.VOID: "void",
    TokenType.DEF: "def",
    TokenType.RETURN: "return",
    # conditional statements and loop
    TokenType.IF: "if",
    TokenType.ELIF: "elif",
    TokenType.ELSE: "else",
    TokenType.WHILE: "while",
    # logical operators
    TokenType.AND: "and",
    TokenType.OR: "or",
    TokenType.NOT: "not",
}
