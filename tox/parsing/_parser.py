import sys

from ply import yacc

from tox.lexing._lexer import *
from tox import Scope, MetaData
from tox import Functions, FunctionData
from tox import TypeCheck
from tox.utils.errors import syntax_error, compiler_error, compiler_note
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
    IO,
    Assignment,
    Declaration,
    DeclarationAssignment,
    If,
    Match,
    Loop,
    BreakContinue
)


def p_prog(p):
    """
    prog : global_declarations functions
    """
    parser.global_count = 0
    parser.loop_count = 0
    parser.if_count = 0
    if not parser.type_checker.is_empty():
        compiler_error(p, 1, f"Leftover types in type checker. {p.parser.type_checker}")
        sys.exit(1)

    if parser.functions_handler.get("main") is None:
        compiler_error(p, 0, "Did not find main function")
        compiler_note("Called from p_prog.")
        sys.exit(1)

    for function, meta in parser.functions_handler.Table.items():
        if meta.init is False:
            compiler_error(p, 0, f"Function '{function}' was declared but not defined")
            sys.exit(1)

    p[0] = p[1]
    p[0] += "start\n"
    p[0] += f"PUSHA main\n"
    p[0] += f"CALL\n"
    p[0] += "stop\n"
    p[0] += p[2]

######################
##   GLOBAL RULES   ##
######################

def p_global_declarations(p):
    """
    global_declarations : global_declaration global_declarations
    """
    p[0] = p[1] + p[2]

def p_global_declarations_empty(p):
    """
    global_declarations :
    """
    p[0] = ""

def p_global_declaration(p):
    """
    global_declaration : declaration_assignment
                    | declaration
    """
    p[0] = p[1]

######################
##   FUNCS RULES    ##
######################

def p_functions(p):
    """
    functions : function functions
    """
    p[0] = p[1] + p[2]

def p_functions_empty(p):
    """
    functions :
    """
    p[0] = ""
def p_function(p):
    """
    function : function_declaration
            | function_definition
    """
    p[0] = p[1]
def p_function_declaration(p):
    """
    function_declaration : function_def
    """
    p[0] = p[1]
def p_function_definition(p):
    """
    function_definition : function_header function_body
    """
    p[0] = p[1] + p[2]
def p_function_def(p):
    """
    function_def : function_id ss '(' params ')' out_type es
    """
    p[0] = parser.functions_handler.handle(p, 'def')
def p_function_header(p):
    """
    function_header : function_id ss '(' params ')' out_type
    """
    p[0] = parser.functions_handler.handle(p, 'header')
def p_function_id(p):
    """
    function_id : FUNCTION ID
    """
    p[0] = parser.functions_handler.handle(p, 'id')
def p_function_body(p):
    """
    function_body : '{' stmts '}' es
    """
    p[0] = parser.functions_handler.handle(p, 'body')
def p_function_call(p):
    """
    function_call : f_call '(' args ')'
    """
    p[0] = parser.functions_handler.handle(p, 'call')
def p_f_call(p):
    """
    f_call : ID
    """
    p.parser.num_args.append(0)
    p[0] = p[1]

def p_params(p):
    """
    params : params ',' param
    """
    p[0] = p[1] + p[3]
def p_params_empty(p):
    """
    params :
    """
    p[0] = ""
def p_single_param(p):
    """
    params : param
    """
    p[0] = p[1]
def p_param(p):
    """
    param : ID ':' type
        |   ID ':' Ptype
    """
    p[0] = parser.functions_handler.handle(p, 'parameter')

def p_out_type(p):
    """
    out_type : RARROW type
            | RARROW Ptype
            |
    """
    p[0] = parser.functions_handler.handle(p, 'out_type')

def p_args(p):
    """
    args : args ',' arg
    """
    p[0] = p[3] + p[1]
def p_args_empty(p):
    """
    args :
        | arg
    """
    if len(p) == 1:
        p[0] = ""
    else:
        p[0] = p[1]
def p_single_arg(p):
    """
    arg : expression
    """
    p[0] = parser.functions_handler.handle(p, 'argument')


######################
##    STMTS RULE    ##
######################

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
        | read
        | function_call
        | declaration_assignment
        | assignment
        | declaration
        | if
        | match
        | while
        | for
        | do_while
        | break
        | continue
        | return
    """
    p[0] = p[1]

######################
##    SCOPE RULE    ##
######################

def p_start_scope(p):
    """
    ss :
    """
    p.parser.current_scope.handle(p, "start_scope")
def p_end_scope(p):
    """
    es :
    """
    p[0] = p.parser.current_scope.handle(p, "end_scope")

######################
##   RETURN STMT    ##
######################

def p_return(p):
    """
    return : RETURN expression
            | RETURN ';'
    """
    p[0] = parser.functions_handler.handle(p, 'return')

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
    for : loop_for ss '(' for_inits ';' expression ';' for_updates ')' ss '{' stmts  '}' es es
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
    do_while : loop_do ss '{' stmts '}' es WHILE '(' expression ')'
    """
    p[0] = parser.loop_handler.handle(p, "do_while")

