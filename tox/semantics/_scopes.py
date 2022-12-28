from __future__ import annotations
from typing import Optional, Dict, Tuple
from dataclasses import dataclass, field

from tox import std_message


@dataclass
class MetaData:
    """
    Class that represents the metadata of a variable in a given scope.
    """
    type: str
    stack_position: Tuple[int, int]
    p_init: bool = True

    @property
    def size_in_cells(self) -> int:
        """
        Return the size in cells that the variable takes up in the stack.
        """
        return self.stack_position[1] - self.stack_position[0] + 1

@dataclass
class Scope:
    """
    Class that represents a scope and all the variables in it.
    """
    name: str
    level : int
    parent: Optional[Scope] = None
    in_function: bool = False
    Table: Dict[str, MetaData] = field(default_factory=dict)

    def __post_init__(self):
        self.productions = {
            "start_scope": self._start_scope,
            "end_scope": self._end_scope,
        }

    def handle(self, p, production: str):
        return self.productions[production](p)


    def add(self, key: str, type: str, stack_position: Tuple[int, int], p_init: bool = True): # Adds a variable to the scope
        self.Table[key] = MetaData(type, stack_position, p_init)

    def get(self, key: str) -> Tuple[Optional[MetaData], bool]:
        """
        Returns the metadata of a variable in the scope if it exists in any scope.
        Also returns whether or not the variable is in a function as well as the name of the scope it is in.
        """
        if self.parent == None:
            return self.Table.get(key), self.in_function, self.name

        metadata = self.Table.get(key)
        if metadata is not None:
            return metadata, self.in_function, self.name
        return self.parent.get(key)

    def num_alloced(self) -> int:  # Returns the number of cells allocated in the scope
        return sum([metadata.size_in_cells for metadata in self.Table.values()])

    def _start_scope(self, p):
        """
        ss :
        """
        p.parser.current_scope = Scope(
            name=f"SCOPE_{p.parser.current_scope.level + 1}", 
            level=p.parser.current_scope.level + 1, 
            parent=p.parser.current_scope,
            in_function=False if p.parser.functions_handler.current_function is None else True
        )

    def _end_scope(self, p):
        """
        es :
        """
        if p.parser.functions_handler.current_function is not None:
            p.parser.frame_count -= p.parser.current_scope.num_alloced() 
        else:
            p.parser.global_count -= p.parser.current_scope.num_alloced()
        out = std_message([f"POP {p.parser.current_scope.num_alloced()}"])
        p.parser.current_scope = p.parser.current_scope.parent
        return out

