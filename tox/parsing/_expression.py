import sys

from tox import compiler_error, compiler_note, std_message


class Primary:
    """
    Class that handles the basic building blocks of an expression.
    """
    def __init__(self):
        self.productions = {    #   Maps production names to their respective functions
            "indexing": self._indexing,
            "id": self._id,
            "int": self._int,
            "string": self._string,
            "true": self._true,
            "false": self._false,
            "new": self._new
        }

    def handle(self, p, production) -> str:     # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _indexing(self, p) -> str: # Handles indexing into an array
        """
        primary : ID '[' expression ']'
        """
        id_meta, in_function, scope_name = p.parser.current_scope.get(p[1]) # Get the metadata of the variable
        if id_meta is None: # If the variable is not declared, Throw an error
            compiler_error(p, 1, f"Variable {p[1]} not declared")
            compiler_note("Called from Primary._indexing")
            sys.exit(1)
        if id_meta.type != "&int":  # If the variable is not an array, Throw an error
            compiler_error(p, 1, f"Variable {p[1]} is not an array")
            compiler_note("Called from Primary._indexing")
            sys.exit(1)
        p.parser.type_stack.append("int")
        push_op = "PUSHGP" if not in_function else "PUSHFP" # If the variable is in a function, push the frame pointer else push the global pointer
        return std_message([push_op, f"PUSHI {id_meta.stack_position[0]}", "PADD", f"{p[3]}PADD", "LOAD 0"]) # Return the message

    def _id(self, p) -> str: # Handles pushing the value of a variable
        """
        primary : ID
        """
        id_meta, in_function, scope_name = p.parser.current_scope.get(p[1]) # Get the metadata of the variable
        if id_meta is None: # If the variable is not declared, Throw an error
            compiler_error(p, 1, f"Variable {p[1]} not declared")
            compiler_note("Called from Primary.id")
            sys.exit(1)
        p.parser.type_stack.append(id_meta.type)
        push_op = "PUSHGP" if not in_function else "PUSHFP" # If the variable is in a function, push the frame pointer else push the global pointer
        return std_message([push_op, f"LOAD {id_meta.stack_position[0]}"])  # Return the message

    def _int(self, p) -> str: # Handles pushing an integer
        """
        primary : INT
        """
        p.parser.type_stack.append("int")
        return std_message([f"PUSHI {p[1]}"]) # Return the message

    def _string(self, p) -> str: # Handles pushing an integer
        """
        primary : STRING
        """
        p.parser.type_stack.append("string")
        return std_message([f"PUSHS {p[1]}"]) # Return the message

    def _true(self, p) -> str: # Handles pushing a true value
        """
        primary : TRUE
        """
        p.parser.type_stack.append("int")
        return std_message(["PUSHI 1"]) # Return the message

    def _false(self, p) -> str: # Handles pushing a false value
        """
        primary : TRUE
        """
        p.parser.type_stack.append("int")
        return std_message(["PUSHI 0"]) # Return the message

    def _new(self, p) -> str: # Handles a grouped expression
        """
        primary : '(' expression ')'
        """
        return p[2] # Return the message


class Unary:
    """
    Class that handles unary operations.
    """
    def __init__(self):
        self.productions = {    #   Maps production names to their respective functions
            "not": self._not,
            "neg": self._neg,
            "primary": self._primary
        }

    def handle(self, p, production) -> str:    # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _not(self, p) -> str: # Handles a not operation
        """
        unary : '!' unary
        """
        top = p.parser.type_stack.pop()
        if top != "int":
            compiler_error(p, 2, f"Cannot apply not to {top}")
            compiler_note("Called from Unary._not")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[2]}", "NOT"]) # Return the message

    def _neg(self, p) -> str: # Handles a negation operation
        """
        unary : '-' unary
        """
        top = p.parser.type_stack.pop()
        if top != "int":
            compiler_error(p, 2, f"Cannot apply negation to {top}")
            compiler_note("Called from Unary._neg")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[2]}PUSHI -1", "MUL"]) # Return the message

    def _primary(self, p) -> str: # Handles a primary expression
        """
        unary : primary
        """
        return p[1] # Return the message


