import argparse
import os
from pathlib import Path

from src.interpreter.interpreter import Interpreter
from src.lexer.lexer import LexerSkippingComments
from src.parser.parser import Parser
from src.source import FileSource


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-f", "--file", required=True, help="path to file to interpret")
    args = arg_parser.parse_args()

    if os.path.exists(args.file):
        source = FileSource(file_name=Path(args.file))
        lexer = LexerSkippingComments(source=source)
        parser = Parser(lexer=lexer)
        # program = parser.parse_program()
        # print(program.objects)
        interpreter = Interpreter(parser=parser)
        interpreter.interpret()


if __name__ == '__main__':
    main()
