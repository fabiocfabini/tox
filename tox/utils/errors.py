from typing import List

import sys

import tox

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
    try:
        last_cr = input.rfind('\n', 0, token.lexpos(n)) + 1
        return (token.lexpos(n) - last_cr) + 1
    except Exception:
        return -1

def lex_error(p, msg: str):
    """
    Report a lex error.
    """
    sys.stderr.write(f"{tox.COLOR_RED}Lex Error:{tox.COLOR_YELLOW}{p.lineno}:{tox.COLOR_GREEN}{find_column(p.lexer.lexdata, p)}:{tox.RESET_COLOR} {msg}\n")

def syntax_error(p, msg: str):
    """
    Report a syntax error.
    """
    sys.stderr.write(f"{tox.COLOR_RED}Syntax Error:{tox.COLOR_YELLOW}{p.lineno}:{tox.COLOR_GREEN}{find_column(p.lexer.lexdata, p)}:{tox.RESET_COLOR} {msg}\n")

def compiler_error(p, n: int, msg: str):
    """
    Report a compiler error.
    """
    sys.stderr.write(f"{tox.COLOR_RED}Compiler Error:{tox.COLOR_YELLOW}{p.lineno(n)}:{tox.COLOR_GREEN}{find_column_comp(p.parser.input, p, n)}:{tox.RESET_COLOR} {msg}\n")

def compiler_warning(p, n: int, msg: str):
    """
    Report a compiler warning.
    """
    try:
        line = p.lineno(n)
    except IndexError:
        line = n
    sys.stderr.write(f"{tox.COLOR_YELLOW}Compiler Warning:{tox.COLOR_YELLOW}{n}:{tox.COLOR_GREEN}{find_column_comp(p.parser.input, p, n)}:{tox.RESET_COLOR} {msg}\n")

def compiler_note(msg):
    """
    Report a compiler note.
    """
    sys.stderr.write(f"{tox.COLOR_BLUE}Compiler Note:{tox.RESET_COLOR} {msg}\n")

def std_message(msg: List[str]):
    """
    Helper function to print an operation message.
    """
    return "\n".join(msg) + "\n"