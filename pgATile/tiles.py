"""Tile supply and exposed rack."""
import random
from constants import gEXPOSED_TILE_COUNT, gTILE_COUNTS, gTOTAL_TILES
from tile import Tile

def initialize_tiles():
    total = sum(gTILE_COUNTS.values())
    if total != gTOTAL_TILES:
        raise ValueError(f"Tile distribution must total {gTOTAL_TILES}; got {total}.")
    supply = []
    for tile_type, count in gTILE_COUNTS.items():
        supply.extend(Tile(tile_type) for _ in range(count))
    random.shuffle(supply)
    return supply

class TileRack:
    def __init__(self, supply):
        self.supply = supply
        self.exposed = [None] * gEXPOSED_TILE_COUNT
        for slot in range(gEXPOSED_TILE_COUNT):
            self.draw_replacement(slot)

    def draw_replacement(self, slot):
        self.exposed[slot] = self.supply.pop() if self.supply else None

    def take_tile(self, slot):
        tile = self.exposed[slot]
        self.exposed[slot] = None
        return tile
