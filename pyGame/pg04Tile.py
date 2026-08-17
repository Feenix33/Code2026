"""
Experiment to draw a square tile with path

"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import random
import math
from dataclasses import dataclass, field


@dataclass
class Tile:
    id: int
    orient: int
    pos: (int, int) = (0,0)
    paths: list = field(default_factory=list)

def draw_tile(screen, tile):
    kDim = 100       # size of a side
    kPath = 20      # % of dim that is path width
    kBorder = 3     # border thickness
    kMid = kDim/2   # half a dim
    kPathW = 9      # path thickness

    # kolors
    klrGrass = (64,192,64)
    klrBorder = (255, 215, 0) 
    klrPath =  (165, 42, 42)

    # calcs
    x = tile.pos[0] * kDim
    y = tile.pos[1] * kDim

    pygame.draw.rect(screen, klrGrass, (x, y, kDim, kDim))
    pygame.draw.rect(screen, klrBorder, (x, y, kDim, kDim), kBorder)

    # draw the paths
    posN = (x+kMid, y)
    posS = (x+kMid, y+kDim)
    posE = (x+kDim, y+kMid)
    posW = (x, y+kMid)
    pii = 3.14159
    for path in tile.paths:
        match path:
            case 'NS' | 'SN': # straight
                pygame.draw.line(screen, klrPath, posN, posS, kPathW)
            case 'EW' | 'WE':  # straight
                pygame.draw.line(screen, klrPath, posW, posE, kPathW)
            case 'NE' | 'EW':
                # pygame.draw.line(screen, klrPath, posN, posE, kPathW)
                pygame.draw.arc(screen, klrPath, (x+kMid, y-kMid, kDim, kDim), pii, -pii/2, kPathW)
            case 'NW' | 'WN':
                # pygame.draw.line(screen, klrPath, posN, posW, kPathW)
                pygame.draw.arc(screen, klrPath, (x-kMid, y-kMid, kDim, kDim), -pii/2, 0, kPathW)
            case 'SE' | 'ES':
                # pygame.draw.line(screen, klrPath, posS, posE, kPathW)
                pygame.draw.arc(screen, klrPath, (x+kMid, y+kMid, kDim, kDim), pii/2, pii, kPathW)
            case 'SW' | 'WS':
                # pygame.draw.line(screen, klrPath, posS, posW, kPathW)
                pygame.draw.arc(screen, klrPath, (x-kMid, y+kMid, kDim, kDim), 0, pii/2, kPathW)
            case _:
                print (f"Unknown path type {path}")


# ----------------------------------------------------------------------
# Global variables
# ----------------------------------------------------------------------
g_width = 800
g_height = 600
g_background_color = (128,128,128)
gTiles = []

def init_tiles():
    gTiles.append (Tile(id=1, orient=0, pos=( 0, 0), paths=["NS", "EW"]))
    gTiles.append (Tile(id=2, orient=0, pos=( 1, 0), paths=["SN" ]))
    gTiles.append (Tile(id=3, orient=0, pos=( 2, 0), paths=["WE" ]))
    gTiles.append (Tile(id=3, orient=0, pos=( 0, 1), paths=["SE" ]))
    gTiles.append (Tile(id=3, orient=0, pos=( 1, 1), paths=["EW" ]))
    gTiles.append (Tile(id=3, orient=0, pos=( 2, 1), paths=["SW" ]))
    gTiles.append (Tile(id=3, orient=0, pos=( 0, 2), paths=["NE" ]))
    gTiles.append (Tile(id=3, orient=0, pos=( 1, 2), paths=["EW" ]))
    gTiles.append (Tile(id=3, orient=0, pos=( 2, 2), paths=["NW" ]))
    gTiles.append (Tile(id=3, orient=0, pos=( 3, 3), paths=["SE", "NW" ]))



def print_tiles():
    for tile in gTiles:
        print (tile)

# ----------------------------------------------------------------------
def randomColor():
    color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )
    return color

# ----------------------------------------------------------------------
def render(screen):
    """Generate and draw one random graphic."""
    # Clear the screen
    screen.fill(g_background_color)
    screenW, screenH = screen.get_size()
    maxR = 50

    for tile in gTiles:
        draw_tile(screen, tile)

    # for _ in range(10):
    #     x = random.randint(0, screenW-2*maxR) + maxR
    #     y = random.randint(0, screenH-2*maxR) + maxR
    #     clr = randomColor()
    #     r = random.randint(5, maxR)

    #     pygame.draw.circle(screen, clr, (x, y), r, )
    #     pygame.draw.circle(screen,(0,0,0),(x,y),r,width=1)

    # Make the drawing visible
    pygame.display.flip()

# ----------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------

def main():
    init_tiles()
    print_tiles()

    pygame.init()

    screen = pygame.display.set_mode((g_width, g_height))
    pygame.display.set_caption("Graphics Drawing Explorer")

    # Draw the initial graphic
    render(screen)

    running = True

    while running:

        # --------------------------------------------------------------
        # Wait for an event
        # --------------------------------------------------------------
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                # ESC quits the program
                if event.key == pygame.K_ESCAPE:
                    running = False

                # SPACE generates a new graphic
                elif event.key == pygame.K_SPACE:
                    render(screen)

    pygame.quit()


# ----------------------------------------------------------------------
# Program entry point
# ----------------------------------------------------------------------

if __name__ == "__main__":
    main()