class Factor:
    """
    Class that handles factor operations.
    """
    def __init__(self):
        self.productions = {   #   Maps production names to their respective functions
            "mul": self._mul,
            "div": self._div,
            "mod": self._mod,
            "unary": self._unary
        }

    def handle(self, p, production) -> str:   # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _mul(self, p) -> str: # Handles a multiplication operation
        """
        factor : unary '*' factor
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot multiply {first} and {second}")
            compiler_note("Called from Factor._mul")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}MUL"]) # Return the message

    def _div(self, p) -> str: # Handles a division operation
        """
        factor : unary '/' factor
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot divide {first} and {second}")
            compiler_note("Called from Factor._div")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}DIV"]) # Return the message

    def _mod(self, p) -> str: # Handles a modulo operation
        """
        factor : unary '%' factor
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot modulo {first} and {second}")
            compiler_note("Called from Factor._mod")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}MOD"]) # Return the message

    def _unary(self, p) -> str: # Handles a unary expression
        """
        factor : unary
        """
        return p[1] # Return the message


class Term:
    """
    Class that handles term operations.
    """
    def __init__(self):
        self.productions = {   #   Maps production names to their respective functions
            "add": self._add,
            "sub": self._sub,
            "factor": self._factor
        }

    def handle(self, p, production) -> str:    # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _add(self, p) -> str: # Handles an addition operation
        """
        term : factor '+' term
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot add {first} and {second}")
            compiler_note("Called from Term._add")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}ADD"])    # Return the message

    def _sub(self, p) -> str: # Handles a subtraction operation
        """
        term : factor '-' term
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot subtract {first} and {second}")
            compiler_note("Called from Term._sub")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}SUB"])   # Return the message

    def _factor(self, p) -> str: # Handles a factor expression
        """
        term : factor
        """
        return p[1] # Return the message


class Comparison:
    """
    Class that handles comparison operations.
    """
    def __init__(self):
        self.productions = {  #   Maps production names to their respective functions
            "lt": self._lt,
            "gt": self._gt,
            "lte": self._lte,
            "gte": self._gte,
            "term": self._term
        }

    def handle(self, p, production) -> str:    # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _lt(self, p) -> str: # Handles a less than operation
        """
        comparison : term '<' comparison
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot compare {first} and {second}")
            compiler_note("Called from Comparison._lt")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}INF"]) # Return the message

    def _gt(self, p) -> str: # Handles a greater than operation
        """
        comparison : term '>' comparison
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot compare {first} and {second}")
            compiler_note("Called from Comparison._gt")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}SUP"]) # Return the message

    def _lte(self, p) -> str: # Handles a less than or equal to operation
        """
        comparison : term '<=' comparison
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot compare {first} and {second}")
            compiler_note("Called from Comparison._lte")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}INFEQ"]) # Return the message

    def _gte(self, p) -> str: # Handles a greater than or equal to operation
        """
        comparison : term '>=' comparison
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot compare {first} and {second}")
            compiler_note("Called from Comparison._gte")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}SUPEQ"]) # Return the message

    def _term(self, p) -> str: # Handles a term expression
        """
        comparison : term
        """
        return p[1] # Return the message


class Condition:
    """
    Class that handles conditions.
    """
    def __init__(self):
        self.productions = {    #   Maps production names to their respective functions
            "eq": self._eq,
            "neq": self._neq,
            "comparison": self._comparison
        }

    def handle(self, p, production) -> str:   # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _eq(self, p) -> str: # Handles an equal to operation
        """
        condition : comparison EQ condition
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot compare {first} and {second}")
            compiler_note("Called from Condition._eq")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}EQUAL"]) # Return the message

    def _neq(self, p) -> str: # Handles a not equal to operation
        """
        condition : comparison NEQ condition
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot compare {first} and {second}")
            compiler_note("Called from Condition._neq")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}EQUAL", "NOT"]) # Return the message

    def _comparison(self, p) -> str: # Handles a comparison expression
        """
        condition : comparison
        """
        return p[1] # Return the message


class SubExpression:
    """
    Class that handles subexpressions.
    """
    def __init__(self):
        self.productions = {   #   Maps production names to their respective functions
            "and": self._and,
            "condition": self._condition
        }

    def handle(self, p, production) -> str:  # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _and(self, p) -> str: # Handles an and operation
        """
        subexpression : subexpression AND condition
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot compare {first} and {second}")
            compiler_note("Called from SubExpression._and")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}AND"])    # Return the message

    def _condition(self, p) -> str: # Handles a condition expression
        """
        subexpression : condition
        """
        return p[1] # Return the message

class Expression:
    """
    Class that handles expressions.
    """
    def __init__(self):
        self.productions = {    #   Maps production names to their respective functions
            "or": self._or,
            "subexpression": self._subexpression
        }

    def handle(self, p, production) -> str:  # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _or(self, p) -> str: # Handles an or operation
        """
        expression : expression OR subexpression
        """
        first = p.parser.type_stack.pop()
        second = p.parser.type_stack.pop()
        if first != "int" or second != "int":
            compiler_error(p, 2, f"Cannot compare {first} and {second}")
            compiler_note("Called from Expression._or")
            sys.exit(1)
        p.parser.type_stack.append("int")
        return std_message([f"{p[1]}{p[3]}OR"]) # Return the message

    def _subexpression(self, p) -> str: # Handles a subexpression expression
        """
        expression : subexpression
        """
        return p[1] # Return the message