from typing import List

import sys

import lat

def find_column(input, token):
    """
    Compute the column of a given token.
    """
    last_cr = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - last_cr) + 1

def find_column_comp(input, token, n):
    """
    Compute the column of a given token.
    """
    last_cr = input.rfind('\n', 0, token.lexpos(n)) + 1
    return (token.lexpos(n) - last_cr) + 1

def lex_error(p, msg: str):
    """
    Report a lex error.
    """
    sys.stderr.write(f"{lat.COLOR_RED}Lex Error:{lat.COLOR_YELLOW}{p.lineno}:{lat.COLOR_GREEN}{find_column(p.lexer.lexdata, p)}:{lat.RESET_COLOR} {msg}\n")

def syntax_error(p, msg: str):
    """
    Report a syntax error.
    """
    sys.stderr.write(f"{lat.COLOR_RED}Syntax Error:{lat.COLOR_YELLOW}{p.lineno}:{lat.COLOR_GREEN}{find_column(p.lexer.lexdata, p)}:{lat.RESET_COLOR} {msg}\n")

def compiler_error(p, n: int, msg: str):
    """
    Report a compiler error.
    """
    sys.stderr.write(f"{lat.COLOR_RED}Compiler Error:{lat.COLOR_YELLOW}{p.lineno(n)}:{lat.COLOR_GREEN}{find_column_comp(p.parser.input, p, n)}:{lat.RESET_COLOR} {msg}\n")

def compiler_warning(p, n: int, msg: str):
    """
    Report a compiler warning.
    """
    sys.stderr.write(f"{lat.COLOR_YELLOW}Compiler Warning:{lat.COLOR_YELLOW}{p.lineno(n)}:{lat.COLOR_GREEN}{find_column_comp(p.parser.input, p, n)}:{lat.RESET_COLOR} {msg}\n")

def compiler_note(msg):
    """
    Report a compiler note.
    """
    sys.stderr.write(f"{lat.COLOR_BLUE}Compiler Note:{lat.RESET_COLOR} {msg}\n")

def std_message(msg: List[str]):
    """
    Helper function to print an operation message.
    """
    return "\n".join(msg) + "\n"