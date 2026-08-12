"""Program entry point and Pygame event loop."""
import pygame
from constants import gSCREEN_WIDTH,gSCREEN_HEIGHT,gWRITE_SPRITE_SHEET
from game import Game
from sprite_generator import create_sprite_sheet,load_tile_sprites

def main():
    pygame.init()
    screen=pygame.display.set_mode((gSCREEN_WIDTH,gSCREEN_HEIGHT))
    pygame.display.set_caption("Tile Loop Game - Version 1")
    sheet=create_sprite_sheet(gWRITE_SPRITE_SHEET)
    game=Game(screen,load_tile_sprites(sheet))
    clock=pygame.time.Clock()
    running=True
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==pygame.KEYDOWN:
                if game.handle_key(event.key)=="quit": running=False
            elif event.type==pygame.MOUSEMOTION:
                game.handle_mouse_motion(event.pos)
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if game.handle_mouse_button(event.pos)=="quit": running=False
        game.draw()
        clock.tick(60)
    pygame.quit()

if __name__=="__main__":
    main()
