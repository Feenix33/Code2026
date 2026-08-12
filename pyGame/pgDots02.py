"""
Dots
Add some structure to the random drawing and have a different drawing routine
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import random


# ----------------------------------------------------------------------
# Global variables
# ----------------------------------------------------------------------

g_width = 800
g_height = 600
g_background_color = (240, 240, 240)

g_circle_count = 100
g_min_radius = 5
g_max_radius = 40


# ----------------------------------------------------------------------
# Render the graphics
# ----------------------------------------------------------------------

def render_graphics(screen):
    """Generate and draw one random graphic."""

    # Clear the screen
    screen.fill(g_background_color)

    # Draw random circles
    for _ in range(g_circle_count):
        x = random.randint(0, g_width)
        y = random.randint(0, g_height)
        radius = random.randint(g_min_radius, g_max_radius)

        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

        pygame.draw.circle(
            screen,
            color,
            (x, y),
            radius,
        )

    # Make the drawing visible
    pygame.display.flip()


# ----------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------

def main():
    pygame.init()

    screen = pygame.display.set_mode((g_width, g_height))
    pygame.display.set_caption("Graphics Drawing Explorer")

    # Draw the initial graphic
    render_graphics(screen)

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
                    render_graphics(screen)

    pygame.quit()


# ----------------------------------------------------------------------
# Program entry point
# ----------------------------------------------------------------------

if __name__ == "__main__":
    main()