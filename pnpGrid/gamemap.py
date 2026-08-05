"""
Defines the GameMap class.
A GameMap is a collection of Cells arranged in rows and columns.
"""
from dataclasses import dataclass, field
from cell import Cell
@dataclass
class GameMap:
    width: int
    height: int
    # A 2D list of Cell objects.
    cells: list[list[Cell]] = field(default_factory=list)
