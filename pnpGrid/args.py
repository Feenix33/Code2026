"""
Command-line argument processing.
"""
import argparse
from pathlib import Path
VERSION = "1.0"
def get_arguments():
    """
    Read the command-line arguments.
    Rules:
    program
        input.dat
        output.pdf
    program map.dat
        input = map.dat
        output = map.pdf
    program map.dat mymap.pdf
        input = map.dat
        output = mymap.pdf
    """
    parser = argparse.ArgumentParser(
        description="Simple Grid Demo"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="input.dat",
        help="Input filename"
    )
    parser.add_argument(
        "output",
        nargs="?",
        help="Output filename"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )
    args = parser.parse_args()
    #
    # If the user didn't supply an output filename,
    # create one from the input filename.
    #
    if args.output is None:
        path = Path(args.input)
        args.output = path.with_suffix(".pdf")
    return args
