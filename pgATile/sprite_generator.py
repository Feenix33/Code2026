"""Generate the initial program-drawn sprite sheet."""
from pathlib import Path
import pygame
from constants import (
    gCOLOR_PATH, gCOLOR_TILE, gCOLOR_TILE_BORDER,
    gSPRITE_SHEET_FILE, gSPRITE_TILE_SIZE, gWRITE_SPRITE_SHEET,
)
from tile import Side, Tile, TileType

def _endpoint(size, side):
    edge, center = 7, size // 2
    if side == Side.TOP: return center, edge
    if side == Side.RIGHT: return size - edge, center
    if side == Side.BOTTOM: return center, size - edge
    return edge, center

def _draw_tile(surface, tile):
    size, center = surface.get_width(), surface.get_width() // 2
    pygame.draw.rect(surface, gCOLOR_TILE, (1,1,size-2,size-2), border_radius=5)
    pygame.draw.rect(surface, gCOLOR_TILE_BORDER, (1,1,size-2,size-2), 3, border_radius=5)
    for first, second in tile.segments():
        p1, p2 = _endpoint(size, first), _endpoint(size, second)
        pygame.draw.line(surface, gCOLOR_PATH, p1, (center,center), 22)
        pygame.draw.line(surface, gCOLOR_PATH, (center,center), p2, 22)
        pygame.draw.circle(surface, gCOLOR_PATH, p1, 11)
        pygame.draw.circle(surface, gCOLOR_PATH, p2, 11)
        pygame.draw.circle(surface, gCOLOR_PATH, (center,center), 11)

def create_sprite_sheet(write_file=gWRITE_SPRITE_SHEET):
    types = (TileType.STRAIGHT, TileType.CORNER, TileType.QUAD_CORNER)
    sheet = pygame.Surface((gSPRITE_TILE_SIZE*3, gSPRITE_TILE_SIZE), pygame.SRCALPHA)
    for i, tile_type in enumerate(types):
        image = pygame.Surface((gSPRITE_TILE_SIZE, gSPRITE_TILE_SIZE), pygame.SRCALPHA)
        _draw_tile(image, Tile(tile_type))
        sheet.blit(image, (i*gSPRITE_TILE_SIZE, 0))
    if write_file:
        output = Path(gSPRITE_SHEET_FILE)
        output.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(sheet, output)
    return sheet

def load_tile_sprites(sheet):
    types = (TileType.STRAIGHT, TileType.CORNER, TileType.QUAD_CORNER)
    return {
        tile_type: sheet.subsurface(pygame.Rect(i*gSPRITE_TILE_SIZE,0,
                                                 gSPRITE_TILE_SIZE,gSPRITE_TILE_SIZE)).copy()
        for i, tile_type in enumerate(types)
    }

if __name__ == "__main__":
    pygame.init()
    create_sprite_sheet()
    pygame.quit()
