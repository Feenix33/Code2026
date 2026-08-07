"""
A single square of the map.
"""
from dataclasses import dataclass
from terrain import TerrainType

@dataclass
class Cell:
    """
    Represents one location on the map.
    """
    terrain: TerrainType = TerrainType.GRASS
    occupied: bool = False