def p_while(p):
    """
    while : loop_while expression ss '{' stmts '}' es
    """
    p[0] = parser.loop_handler.handle(p, "while")

# This functions append the loop type to the loop list
def p_loop_for(p):
    """
    loop_for : FOR
    """
    parser.current_loops.append("FOR")
def p_loop_do(p):
    """
    loop_do : DO
    """
    parser.current_loops.append("DO")
def p_loop_while(p):
    """
    loop_while : WHILE
    """
    parser.current_loops.append("WHILE")

######################
##     IF STMT      ##
######################

def p_if(p):
    """
    if : IF expression ss '{' stmts '}' es else_if
    """
    p[0] = parser.if_handler.handle(p, "if")
def p_else_if(p):
    """
    else_if : ELSE IF expression ss '{' stmts '}' es else_if
            | else
    """
    p[0] = parser.if_handler.handle(p, "else_if")
def p_else(p):
    """
    else : ELSE ss '{' stmts '}' es
        |
    """
    p[0] = parser.if_handler.handle(p, "else")

######################
##   SWITCH STMT    ##
######################

def p_match(p):
    """
    match : match_start expression '{' cases '}'
    """
    p[0] = parser.match_handler.handle(p, "match")
def p_match_start(p):
    """
    match_start : MATCH
    """
    p.parser.frame_count += 1 # Increment the global count aas to prevent shadowing of variables declared in the match statement
def p_cases(p):
    """
    cases : expression RARROW ss '{' stmts '}' es cases
        | default
    """
    p[0] = parser.match_handler.handle(p, "cases")
def p_default(p):
    """
    default : DEFAULT RARROW ss '{' stmts '}' es
    """
    p[0] = parser.match_handler.handle(p, "default")

######################
##    INIT STMT     ##
######################

def p_variable_init(p):
    """
    declaration_assignment : ID ':' type ASSIGN expression
    """
    p[0] = parser.declaration_assignment_handler.handle(p, "variable_init")
def p_pointer_init(p):
    """
    declaration_assignment : ID ':' Ptype ASSIGN expression
    """
    p[0] = parser.declaration_assignment_handler.handle(p, "pointer_init")
def p_array_literal_init(p):
    """
    declaration_assignment : ID ':' Vtype ndim ASSIGN '[' arrayitems ']'
                        | ID ':' Vtype ASSIGN '[' arrayitems ']'
    """
    p[0] = parser.declaration_assignment_handler.handle(p, "array_literal_init")
