import sys

from ply import lex

COLOR_RED = "\033[1;31m"
RESET_COLOR = "\033[0;0m"

arithmetics_literals = "[]()+-/*%^!{}&"
general_literals = ",:;"

literals = arithmetics_literals + general_literals

type_tokens = ['INT', 'STRING', 'TRUE', 'FALSE']
op_tokens = ["ASSIGN", "LTE", "LT", 'EQ', "NEQ", "GT", "GTE", "RETI"]
special_tokens = ['NEWLINE', 'COMMENT', 'MULTICOMMENTS', 'ID', 'AND', 'OR']
reserved = {
    'print' : 'PRINT',
    'int'   : 'TYPE_INT',
    'if'    : 'IF',
    'else'  : 'ELSE',
    'while' : 'WHILE',
    'for'   : 'FOR',
    'do'    : 'DO',
    'break' : 'BREAK',
    'continue' : 'CONTINUE',
    'func' : 'FUNCTION',
    'return' : 'RETURN'
}

tokens = type_tokens + special_tokens + list(reserved.values()) + op_tokens

def find_column(input, token):
    last_cr = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - last_cr) + 1

t_EQ = r"=="
t_RETI = r"\.\.\."
t_GTE = r">="
t_LTE = r"<="
t_NEQ = r"!="
t_ASSIGN = r"="
t_LT = r"<"
t_GT = r">"

@lex.TOKEN(r'\d+')
def t_INT(t):
    return t

@lex.TOKEN(r'\|\|')
def t_OR(t):
    return t

@lex.TOKEN(r'&&')
def t_AND(t):
    return t

@lex.TOKEN(r"print")
def t_PRINT(t):
    return t

@lex.TOKEN(r"False")
def t_FALSE(t):
    return t

@lex.TOKEN(r"True")
def t_TRUE(t):
    return t

@lex.TOKEN(r'\"[^"]*\"')
def t_STRING(t):
    return t

@lex.TOKEN(r'[a-zA-Z_][a-zA-Z0-9_]*')
def t_ID(t):
    t.type = reserved.get(t.value, 'ID')
    return t

@lex.TOKEN(r"//.*")
def t_COMMENT(t):
    pass

@lex.TOKEN(r"/\*(.|\n)*?\*/")
def t_MULTICOMMENTS(t):
    t.lexer.lineno += t.value.count('\n')

@lex.TOKEN(r'\n+')
def t_NEWLINE(t):
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    sys.stderr.write(f"{COLOR_RED}LexError:{RESET_COLOR}{t.lineno}:{find_column(t.lexer.lexdata, t)}: Illegal character {t.value[0]}\n")
    sys.exit(1)

lexer = lex.lex()

if __name__ == "__main__":
    lexer.input("&||&&&&...")
    while True:
        tok = lexer.token()
        if tok:
            print(tok)
        else:
            break

"""
LexToken(LESSEQ,'<=',1,0)
LexToken(LESS,'<',1,3)
LexToken(EQ,'==',1,5)
LexToken(DIF,'!=',1,8)
LexToken(GRT,'>',1,11)
LexToken(GRTEQ,'>=',1,13)
LexToken(INV,'-',1,16)
LexToken(NOT,'!',1,18)
"""