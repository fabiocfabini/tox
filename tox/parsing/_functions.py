from __future__ import annotations
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field

import sys

from tox import compiler_error, compiler_note, std_message

@dataclass
class FunctionData:
    name: str


@dataclass
class Functions:
    Table: Dict[str, FunctionData] = field(default_factory=dict)

    def add(self, name: str):
        self.Table[name] = FunctionData(name)

    def get(self, name: str) -> Optional[FunctionData]:
        return self.Table.get(name)

    def call(self, p):
        """
        function_call : ID '(' args ')'
        """
        if self.get(p[1]) is None:
            compiler_error(p, 1, f"Function {p[1]} not declared")
            compiler_note(f"Error on Function '{p.parser.current_function.name}'")
            compiler_note("Called from Functions.call")
            sys.exit(1)
        
        return std_message([f"PUSHA {self.get(p[1]).name}", "CALL"])