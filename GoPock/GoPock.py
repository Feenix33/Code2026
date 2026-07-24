"""
GoPock.py
Entry point for booklet creation.
"""
import pprint
import sys
import argparse
import os

from booklet import Booklet
from page import PageFactory
import page_word
import page_text
import page_lines
import page_grid
import page_checklist
import page_weekly
import page_title
import page_tracker
import page_montrack
from utils import read_page_specs, build_book

# Version constant
VERSION = "1.0.0"

"""
Main TODO:
- Dice page
- daily page
- spreadsheet or expense tracker
- title page

- all pages should do a setLineSpec() as part of the base class
- tracker check if no arguments, should have default blank lines
- weekly tracker should have day offset like monthly tracker
- simplify the title font parameters
- check that we use title font for title, then switch to standard font for the rest of the page
- help guide


Hints:
================================================================================================
Reportlab units are in points (1/72 inch)
from reportlab.lib.units import inch
x_coordinate = 1.5 * inch 
================================================================================================
Print current function name
import sys
def my_awesome_function():
    func_name = sys._getframe().f_code.co_name
    print(f"Currently executing: {func_name}")

    import sys
    print(f"DEBUG {sys._getframe().f_code.co_name}({self.debugID}) ")
================================================================================================
Line number
import inspect
{inspect.currentframe().f_lineno}
================================================================================================
strftime
Years & Months: 
%Y (4-digit)
%y (2-digit)
%B (full name)
%b (abbr.)
%m (zero-padded)

Days & Weeks
%d (day)
%A/%a (weekday name)
%j (day of year)
%w = Weekday symbol (custom)

Time & Zone:
%H/%I (24/12h),
%M (min)
%S (sec)
%p (AM/PM)
%z (UTC offset)
%Z (timezone)

Locales:
%c (date/time)
%x (date)
%X (time)

"""


def print_help():
    """Print help message for GoPock."""
    help_text = """GoPock - Pocket Booklet Creator
Version: {}

USAGE:
    GoPock.py [INPUT_FILE] [OUTPUT_FILE]

ARGUMENTS:
    INPUT_FILE      Input specification file (default: input.txt)
    OUTPUT_FILE     Output PDF filename (default: GoPock.pdf)
                    If OUTPUT_FILE does not end with .pdf, it will be added.

FLAGS:
    -h, --help      Show this help message and exit
    -v, --version   Show version information and exit

DESCRIPTION:
    GoPock creates customized pocket booklets from a specification file.
    The input file uses key=value pairs to define pages and booklet settings.

INPUT FILE FORMAT:
    - Lines starting with # are comments and are ignored
    - Page types: blank, text, title, grid, lines, checklist, tracker, montrack
    - Booklet settings: addPages, margin, useRecipeAbbreviations, nameOut
    - Page style defaults: font.name, font.size, font.color, colorLine, etc.

EXAMPLES:
    GoPock.py                           # Use input.txt, output to GoPock.pdf
    GoPock.py recipes.txt               # Use recipes.txt, output to GoPock.pdf
    GoPock.py input.txt output.pdf      # Use input.txt, output to output.pdf
    GoPock.py --help                    # Show this help message
    GoPock.py --version                 # Show version information

For more information, see help.txt in the GoPock folder.
""".format(VERSION)
    print(help_text)


def main():
    parser = argparse.ArgumentParser(
        prog='GoPock',
        add_help=False,  # We'll handle help manually
        description='Create customized pocket booklets'
    )
    
    parser.add_argument(
        'input_file',
        nargs='?',
        default='input.txt',
        help='Input specification file (default: input.txt)'
    )
    parser.add_argument(
        'output_file',
        nargs='?',
        default='GoPock.pdf',
        help='Output PDF filename (default: GoPock.pdf)'
    )
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='Show version information and exit'
    )
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help='Show help message and exit'
    )
    
    args = parser.parse_args()
    
    # Handle version flag
    if args.version:
        print(f"GoPock version {VERSION}")
        sys.exit(0)
    
    # Handle help flag
    if args.help:
        print_help()
        sys.exit(0)
    
    # Check if input file exists
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Ensure output file ends with .pdf
    output_file = args.output_file
    if not output_file.lower().endswith('.pdf'):
        output_file += '.pdf'
    
    booklet = Booklet()
    specs = read_page_specs(args.input_file)
    
    # Override the output filename from the config if command-line argument was provided
    booklet.config.nameOut = output_file
    
    build_book(booklet, specs, PageFactory)
    booklet.render()


if __name__ == '__main__':
    main()
