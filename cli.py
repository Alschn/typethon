import argparse
import os
from pathlib import Path

from src.lexer import Lexer
from src.source import FileSource


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, help="path to file to interpret")
    args = parser.parse_args()

    # temporarily
    if os.path.exists(args.file):
        source = FileSource(file_name=Path(args.file))
        lexer = Lexer(source=source)

        # while lexer.source.current_char != TokenType.ETX:
        #     lexer.build_next_token()


if __name__ == '__main__':
    main()
