"""
Maps terrain types to visual styles.
Every renderer can use this file.
Later we might have
pygame_style.py
pdf_style.py
ascii_style.py
"""
from dataclasses import dataclass
from terrain import TerrainType
@dataclass
class TerrainStyle:
    fill_color: tuple
    pattern: str
STYLE = {
    TerrainType.GRASS:
        TerrainStyle((80, 180, 80), "solid"),
    TerrainType.WATER:
        TerrainStyle((70, 120, 255), "waves"),
    TerrainType.FOREST:
        TerrainStyle((20, 120, 20), "trees"),
    TerrainType.MOUNTAIN:
        TerrainStyle((120, 120, 120), "rocks"),
    TerrainType.DESERT:
        TerrainStyle((230, 210, 120), "dots"),
    TerrainType.SWAMP:
        TerrainStyle((90, 120, 40), "cross"),
    TerrainType.ROAD:
        TerrainStyle((100, 100, 100), "lines"),
    TerrainType.CITY:
        TerrainStyle((200, 80, 80), "grid")
}

class TerrainStyleSet:
    def __init__(self):
        self.styles = {
            TerrainType.GRASS:
                TerrainStyle((80, 180, 80), "solid"),
            TerrainType.WATER:
                TerrainStyle((70, 120, 255), "waves"),
            TerrainType.FOREST:
                TerrainStyle((20, 120, 20), "trees"),
            TerrainType.MOUNTAIN:
                TerrainStyle((120, 120, 120), "rocks"),
            TerrainType.DESERT:
                TerrainStyle((230, 210, 120), "dots"),
            TerrainType.SWAMP:
                TerrainStyle((90, 120, 40), "cross"),
            TerrainType.ROAD:
                TerrainStyle((100, 100, 100), "lines"),
            TerrainType.CITY:
                TerrainStyle((200, 80, 80), "grid")
        }

    def get(self, terrain):
        return self.styles[terrain]

