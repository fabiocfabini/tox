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

    def add(self, name: str) -> None:   # Adds a function to the table
        self.Table[name] = FunctionData(name)

    def get(self, name: str) -> Optional[FunctionData]:  # Gets a function from the table if it exists
        return self.Table.get(name)

    def call(self, p):  # Calls a function
        """
        function_call : ID '(' args ')'
        """
        if self.get(p[1]) is None:  # If the function doesn't exist, report an error
            compiler_error(p, 1, f"Function {p[1]} not declared")
            compiler_note(f"Error on Function '{p.parser.current_function.name}'")
            compiler_note("Called from Functions.call")
            sys.exit(1)
        
        return std_message([f"PUSHA {self.get(p[1]).name}", "CALL"])    # If the function exists, return the assembly code