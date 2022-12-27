from typing import List
from dataclasses import dataclass, field

import sys

from tox import compiler_error, std_message

@dataclass
class TypeCheck:
    stack: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.productions = {
            "add":  self._add,
            "sub":  self._sub,
            "mul":  self._mul,
            "div":  self._div,
            "mod":  self._mod,
            "not":  self._not,
            "neg": self._neg,
            "eq":   self._eq,
            "neq":   self._neq,
            "lt":   self._lt,
            "lte":   self._lte,
            "gt":   self._gt,
            "gte":   self._gte,
            "and":  self._and,
            "or":   self._or,
        }

    def handle(self, p, production: str):
        return self.productions[production](p)

    def push(self, type: str):
        self.stack.append(type)

    def pop(self):
        return self.stack.pop()

    def is_empty(self):
        return len(self.stack) == 0

    def _not(self, p):
        """
        unary : '!' unary
        """
        right_operand = self.stack.pop()
        if right_operand == "int":
            self.stack.append("int")
            return p[2] + std_message(["NOT"])
        else:
            compiler_error(p, 2, f"Operation 'not' not supported for type {right_operand}")
            sys.exit(1)

    def _neg(self, p):
        """
        unary : '-' unary
        """
        right_operand = self.stack.pop()
        if right_operand == "int":
            self.stack.append("int")
            return p[2] + std_message(["PUSHI -1", "MUL"])
        else:
            compiler_error(p, 2, f"Operation 'neg' not supported for type {right_operand}")
            sys.exit(1)

    def _mul(self, p):
        """
        factor : factor '*' unary
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand == "int":
            self.stack.append("int")
            return p[1] + p[3] + std_message(["MUL"])
        else:
            compiler_error(p, 2, f"Operation 'mul' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)

    def _div(self, p):
        """
        factor : factor '/' unary
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand == "int":
            self.stack.append("int")
            return p[1] + p[3] + std_message(["DIV"])
        else:
            compiler_error(p, 2, f"Operation 'div' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)

    def _mod(self, p):
        """
        factor : factor '%' unary
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand == "int":
            self.stack.append("int")
            return p[1] + p[3] + std_message(["MOD"])
        else:
            compiler_error(p, 2, f"Operation 'mod' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)

    def _add(self, p):
        """
        term : term '+' factor
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand == "int":
            self.stack.append("int")
            return p[1] + p[3] + std_message(["ADD"])
        elif left_operand.startswith("&") and right_operand == "int":
            self.stack.append(left_operand)
            return p[1] + p[3] + std_message(["PADD"])
        else:
            compiler_error(p, 2, f"Operation 'add' not supported for types {left_operand} and {right_operand}")
            sys.exit(1)

    def _sub(self, p):
        """
        term : term '-' factor
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if (right_operand, left_operand) in [("int", "int"), ("&int", "&int")]:
            self.stack.append("int")
            return p[1] + p[3] + std_message(["SUB"])
        elif left_operand.startswith("&") and right_operand == "int":
            self.stack.append(left_operand)
            return p[1] + p[3] + std_message(["PUSHI -1", "MUL", "PADD"])
        else:
            compiler_error(p, 2, f"Operation 'sub' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)

    def _lt(self, p):
        """
        comparison : comparison LT term
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand:
            self.stack.append("int")
            return p[1] + p[3] + std_message(["INF"])
        else:
            compiler_error(p, 2, f"Operation 'lt' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)

    def _gt(self, p):
        """
        comparison : comparison GT term
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand:
            self.stack.append("int")
            return p[1] + p[3] + std_message(["SUP"])
        else:
            compiler_error(p, 2, f"Operation 'gt' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)

    def _lte(self, p):
        """
        comparison : comparison LTE term
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand:
            self.stack.append("int")
            return p[1] + p[3] + std_message(["INFEQ"])
        else:
            compiler_error(p, 2, f"Operation 'lte' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)

    def _gte(self, p):
        """
        comparison : comparison GTE term
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand:
            self.stack.append("int")
            return p[1] + p[3] + std_message(["SUPEQ"])
        else:
            compiler_error(p, 2, f"Operation 'gte' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)

    def _eq(self, p):
        """
        condition : condition EQ comparison
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand:
            self.stack.append("int")
            return p[1] + p[3] + std_message(["EQUAL"])
        else:
            compiler_error(p, 2, f"Operation 'eq' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)

    def _neq(self, p):
        """
        condition : condition NEQ comparison
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand:
            self.stack.append("int")
            return p[1] + p[3] + std_message(["EQUAL", "NOT"])
        else:
            compiler_error(p, 2, f"Operation 'neq' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)

    def _and(self, p):
        """
        subexpression : subexpression AND condition
        """
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand == "int":
            self.stack.append("int")
            return p[1] + p[3] + std_message(["AND"])
        else:
            compiler_error(p, 2, f"Operation 'and' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)

    def _or(self, p):
        right_operand = self.stack.pop()
        left_operand = self.stack.pop()
        if right_operand == left_operand == "int":
            self.stack.append("int")
            return p[1] + p[3] + std_message(["OR"])
        else:
            compiler_error(p, 2, f"Operation 'or' not supported for types {right_operand} and {left_operand}")
            sys.exit(1)
