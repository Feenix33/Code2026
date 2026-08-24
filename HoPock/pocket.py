import argparse
import sys

from definition_parser import DefinitionParser
from engine import BookletEngine

def main():
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
    
    # 1. Parse the .p8 file
    try:
        cfgParser = DefinitionParser()
        pages_to_render = cfgParser.parse_file(args.manifest)
        for entry in pages_to_render:
            print (entry)
    except Exception as e:
        print(f"Error reading definition file: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Resolve any overrides from command line arguments and input cfg file
    # TODO add here
        
    # 3. Build the PDF
    print(f"Building your booklet from '{args.manifest}'...")
    engine = BookletEngine(pages_to_render)
    # engine.build()
    print(f"Success! Saved to {args.output}")

if __name__ == "__main__":
    main()

