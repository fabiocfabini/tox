from __future__ import annotations
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

@dataclass
class MetaData:
    type: str
    stack_position: Tuple[int, int]

    @property
    def size_in_cells(self) -> int:
        return self.stack_position[1] - self.stack_position[0] + 1

@dataclass
class Stack:
    name: str 
    level: int 
    parent: Optional[Stack] = None

    def __post_init__(self):
        self.Table: Dict[str, MetaData] = {}

    def add(self, key: str, type: str, stack_position: Tuple[int, int]):
        self.Table[key] = MetaData(type, stack_position)

    def get(self, key: str) -> Optional[MetaData]:
        if self.parent == None:
            return self.Table.get(key)

        metadata = self.Table.get(key)
        if metadata is not None:
            return metadata
        return self.parent.get(key)

    def num_alloced(self) -> int:
        return sum([metadata.size_in_cells for metadata in self.Table.values()])
