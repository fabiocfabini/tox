from __future__ import annotations
from typing import Optional, Dict
from dataclasses import dataclass, field

import sys

from tox import compiler_error, compiler_note, std_message

@dataclass
class FunctionData:
    """
    Class That represents everything about a function.
    Input values and output values are missing but should be added later to provide for a better compiler.
    """
    name: str

@dataclass
class Functions:
    """
    Class that holds all the functions.
    """
    Table: Dict[str, FunctionData] = field(default_factory=dict)    # Table of functions

    def __post_init__(self):
        self.productions = {
            "call": self._call,
            "function_header": self._header,
            "function_body": self._body,
            "parameter": self._parameter,
            "argument": self._argument,
        }

    def handle(self, p, production: str):
        return self.productions[production](p)

    def add(self, name: str) -> None:   # Adds a function to the table
        self.Table[name] = FunctionData(name)

    def get(self, name: str) -> Optional[FunctionData]:  # Gets a function from the table if it exists
        return self.Table.get(name)

    def _header(self, p):  # Declares a function
        """
        function_header : FUNCTION ID ss '(' params ')'
        """
        if p.parser.functions_handler.get(p[2]) is not None:
            compiler_error(p, 2, f"Redefinition of function {p[2]}")
            compiler_note("Called from p_function_id.")
            sys.exit(1)
        p.parser.functions_handler.add(p[2])
        p.parser.current_function = p.parser.functions_handler.get(p[2])
        return std_message([f"{p[2].replace('_', '')}:"]) + p[5]

    def _body(self, p):  # Adds the body of a function
        """
        function_body :  '{' stmts '}' es
        """
        out = p[2] + std_message([f"RETURN"])
        p.parser.current_function = None
        return out

    def _parameter(self, p):  # Adds a parameter to the function
        """
        param : ID ':' type
        """
        p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count))
        p.parser.frame_count += 1
        p.parser.num_params += 1
        return std_message(["PUSHI 0", "PUSHFP", f"LOAD {-p.parser.num_params}", f"STOREL {p.parser.num_params-1}"])

    def _argument(self, p):  # Adds an argument to the function
        """
        args : expression
        """
        return p[1]

    def _call(self, p):  # Calls a function
        """
        function_call : ID '(' args ')'
        """
        if self.get(p[1]) is None:  # If the function doesn't exist, report an error
            compiler_error(p, 1, f"Function {p[1]} not declared")
            compiler_note(f"Error on Function '{p.parser.current_function.name}'")
            compiler_note("Called from Functions._call")
            sys.exit(1)
        out = p[3] + std_message([f"PUSHA {self.get(p[1]).name}", "CALL", f"POP {p.parser.num_params}"])    # If the function exists, return the assembly code
        p.parser.num_params = 0
        return out