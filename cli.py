import argparse
import os
from pathlib import Path

from src.lexer import Lexer
from src.lexer.token_type import TokenType, ETX_VALUE
from src.source import FileSource


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, help="path to file to interpret")
    args = parser.parse_args()

    # temporarily
    if os.path.exists(args.file):
        source = FileSource(file_name=Path(args.file))
        lexer = Lexer(source=source)

        while lexer.source.current_char != ETX_VALUE:
            token = lexer.build_next_token()
            print(token)


if __name__ == '__main__':
    main()
