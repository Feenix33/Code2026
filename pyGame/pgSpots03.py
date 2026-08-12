"""
Spots
Draw random spots
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import random
import math


# ----------------------------------------------------------------------
# Global variables
# ----------------------------------------------------------------------

g_width = 800
g_height = 600
g_background_color = (128,128,128)

g_circle_count = 600
g_min_radius = 5
g_max_radius = 80


# ----------------------------------------------------------------------
def randomColor():
    color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )
    return color

# ----------------------------------------------------------------------
def get_max_radius(screen, center_x, center_y, bkgrnd, maxR):
    # The background color we are ignoring
    BACKGROUND_COLOR = bkgrnd

    screen_w, screen_h = screen.get_size()
    radius = 1

    while True:
        # 1. Quick boundary check: stop if the circle hits the edge of the window
        if (
            center_x - radius < 0
            or center_x + radius >= screen_w
            or center_y - radius < 0
            or center_y + radius >= screen_h
        ):
            return radius - 1

        # 2. Calculate how many points to sample based on the circumference
        # Dynamic steps ensure we don't skip pixels as the circle grows
        circumference = 2 * math.pi * radius
        steps = max(8, int(circumference))

        # 3. Scan the perimeter of the current radius
        for i in range(steps):
            angle = (2 * math.pi * i) / steps
            check_x = int(center_x + radius * math.cos(angle))
            check_y = int(center_y + radius * math.sin(angle))

            # Read the pixel
            pixel = screen.get_at((check_x, check_y))

            # If it's NOT neutral grey, a collision occurred!
            if (pixel.r, pixel.g, pixel.b) != BACKGROUND_COLOR:
                return radius - 1  # Return the last safe radius

        # Expand the circle for the next loop iteration
        if radius == maxR:
            return radius
        radius += 1

# ----------------------------------------------------------------------
def drawSpot(screen, bkgrnd, maxR):
    screenW, screenH = screen.get_size()

    x = random.randint(0, screenW)
    y = random.randint(0, screenH)
    clr = randomColor()
    r = get_max_radius(screen, x, y, bkgrnd, maxR)

    if r > 0:
        pygame.draw.circle(screen, clr, (x, y), r, )
        pygame.draw.circle(screen,(0,0,0),(x,y),r,width=1)
    


def render_graphics(screen):
    """Generate and draw one random graphic."""
    # Clear the screen
    screen.fill(g_background_color)

    # Draw random circles
    for _ in range(g_circle_count):
        drawSpot(screen, g_background_color, g_max_radius)

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