def p_array_range_init(p):
    """
    declaration_assignment : ID ':' Vtype ASSIGN '['  INT  RETI  INT ']'
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
def p_pointer_declaration(p):
    """
    declaration : ID ':' Ptype
    """
    p[0] = p.parser.declaration_handler.handle(p, "pointer_declaration")
def p_array_declaration(p):
    """
    declaration : ID ':' Vtype ndim
    """
    p[0] = p.parser.declaration_handler.handle(p, "array_declaration")
def p_array_dimension(p):
    """
    ndim : ndim '[' INT ']'
        | '[' INT ']'
    """
    p[0] = p.parser.declaration_handler.handle(p, "array_dimension")

######################
##   ASSIGN STMT    ##
######################

def p_assignment_indexing(p):
    """
    assignment : ID ndepth ASSIGN expression
    """
    p[0] = parser.assignment_handler.handle(p, "indexing")
def p_assignment_expression(p):
    """
    assignment : ID ASSIGN expression
    """
    p[0] = parser.assignment_handler.handle(p, "variable")

######################
##    READ  STMT    ##
######################

def p_read(p):
    """
    read : read_type '(' multiple_prints ')'
    """
    p[0] = parser.io_handler.handle(p, "read")
def p_read_type(p):
    """
    read_type : READ_INT
            | READ_FLOAT
            | READ_STRING
    """
    p[0] = parser.io_handler.handle(p, "read_type")

######################
##    PRINT STMT    ##
######################

def p_print(p):
    """
    print : PRINT '(' multiple_prints ')'
    """
    p[0] = parser.io_handler.handle(p, "print")
def p_print_multiple(p):
    """
    multiple_prints : multiple_prints ',' expression
    """
    p[0] = parser.io_handler.handle(p, "multiple")
def p_print_single(p):
    """
    multiple_prints : expression
    """
    p[0] = parser.io_handler.handle(p, "single")
def p_print_empty(p):
    """
    multiple_prints :
    """
    p[0] = parser.io_handler.handle(p, "empty")

######################
## TYPES INITAL IMP ##
######################

def p_type(p):
    """
    type : TYPE_INT
        | TYPE_STRING
        | TYPE_FLOAT
    """
    p[0] = p[1]
def p_vtype(p):
    """
    Vtype : TYPE_VEC LT  type GT
    """
    p[0] = p[1] + p[2] + p[3] + p[4]
def p_ptype(p):
    """
    Ptype : '&' TYPE_INT
        | '&' TYPE_STRING
        | '&' TYPE_FLOAT
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
    subexpression : subexpression AND condition
    """
    p[0] = parser.subexpression_handler.handle(p, "and")
def p_subexpression_condition(p):
    """
    subexpression : condition
    """
    p[0] = parser.subexpression_handler.handle(p, "condition")

def p_condition_eq(p):
    """
    condition : condition EQ comparison
    """
    p[0] = parser.condition_handler.handle(p, "eq")
def p_condition_neq(p):
    """
    condition : condition NEQ comparison
    """
    p[0] = parser.condition_handler.handle(p, "neq")
def p_condition_comparison(p):
    """
    condition : comparison
    """
    p[0] = parser.condition_handler.handle(p, "comparison")

def p_comparison_lt(p):
    """
    comparison : comparison LT term
    """
    p[0] = parser.comparison_handler.handle(p, "lt")
def p_comparison_gt(p):
    """
    comparison : comparison GT term
    """
    p[0] = parser.comparison_handler.handle(p, "gt")
def p_comparison_lte(p):
    """
    comparison : comparison LTE term
    """
    p[0] = parser.comparison_handler.handle(p, "lte")
def p_comparison_gte(p):
    """
    comparison : comparison GTE term
    """
    p[0] = parser.comparison_handler.handle(p, "gte")
def p_comparison_term(p):
    """
    comparison : term
    """
    p[0] = parser.comparison_handler.handle(p, "term")

def p_term_sub(p):
    """
    term : term '-' factor
    """
    p[0] = parser.term_handler.handle(p, "sub")
def p_term_add(p):
    """
    term : term '+' factor
    """
    p[0] = parser.term_handler.handle(p, "add")
def p_term_factor(p):
    """
    term : factor
    """
    p[0] = parser.term_handler.handle(p, "factor")

def p_factor_mul(p):
    """
    factor : factor '*' unary
    """
    p[0] = parser.factor_handler.handle(p, "mul")
def p_factor_div(p):
    """
    factor : factor '/' unary
    """
    p[0] = parser.factor_handler.handle(p, "div")
def p_factor_mod(p):
    """
    factor : factor '%' unary
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
    primary : ID ndepth
    """
    p[0] = parser.primary_handler.handle(p, "indexing")
def p_array_indexing_depth(p):
    """
    ndepth : ndepth '[' expression ']'
        | '[' expression ']'
    """
    p[0] = p.parser.primary_handler.handle(p, "array_indexing_depth")
def p_primary_ref(p):
    """
    primary : '&' ID 
    """
    p[0] = parser.primary_handler.handle(p, "ref")
def p_primary_int(p):
    """
    primary : INT
    """
    p[0] = parser.primary_handler.handle(p, "int")
def p_primary_float(p):
    """
    primary : FLOAT
    """
    p[0] = parser.primary_handler.handle(p, "float")
def p_primary_string(p):
    """
    primary : STRING
    """
    p[0] = parser.primary_handler.handle(p, "string")
def p_primary_id(p):
    """
    primary : ID
    """
    p[0] = parser.primary_handler.handle(p, "id")
def p_primary_function(p):
    """
    primary : function_call
    """
    p[0] = p[1]
def p_primary_read(p):
    """
    primary : read
    """
    p[0] = p[1]
def p_primary_new(p):
    """
    primary : '(' expression ')'
    """
    p[0] = parser.primary_handler.handle(p, "new")

def p_error(p):
    syntax_error(p, f"Invalid syntax '{p.value}'")
    sys.exit(1)

parser = yacc.yacc()

parser.primary_handler = Primary()
parser.unary_handler = Unary()
parser.factor_handler = Factor()
parser.term_handler = Term()
parser.comparison_handler = Comparison()
parser.condition_handler = Condition()
parser.subexpression_handler = SubExpression()
parser.expression_handler = Expression()

parser.io_handler = IO()
parser.assignment_handler = Assignment()
parser.declaration_handler = Declaration()
parser.declaration_assignment_handler = DeclarationAssignment()
parser.if_handler = If()
parser.match_handler = Match()
parser.loop_handler = Loop()
parser.loop_break_handler = BreakContinue()

parser.functions_handler = Functions()
parser.num_params = 0
parser.num_args = []

parser.frame_count = 0
parser.global_count = 0
parser.current_scope: Scope = Scope(name="Global Scope", level=0, parent=None) 

parser.type_checker = TypeCheck()

parser.if_count = 0
parser.rel_if_count = 0
parser.match_count = 0
parser.rel_match_count = 0
parser.loop_count = 0
parser.current_loops = [] # This is needed for break and continue statements to be checked
parser.array_assign_items = 0
parser.indexing_depth = []
parser.arr_dim = []

if __name__ == "__main__":
    for line in sys.stdin:
        parser.parse(line)