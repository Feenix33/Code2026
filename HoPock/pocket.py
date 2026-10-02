import argparse
import sys
import logging

from definition_parser import DefinitionParser
from config_builder import build_configuration
#from pages.factory import PageFactory
from engine import BookletEngine
from predefine import parse_start_date, build_file_definition, build_manual_definition, build_daily_definition, build_weekly_definition
from pathlib import Path

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        mode, source, output_file = resolve_input_output(args)

        dfn_parser = DefinitionParser()

        if mode == "definition":
            booklet_definition = dfn_parser.parse_file(source)

        elif mode == "file":
            definition_lines = build_file_definition(source)
            booklet_definition = dfn_parser.parse_lines(
                definition_lines
            )

        elif mode == "manual":
            definition_lines = build_manual_definition()
            booklet_definition = dfn_parser.parse_lines(
                definition_lines
            )

        elif mode == "daily":
            start_date = parse_start_date(source)
            definition_lines = build_daily_definition(start_date)
            booklet_definition = dfn_parser.parse_lines(
                definition_lines
            )

        elif mode == "weekly":
            start_date = parse_start_date(source)
            definition_lines = build_weekly_definition(start_date)
            booklet_definition = dfn_parser.parse_lines(
                definition_lines
            )

        cfg_booklet = build_configuration(booklet_definition)
        cfg_booklet.output = output_file

        engine = BookletEngine(cfg_booklet)
        engine.build()

    except Exception as e:
        logger.exception("Failed to build booklet")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(filename)s:%(lineno)d "
               "%(funcName)s() - %(message)s"
    )
    # logging.getLogger("pages").setLevel(logging.CRITICAL + 1)

def create_argument_parser():
    parser = argparse.ArgumentParser(
        description="Pocket: Turn text and images into a PDF booklet."
    )

    parser.add_argument(
        "manifest",
        nargs="?",
        default=None,
        help="Input definition file (e.g., planner.p8)"
    )

    parser.add_argument(
        "-i", "--input",
        default=None,
        help="Input definition file (default: pocket.p8)"
    )

    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output PDF filename"
    )

    modes = parser.add_mutually_exclusive_group()

    modes.add_argument(
        "--manual",
        action="store_true",
        help="Generate the user manual"
    )

    modes.add_argument(
        "--daily",
        nargs="?",
        const="today",
        metavar="DATE",
        help="Generate a daily booklet (optional date: YYYY-MM-DD)"
    )

    modes.add_argument(
        "--weekly",
        nargs="?",
        const="today",
        metavar="DATE",
        help="Generate a weekly booklet (optional date: YYYY-MM-DD)"
    )

    modes.add_argument(
        "--file",
        metavar="FILENAME",
        help="Generate a text booklet from a file"
    )

    return parser

def resolve_input_output(args):
    """
    Determine the input source and output filename.

    Returns:
        mode: Selected operation
        input_file: Input filename, if applicable
        output_file: Output PDF filename
    """

    # Built-in booklet modes.
    if args.manual:
        return "manual", None, args.output or "manual.pdf"

    if args.daily is not None:
        return "daily", args.daily, args.output or "daily.pdf"

    if args.weekly is not None:
        return "weekly", args.weekly, args.output or "weekly.pdf"

    if args.file is not None:
        filename = Path(args.file)
        output = args.output or str(filename.with_suffix(".pdf"))
        return "file", str(filename), output

    # Normal definition-file mode.
    input_file = args.input or args.manifest or "pocket.p8"

    # Explicit -o wins; otherwise derive the output name.
    output_file = args.output or str(
        Path(input_file).with_suffix(".pdf")
    )

    return "definition", input_file, output_file

# ======================================================================================================

if __name__ == "__main__":
    main()

