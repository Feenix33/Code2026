"""
Pygame renderer.
"""
import pygame
from renderer import Renderer
#from terrain_style import TerrainStyleSet
from styles.screen import STYLE
from gamemap import GameMap

class PygameRenderer(Renderer):
    def __init__(self, cell_size=40):
        self.cell_size = cell_size

    def render(self, generator):
        # Create the initial map
        game_map = generator.generate()
        rows = game_map.height #len(grid)
        cols = game_map.width #len(grid[0])
        width = cols * self.cell_size
        height = rows * self.cell_size
        pygame.init()
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Grid Demo")
        running = True
        styles = STYLE #TerrainStyleSet()
        while running:
            #
            # Handle keyboard and window events.
            #
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Keyboard input
                elif event.type == pygame.KEYDOWN:
                    # esc quits
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        #grid = generator.generate()
                        game_map = generator.generate()
            #
            # Fill the window with white.
            #
            screen.fill((255, 255, 255))
            #
            # Draw every cell.
            #
            for row in range(rows):
                for col in range(cols):
                    x = col * self.cell_size
                    y = row * self.cell_size
                    rect = pygame.Rect(
                        x,
                        y,
                        self.cell_size,
                        self.cell_size
                    )
                    #
                    # Draw the cell border.
                    #
                    pygame.draw.rect(
                        screen,
                        (0, 0, 0),
                        rect,
                        1
                    )
                    cell = game_map.cells[row][col]
                    style = styles.get(cell.terrain)
                    pygame.draw.rect(screen,
                                     style.fill_color,
                                     rect.inflate(-4, -4)
                                     )
            pygame.display.flip()
        pygame.quit()
