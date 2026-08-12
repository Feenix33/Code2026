"""
Packing circles pygame demonstrator
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import random

# globals
def game_loop():
    pygame.init()
    # screen = pygame.display.set_mode((1280, 720))
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True

    pygame.display.set_caption("Grid Demo")
    running = True
    oneshot = True
 
    screen.fill("purple")

    while running:
        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Keyboard input
            elif event.type == pygame.KEYDOWN:
                # esc quits
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    pass

        # fill the screen with a color to wipe away anything from last frame
        # screen.fill("purple")

        # RENDER YOUR GAME HERE
        for j in range(1):
            cr = random.randint(0,255)
            cg = random.randint(0,255)
            cb = random.randint(0,255)
            # apos = pygame.Vector2(100*(j+1), 75*(j+1))
            apos = pygame.Vector2(random.randint(0, 800), random.randint(0, 600))
            radius = random.randint(10,50)
            pygame.draw.circle(screen, pygame.Color(cr,cg,cb), apos, radius)

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
        pygame.time.wait(100)

    pygame.quit()


def main():
    game_loop()


if __name__ == "__main__":
    main()