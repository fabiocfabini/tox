import sys

from ply import yacc

from tox.lexing._lexer import *
from tox import Scope, MetaData
from tox.utils.errors import syntax_error
from tox import (
    Primary,
    Unary,
    Factor,
    Term,
    Comparison,
    Condition,
    SubExpression,
    Expression
)
from tox import (
    Print,
    Assignment,
    Declaration,
    DeclarationAssignment,
    If,
    Loop,
    BreakContinue
)


def p_prog(p):
    """
    prog : global_declarations stmts
    """
    p[0] = "start\n"
    p[0] += p[2]
    p[0] += f"POP {parser.global_count}\n"
    p[0] += "stop\n"
    parser.global_count = 0
    parser.loop_count = 0
    parser.if_count = 0

def p_global_declarations(p):
    """
    global_declarations :
    """

def p_stmts(p):
    """
    stmts : stmt stmts
    """
    p[0] = p[1] + p[2]
def p_stmts_empty(p):
    """
    stmts :
    """
    p[0] = ""
def p_stmt(p):
    """
    stmt : print
        | declaration_assignment
        | assignment
        | declaration
        | if
        | while
        | for
        | do_while
        | break
        | continue
    """
    p[0] = p[1]

######################
##    SCOPE STMT    ##
######################

def p_start_scope(p):
    """
    ss :
    """
    p.parser.current_scope = Scope(
        f"SCOPE_START_{p.parser.current_scope.level + 1}", 
        p.parser.current_scope.level + 1, 
        p.parser.current_scope
    )
def p_end_scope(p):
    """
    es :
    """
    p.parser.global_count -= p.parser.current_scope.num_alloced()
    p[0] = f"POP {p.parser.current_scope.num_alloced()}\n"
    p.parser.current_scope = p.parser.current_scope.parent

######################
##    BREAK STMT    ##
######################

def p_break(p):
    """
    break : BREAK
    """
    p[0] = parser.loop_break_handler.handle(p, "break")
def p_continue(p):
    """
    continue : CONTINUE
    """
    p[0] = parser.loop_break_handler.handle(p, "continue")

######################
##    LOOPS STMT    ##
######################

def p_for(p):
    """
    for : FOR ss '(' for_inits ';' expression ';' for_updates ')' ss '{' stmts  '}' es es
    """
    p[0] = parser.loop_handler.handle(p, "for")
def p_for_inits(p):
    """
    for_inits : for_inits ',' for_init
            | for_init
    """
    p[0] = parser.loop_handler.handle(p, "for_inits")
def p_for_init(p):
    """
    for_init : declaration_assignment
            | declaration
            | assignment
            |
    """
    p[0] = parser.loop_handler.handle(p, "for_init")
def p_for_updates(p):
    """
    for_updates : for_updates ',' for_update
            | for_update
    """
    p[0] = parser.loop_handler.handle(p, "for_updates")
def p_for_update(p):
    """
    for_update : assignment
    """
    p[0] = parser.loop_handler.handle(p, "for_update")

def p_do_while(p):
    """
    do_while : DO ss '{' stmts '}' es WHILE '(' expression ')'
    """
    p[0] = parser.loop_handler.handle(p, "do_while")

def p_while(p):
    """
    while : WHILE expression ss '{' stmts '}' es
    """
    p[0] = parser.loop_handler.handle(p, "while")

def p_if(p):
    """
    if : IF expression ss '{' stmts '}' es
    """
    p[0] = parser.if_handler.handle(p, "if")
def p_if_else(p):
    """
    if : IF expression ss '{' stmts '}' es ELSE ss '{' stmts '}' es
    """
    p[0] = parser.if_handler.handle(p, "if_else")

######################
##    INIT STMT     ##
######################

def p_variable_init(p):
    """
    declaration_assignment : ID ':' type ASSIGN expression
    """
    p[0] = parser.declaration_assignment_handler.handle(p, "variable_init")
def p_array_literal_init(p):
    """
    declaration_assignment : ID ':' Vtype ASSIGN '[' arrayitems ']'
    """
    p[0] = parser.declaration_assignment_handler.handle(p, "array_literal_init")
def p_array_range_init(p):
    """
    declaration_assignment : ID ':' Vtype ASSIGN '[' INT RETI INT ']'
    """
    p[0] = parser.declaration_assignment_handler.handle(p, "array_range_init")
def p_array_items(p):
    """
    arrayitems : arrayitems ',' expression
        | expression
    """
    p[0] = parser.declaration_assignment_handler.handle(p, "array_items")

######################
##   DECLARE STMT   ##
######################

def p_variable_declaration(p):
    """
    declaration : ID ':' type
    """
    p[0] = p.parser.declaration_handler.handle(p, "variable_declaration")
def p_array_declaration(p):
    """
    declaration : ID ':' Vtype '[' INT ']'
    """
    p[0] = p.parser.declaration_handler.handle(p, "array_declaration")

######################
##   ASSIGN STMT    ##
######################

def p_assignment_array_indexing(p):
    """
    assignment : ID '[' expression ']' ASSIGN expression
    """
    p[0] = parser.assignment_handler.handle(p, "array_indexing")
def p_assignment_expression(p):
    """
    assignment : ID ASSIGN expression
    """
    p[0] = parser.assignment_handler.handle(p, "expression")

######################
##    PRINT STMT    ##
######################

def p_print(p):
    """
    print : PRINT '(' multiple_prints ')'
    """
    p[0] = parser.print_handler.handle(p, "print")
def p_print_expressions(p):
    """
    multiple_prints : multiple_prints ',' expression
    """
    p[0] = parser.print_handler.handle(p, "expressions")
