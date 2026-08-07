import random
from cell import Cell
from terrain import TerrainType
from gamemap import GameMap

class GridGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def generate(self):
        game_map = GameMap(
            width=self.width,
            height=self.height
        )
        terrain_choices = list(TerrainType)
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(
                    Cell(
                        terrain=random.choice(terrain_choices)
                    )
                )
            game_map.cells.append(row)
        return game_map
