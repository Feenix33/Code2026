import argparse
import sys

from definition_parser import DefinitionParser
from config_builder import build_configuration
from pages.factory import PageFactory
from engine import BookletEngine

import logging

# from engine import BookletEngine

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Pocket: Turn text and images into a PDF booklet.")
    # parser.add_argument("manifest", default="pocket.p8", help="Path to your input configuration file (e.g., booklet.p8)")
    parser.add_argument("-o", "--output", default="output.pdf", help="Name of the output PDF file")
    parser.add_argument("-i", "--input", default="pocket.p8", help="Definitionuration definition file")
    parser.add_argument(
        "manifest",
        nargs="?",  # 0 or 1 values allowed
        default="pocket.p8",  # Used if not provided
        help="Path to your input configuration file (default: pocket.p8)"
    )

    args = parser.parse_args()

    # 0. Some debug testing
    strRegPgs = "Registered pages:" + str(PageFactory._pages.keys())
    logger.debug(strRegPgs)

    # 1. Parse the .p8 file
    try:
        dfnParser = DefinitionParser()
        bookletDefinition = dfnParser.parse_file(args.manifest)
    except Exception as e:
        print(f"Error reading definition file: {e}", file=sys.stderr)
        sys.exit(1)

    # 2 Translate definition into configuration and style
    cfgBooklet = build_configuration(bookletDefinition)

    # 3. Build the PDF
    # print(f"Building your booklet from '{args.manifest}'...")
    engine = BookletEngine(cfgBooklet)
    engine.build()

    logger.debug ('Fini')

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(filename)s:%(lineno)d "
               "%(funcName)s() - %(message)s"
    )
    # logging.getLogger("pages").setLevel(logging.CRITICAL + 1)

if __name__ == "__main__":
    main()

