"""Logical tile definitions and rotation."""
from dataclasses import dataclass
from enum import IntEnum

class Side(IntEnum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3

class TileType:
    STRAIGHT = "straight"
    CORNER = "corner"
    QUAD_CORNER = "quad_corner"

gBASE_SEGMENTS = {
    TileType.STRAIGHT: ((Side.TOP, Side.BOTTOM),),
    TileType.CORNER: ((Side.TOP, Side.RIGHT),),
    TileType.QUAD_CORNER: (
        (Side.TOP, Side.RIGHT),
        (Side.BOTTOM, Side.LEFT),
    ),
}

def rotate_side(side, quarter_turns):
    return Side((int(side) + quarter_turns) % 4)

@dataclass
class Tile:
    tile_type: str
    rotation: int = 0

    def rotate_clockwise(self):
        self.rotation = (self.rotation + 1) % 4

    def rotate_counterclockwise(self):
        self.rotation = (self.rotation - 1) % 4

    def segments(self):
        return tuple(
            tuple(rotate_side(s, self.rotation) for s in segment)
            for segment in gBASE_SEGMENTS[self.tile_type]
        )

    def connections(self):
        return frozenset(s for segment in self.segments() for s in segment)

    def is_quad(self):
        return self.tile_type == TileType.QUAD_CORNER
