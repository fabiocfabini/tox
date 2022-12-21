from typing import List

import sys

import tox

def find_column(input, token):
    last_cr = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - last_cr) + 1

def find_column_comp(input, token, n):
    last_cr = input.rfind('\n', 0, token.lexpos(n)) + 1
    return (token.lexpos(n) - last_cr) + 1

def syntax_error(p, msg: str):
    sys.stderr.write(f"{tox.COLOR_RED}Syntax Error:{tox.COLOR_YELLOW}{p.lineno}:{tox.COLOR_GREEN}{find_column(p.lexer.lexdata, p)}:{tox.RESET_COLOR} {msg}\n")

def compiler_error(p, n: int, msg: str):
    sys.stderr.write(f"{tox.COLOR_RED}Compiler Error:{tox.COLOR_YELLOW}{p.lineno(n)}:{tox.COLOR_GREEN}{find_column_comp(p.parser.input, p, n)}:{tox.RESET_COLOR} {msg}\n")

def compiler_note(msg):
    sys.stderr.write(f"{tox.COLOR_BLUE}Compiler Note:{tox.RESET_COLOR} {msg}\n")

def std_message(msg: List[str]):
    return "\n".join(msg) + "\n"