def p_print_strings(p):
    """
    multiple_prints : multiple_prints ',' STRING
    """
    p[0] = parser.print_handler.handle(p, "strings")
def p_print_string(p):
    """
    multiple_prints : STRING
    """
    p[0] = parser.print_handler.handle(p, "string")
def p_print_expression(p):
    """
    multiple_prints : expression
    """
    p[0] = parser.print_handler.handle(p, "expression")
def p_print_empty(p):
    """
    multiple_prints : 
    """
    p[0] = parser.print_handler.handle(p, "empty")

######################
## TYPES INITAL IMP ##
######################

def p_type(p):
    """
    type : TYPE_INT
    """
    p[0] = p[1]
def p_vtype(p):
    """
    Vtype : '&' TYPE_INT
    """
    p[0] = p[1] + p[2]

######################
## EXPRESSION RULES ##
######################

def p_expression_or(p):
    """
    expression : expression OR subexpression
    """
    p[0] = parser.expression_handler.handle(p, "or")
def p_expression_subexpression(p):
    """
    expression : subexpression
    """
    p[0] = parser.expression_handler.handle(p, "subexpression")

def p_subexpression_and(p):
    """
    subexpression : condition AND subexpression
    """
    p[0] = parser.subexpression_handler.handle(p, "and")
def p_subexpression_condition(p):
    """
    subexpression : condition
    """
    p[0] = parser.subexpression_handler.handle(p, "condition")

def p_condition_eq(p):
    """
    condition : comparison EQ condition
    """
    p[0] = parser.condition_handler.handle(p, "eq")
def p_condition_neq(p):
    """
    condition : comparison NEQ condition
    """
    p[0] = parser.condition_handler.handle(p, "neq")
def p_condition_comparison(p):
    """
    condition : comparison
    """
    p[0] = parser.condition_handler.handle(p, "comparison")

def p_comparison_lt(p):
    """
    comparison : term LT comparison
    """
    p[0] = parser.comparison_handler.handle(p, "lt")
def p_comparison_gt(p):
    """
    comparison : term GT comparison
    """
    p[0] = parser.comparison_handler.handle(p, "gt")
def p_comparison_lte(p):
    """
    comparison : term LTE comparison
    """
    p[0] = parser.comparison_handler.handle(p, "lte")
def p_comparison_gte(p):
    """
    comparison : term GTE comparison
    """
    p[0] = parser.comparison_handler.handle(p, "gte")
def p_comparison_term(p):
    """
    comparison : term
    """
    p[0] = parser.comparison_handler.handle(p, "term")

def p_term_sub(p):
    """
    term : factor '-' term
    """
    p[0] = parser.term_handler.handle(p, "sub")
def p_term_add(p):
    """
    term : factor '+' term
    """
    p[0] = parser.term_handler.handle(p, "add")
def p_term_factor(p):
    """
    term : factor
    """
    p[0] = parser.term_handler.handle(p, "factor")

def p_factor_mul(p):
    """
    factor : unary '*' factor
    """
    p[0] = parser.factor_handler.handle(p, "mul")
def p_factor_div(p):
    """
    factor : unary '/' factor
    """
    p[0] = parser.factor_handler.handle(p, "div")
def p_factor_mod(p):
    """
    factor : unary '%' factor
    """
    p[0] = parser.factor_handler.handle(p, "mod")
def p_factor_unary(p):
    """
    factor : unary
    """
    p[0] = parser.factor_handler.handle(p, "unary")

def p_unary_not(p):
    """
    unary : '!' unary
    """
    p[0] = parser.unary_handler.handle(p, "not")
def p_unary_neg(p):
    """
    unary : '-' unary
    """
    p[0] = parser.unary_handler.handle(p, "neg")
def p_unary_primary(p):
    """
    unary : primary
    """
    p[0] = parser.unary_handler.handle(p, "primary")

def p_primary_indexing(p):
    """
    primary : ID '[' expression ']'
    """
    p[0] = parser.primary_handler.handle(p, "indexing")
def p_primary_int(p):
    """
    primary : INT
    """
    p[0] = parser.primary_handler.handle(p, "int")
def p_primary_id(p):
    """
    primary : ID
    """
    p[0] = parser.primary_handler.handle(p, "id")
def p_primary_true(p):
    """
    primary : TRUE
    """
    p[0] = parser.primary_handler.handle(p, "true")
def p_primary_false(p):
    """
    primary : FALSE
    """
    p[0] = parser.primary_handler.handle(p, "false")
def p_primary_new(p):
    """
    primary : '(' expression ')'
    """
    p[0] = parser.primary_handler.handle(p, "new")

def p_error(p):
    syntax_error(p, f"Invalid syntax '{p.value}'")

parser = yacc.yacc()

parser.primary_handler = Primary()
parser.unary_handler = Unary()
parser.factor_handler = Factor()
parser.term_handler = Term()
parser.comparison_handler = Comparison()
parser.condition_handler = Condition()
parser.subexpression_handler = SubExpression()
parser.expression_handler = Expression()

parser.print_handler = Print()
parser.assignment_handler = Assignment()
parser.declaration_handler = Declaration()
parser.declaration_assignment_handler = DeclarationAssignment()
parser.if_handler = If()
parser.loop_handler = Loop()
parser.loop_break_handler = BreakContinue()

parser.current_scope: Scope = Scope(name="Global Scope", level=0, parent=None) 
parser.global_count = 0
parser.if_count = 0
parser.loop_count = 0
parser.array_assign_items = 0

if __name__ == "__main__":
    for line in sys.stdin:
        parser.parse(line)