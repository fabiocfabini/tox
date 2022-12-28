from typing import List
from dataclasses import dataclass, field

import sys

from tox import compiler_error, std_message

@dataclass
class TypeCheck:
    stack: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.productions = {
            "not":  self._not,
            "neg": self._neg,
            "mul":  self._mul,
            "div":  self._div,
            "mod":  self._mod,
            "add":  self._add,
            "sub":  self._sub,
            "lt":   self._lt,
            "lte":   self._lte,
            "gt":   self._gt,
            "gte":   self._gte,
            "eq":   self._eq,
            "neq":   self._neq,
            "and":  self._and,
            "or":   self._or,
        }

    def handle(self, p, production: str):
        return self.productions[production](p)

    def push(self, type: str):
        self.stack.append(type)

    def pop(self):
        if len(self.stack) == 0:
            return "None"
        return self.stack.pop()

    def is_empty(self):
        return len(self.stack) == 0

    def _not(self, p):
        """
        unary : '!' unary
        """
        right_operand = self.stack.pop()
        if right_operand in ("integer", "float"):
            self.stack.append(right_operand)
            return p[2] + std_message(["NOT"])
        else:
            compiler_error(p, 2, f"Operation 'not' not supported for type '{right_operand}'")
            sys.exit(1)

    def _neg(self, p):
        """
        unary : '-' unary
        """
        right_operand = self.stack.pop()
        if right_operand == "integer":
            self.stack.append("integer")
            return p[2] + std_message(["PUSHI -1", "MUL"])
        elif right_operand == "float":
            self.stack.append("float")
            return p[2] + std_message(["PUSHF -1.0", "FMUL"])
        else:
            compiler_error(p, 2, f"Operation 'neg' not supported for type '{right_operand}'")
            sys.exit(1)

    def _mul(self, p):
        """
        factor : factor '*' unary
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand == "integer":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["MUL"])
        elif right_operand == left_operand == "float":
            self.stack.append("float")
            return p[1] + p[3] + std_message(["FMUL"])
        else:
            compiler_error(p, 2, f"Operation 'mul' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _div(self, p):
        """
        factor : factor '/' unary
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand == "integer":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["DIV"])
        elif right_operand == left_operand == "float":
            self.stack.append("float")
            return p[1] + p[3] + std_message(["FDIV"])
        else:
            compiler_error(p, 2, f"Operation 'div' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _mod(self, p):
        """
        factor : factor '%' unary
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand == "integer":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["MOD"])
        else:
            compiler_error(p, 2, f"Operation 'mod' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _add(self, p):
        """
        term : term '+' factor
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        assert not left_operand.startswith("vec"), "vector type cannot appear in this stage"
        if right_operand == left_operand == "integer":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["ADD"])
        elif right_operand == left_operand == "float":
            self.stack.append("float")
            return p[1] + p[3] + std_message(["FADD"])
        elif left_operand.startswith("&") and right_operand == "integer":
            self.stack.append(left_operand)
            return p[1] + p[3] + std_message(["PADD"])
        elif right_operand == left_operand == "filum":
            self.stack.append("filum")
            return p[3] + p[1] + std_message(["CONCAT"])
        else:
            compiler_error(p, 2, f"Operation 'add' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _sub(self, p):
        """
        term : term '-' factor
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        assert not left_operand.startswith("vec"), "vector type cannot appear in this stage"
        if (right_operand, left_operand) in [("integer", "integer"), ("&integer", "&integer")]:
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["SUB"])
        elif right_operand == left_operand == "float":
            self.stack.append("float")
            return p[1] + p[3] + std_message(["FSUB"])
        elif left_operand.startswith("&") and right_operand == "integer":
            self.stack.append(left_operand)
            return p[1] + p[3] + std_message(["PUSHI -1", "MUL", "PADD"])
        else:
            compiler_error(p, 2, f"Operation 'sub' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _lt(self, p):
        """
        comparison : comparison LT term
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        assert not left_operand.startswith("vec"), "vector type cannot appear in this stage"
        if right_operand == left_operand and left_operand not in ("filum", "float"):
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["INF"])
        elif right_operand == left_operand == "float":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["FINF", "FTOI"])
        else:
            compiler_error(p, 2, f"Operation 'lt' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _gt(self, p):
        """
        comparison : comparison GT term
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        assert not left_operand.startswith("vec"), "vector type cannot appear in this stage"
        if right_operand == left_operand and left_operand not in ("filum", "float"):
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["SUP"])
        elif right_operand == left_operand == "float":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["FSUP", "FTOI"])
        else:
            compiler_error(p, 2, f"Operation 'gt' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _lte(self, p):
        """
        comparison : comparison LTE term
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        assert not left_operand.startswith("vec"), "vector type cannot appear in this stage"
        if right_operand == left_operand and left_operand not in ("filum", "float"):
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["INFEQ"])
        elif right_operand == left_operand == "float":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["FINFEQ", "FTOI"])
        else:
            compiler_error(p, 2, f"Operation 'lte' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _gte(self, p):
        """
        comparison : comparison GTE term
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        assert not left_operand.startswith("vec"), "vector type cannot appear in this stage"
        if right_operand == left_operand and left_operand not in ("filum", "float"):
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["SUPEQ"])
        elif right_operand == left_operand == "float":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["FSUPEQ", "FTOI"])
        else:
            compiler_error(p, 2, f"Operation 'gte' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _eq(self, p):
        """
        condition : condition EQ comparison
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        assert not left_operand.startswith("vec"), "vector type cannot appear in this stage"
        if right_operand == left_operand and left_operand != "filum":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["EQUAL"])
        else:
            compiler_error(p, 2, f"Operation 'eq' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _neq(self, p):
        """
        condition : condition NEQ comparison
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        assert not left_operand.startswith("vec"), "vector type cannot appear in this stage"
        if right_operand == left_operand and left_operand != "filum":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["EQUAL", "NOT"])
        else:
            compiler_error(p, 2, f"Operation 'neq' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _and(self, p):
        """
        subexpression : subexpression AND condition
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        assert not left_operand.startswith("vec"), "vector type cannot appear in this stage"
        if right_operand == left_operand == "integer":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["AND"])
        else:
            compiler_error(p, 2, f"Operation 'and' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)

    def _or(self, p):
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        assert not left_operand.startswith("vec"), "vector type cannot appear in this stage"
        if right_operand == left_operand == "integer":
            self.stack.append("integer")
            return p[1] + p[3] + std_message(["OR"])
        else:
            compiler_error(p, 2, f"Operation 'or' not supported for types '{left_operand}' and '{right_operand}'")
            sys.exit(1)
