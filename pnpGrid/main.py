"""
main.py
Main entry point for the program.
This program demonstrates three important ideas:
1. Generate a grid.
2. Display the grid.
3. Keep those two jobs independent.
"""
from args import get_arguments
from grid import GridGenerator
from pygame_renderer import PygameRenderer

def main():
    """
    Main program.
    """
    # Read the command-line arguments.
    args = get_arguments()
    print(f"Input : {args.input}")
    print(f"Output: {args.output}")
    #
    # Create the grid.
    #
    # Nothing here knows how the grid will be displayed.
    #
    generator = GridGenerator(width=15, height=15)
    #
    # Create a renderer.
    #
    # Later we could replace this with:
    #
    # renderer = ReportLabRenderer(...)
    #
    # without changing the GridGenerator.
    #
    renderer = PygameRenderer(cell_size=40)
    renderer.render(generator)
if __name__ == "__main__":
    main()
