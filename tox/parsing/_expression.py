from typing import List

from tox import compiler_error, syntax_error, find_column, find_column_comp

def std_message(msg: List[str]):
    return "\n".join(msg) + "\n"


class Primary:
    def __init__(self):
        self.productions = {
            "indexing": self._indexing,
            "id": self._id,
            "int": self._int,
            "true": self._true,
            "false": self._false,
            "new": self._new
        }

    def handle(self, p, production):
        return self.productions[production](p)

    def _indexing(self, p):
        """
        primary : ID '[' expression ']'
        """
        id_meta = p.parser.current_scope.get(p[1])
        if id_meta is None:
            compiler_error(p, 1, f"Variable {p[1]} not declared")
        if id_meta.type != "&int":
            compiler_error(p, 1, f"Variable {p[1]} is not an array")
        return std_message([f"PUSHGP", f"PUSHI {id_meta.stack_position[0]}", "PADD", f"{p[3]}PADD", "LOAD 0"])

    def _id(self, p):
        """
        primary : ID
        """
        id_meta = p.parser.current_scope.get(p[1])
        if id_meta is None:
            compiler_error(p, 1, f"Variable {p[1]} not declared")
        return std_message(["PUSHGP", f"LOAD {id_meta.stack_position[0]}"])

    def _int(self, p):
        """
        primary : INT
        """
        return std_message([f"PUSHI {p[1]}"])

    def _true(self, p):
        """
        primary : TRUE
        """
        return std_message(["PUSHI 1"])

    def _false(self, p):
        """
        primary : TRUE
        """
        return std_message(["PUSHI 0"])

    def _new(self, p):
        """
        primary : '(' expression ')'
        """
        return p[2]


class Unary:
    def __init__(self):
        self.productions = {
            "not": self._not,
            "neg": self._neg,
            "primary": self._primary
        }

    def handle(self, p, production):
        return self.productions[production](p)

    def _not(self, p):
        """
        unary : '!' unary
        """
        return std_message([f"{p[2]}", "NOT"])

    def _neg(self, p):
        """
        unary : '-' unary
        """
        return std_message([f"{p[2]}PUSHI -1", "MUL"])

    def _primary(self, p):
        """
        unary : primary
        """
        return p[1]


class Factor:
    def __init__(self):
        self.productions = {
            "mul": self._mul,
            "div": self._div,
            "mod": self._mod,
            "unary": self._unary
        }

    def handle(self, p, production):
        return self.productions[production](p)

    def _mul(self, p):
        """
        factor : unary '*' factor
        """
        return std_message([f"{p[1]}{p[3]}MUL"])

    def _div(self, p):
        """
        factor : unary '/' factor
        """
        return std_message([f"{p[1]}{p[3]}DIV"])

    def _mod(self, p):
        """
        factor : unary '%' factor
        """
        return std_message([f"{p[1]}{p[3]}MOD"])

    def _unary(self, p):
        """
        factor : unary
        """
        return p[1]


class Term:
    def __init__(self):
        self.productions = {
            "add": self._add,
            "sub": self._sub,
            "factor": self._factor
        }

    def handle(self, p, production):
        return self.productions[production](p)

    def _add(self, p):
        """
        term : factor '+' term
        """
        return std_message([f"{p[1]}{p[3]}ADD"])

    def _sub(self, p):
        """
        term : factor '-' term
        """
        return std_message([f"{p[1]}{p[3]}SUB"])

    def _factor(self, p):
        """
        term : factor
        """
        return p[1]


class Comparison:
    def __init__(self):
        self.productions = {
            "lt": self._lt,
            "gt": self._gt,
            "lte": self._lte,
            "gte": self._gte,
            "term": self._term
        }

    def handle(self, p, production):
        return self.productions[production](p)

    def _lt(self, p):
        """
        comparison : term '<' comparison
        """
        return std_message([f"{p[1]}{p[3]}INF"])

    def _gt(self, p):
        """
        comparison : term '>' comparison
        """
        return std_message([f"{p[1]}{p[3]}SUP"])

    def _lte(self, p):
        """
        comparison : term '<=' comparison
        """
        return std_message([f"{p[1]}{p[3]}INFEQ"])

    def _gte(self, p):
        """
        comparison : term '>=' comparison
        """
        return std_message([f"{p[1]}{p[3]}SUPEQ"])

    def _term(self, p):
        """
        comparison : term
        """
        return p[1]


class Condition:
    def __init__(self):
        self.productions = {
            "eq": self._eq,
            "neq": self._neq,
            "comparison": self._comparison
        }

    def handle(self, p, production):
        return self.productions[production](p)

    def _eq(self, p):
        """
        condition : comparison EQ condition
        """
        return std_message([f"{p[1]}{p[3]}EQUAL"])

    def _neq(self, p):
        """
        condition : comparison NEQ condition
        """
        return std_message([f"{p[1]}{p[3]}EQUAL", "NOT"])

    def _comparison(self, p):
        """
        condition : comparison
        """
        return p[1]


class SubExpression:
    def __init__(self):
        self.productions = {
            "and": self._and,
            "condition": self._condition
        }

    def handle(self, p, production):
        return self.productions[production](p)

    def _and(self, p):
        """
        subexpression : subexpression AND condition
        """
        return std_message([f"{p[1]}{p[3]}AND"])

    def _condition(self, p):
        """
        subexpression : condition
        """
        return p[1]

class Expression:
    def __init__(self):
        self.productions = {
            "or": self._or,
            "subexpression": self._subexpression
        }

    def handle(self, p, production):
        return self.productions[production](p)

    def _or(self, p):
        """
        expression : expression OR subexpression
        """
        return std_message([f"{p[1]}{p[3]}OR"])

    def _subexpression(self, p):
        """
        expression : subexpression
        """
        return p[1]