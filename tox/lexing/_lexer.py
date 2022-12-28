import sys

from ply import lex

from tox import find_column, lex_error

arithmetics_literals = "[]()+-/*%^!{}&"     # Literals for arithmetics
general_literals = ",:;"                    # Literals for general use

literals = arithmetics_literals + general_literals

type_tokens = ['integer', 'filum', 'FLOAT']                                            # filum so far only works in literals
op_tokens = ["ASSIGN", "LTE", "LT", 'EQ', "NEQ", "GT", "GTE", "RETI", 'AND', 'OR']  # Operators
special_tokens = ['NEWLINE', 'COMMENT', 'MULTICOMMENTS', 'ID', 'RARROW']            # Special tokens
reserved = {                                                                        # Reserved words
    'print' : 'PRINT',
    'readi' : 'READ_INT',
    'readf' : 'READ_FLOAT',
    'reads' : 'READ_STRING',
    'integer'   : 'TYPE_INT',
    'filum': 'TYPE_STRING',
    'float' : 'TYPE_FLOAT',
    'vec'   : 'TYPE_VEC',
    'si'    : 'IF',
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

t_RARROW = r"->"        # '->' for function declaration
t_EQ = r"=="            # Double equal
t_RETI = r"\.\.\."      # '...' for ranged array declaration
t_GTE = r">="           # Greater than or equal
t_LTE = r"<="           # Less than or equal
t_NEQ = r"!="           # Not equal
t_ASSIGN = r"="         # Assign
t_LT = r"<"             # Less than
t_GT = r">"             # Greater than

@lex.TOKEN(r'\d+f | \d+\.\d+(f)?') # Float
def t_FLOAT(t):
    if t.value[-1] == 'f':
        t.value = t.value[:-1]
    if '.' not in t.value:
        t.value += '.0'
    return t

@lex.TOKEN(r'\d+')      # integer
def t_integer(t):
    return t

@lex.TOKEN(r'\|\|')     # OR
def t_OR(t):
    return t

@lex.TOKEN(r'&&')       # AND
def t_AND(t):
    return t

@lex.TOKEN(r"print")    # Print
def t_PRINT(t):
    return t

@lex.TOKEN(r'\"[^"]*\"')    # filum
def t_filum(t):
    return t

@lex.TOKEN(r'[a-zA-Z_][a-zA-Z0-9_]*')       # ID
def t_ID(t):
    t.type = reserved.get(t.value, 'ID')    # Check for reserved words
    return t

@lex.TOKEN(r"//.*")    # Comment
def t_COMMENT(t):
    pass

@lex.TOKEN(r"/\*(.|\n)*?\*/")   # Multiline comment
def t_MULTICOMMENTS(t):
    t.lexer.lineno += t.value.count('\n')

@lex.TOKEN(r'\n+')    # Newline
def t_NEWLINE(t):
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'    # Ignore spaces and tabs

def t_error(t):    # Error handling
    lex_error(t, "Illegal character '%s'" % t.value[0])
    sys.exit(1)

lexer = lex.lex()

if __name__ == "__main__":
    lexer.input("""func main() {
    f: integer = 1

    print("OK\n")
}""")
    while True:
        tok = lexer.token()
        if tok:
            print(tok)
        else:
            break