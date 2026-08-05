"""
Definitions of all terrain types.

Using an Enum makes the code much easier to read than
using integers like 0,1,2...
"""

from enum import Enum


class TerrainType(Enum):

    GRASS = 0
    WATER = 1
    FOREST = 2
    MOUNTAIN = 3
    DESERT = 4
    SWAMP = 5
    ROAD = 6
    CITY = 7
