from typing import List
from dataclasses import dataclass, field

import sys

from tox import compiler_error

@dataclass
class TypeCheck:
    stack: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.productions = {
            "add":  self._add,
            "sub":  self._add,
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
        self.productions[production](p)

    def push(self, type: str):
        self.stack.append(type)

    def pop(self):
        return self.stack.pop()

    def is_empty(self):
        return len(self.stack) == 0

    def _add(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'add' not supported for types {first} and {second}")
            sys.exit(1)

    def _sub(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'sub' not supported for types {first} and {second}")
            sys.exit(1)

    def _mul(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'mul' not supported for types {first} and {second}")
            sys.exit(1)

    def _div(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'div' not supported for types {first} and {second}")
            sys.exit(1)

    def _mod(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'mod' not supported for types {first} and {second}")
            sys.exit(1)

    def _not(self, p):
        first = self.stack.pop()
        if first == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'not' not supported for type {first}")
            sys.exit(1)

    def _neg(self, p):
        first = self.stack.pop()
        if first == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'neg' not supported for type {first}")
            sys.exit(1)

    def _eq(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'eq' not supported for types {first} and {second}")
            sys.exit(1)

    def _neq(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'neq' not supported for types {first} and {second}")
            sys.exit(1)

    def _lt(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'lt' not supported for types {first} and {second}")
            sys.exit(1)

    def _lte(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'lte' not supported for types {first} and {second}")
            sys.exit(1)

    def _gt(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'gt' not supported for types {first} and {second}")
            sys.exit(1)

    def _gte(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'gte' not supported for types {first} and {second}")
            sys.exit(1)

    def _and(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'and' not supported for types {first} and {second}")
            sys.exit(1)

    def _or(self, p):
        first = self.stack.pop()
        second = self.stack.pop()
        if first == second == "int":
            self.stack.append("int")
        else:
            compiler_error(p, 2, f"Operation 'or' not supported for types {first} and {second}")
            sys.exit(1)
