import argparse
import sys
from archive.config import parse_p8_file
from engine import BookletEngine

def main():
    parser = argparse.ArgumentParser(description="Pocket: Turn text and images into a PDF booklet.")
    parser.add_argument("manifest", default="pocket.p8", help="Path to your input configuration file (e.g., booklet.p8)")
    parser.add_argument("-o", "--output", default="output.pdf", help="Name of the output PDF file")
    parser.add_argument("-i", "--input", default="pocket.p8", help="Configuration definition file")
    
    args = parser.parse_args()
    
    # 1. Parse the .p8 file
    try:
        pages_to_render = parse_p8_file(args.manifest)
    except Exception as e:
        print(f"Error reading manifest: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 2. Build the PDF
    print(f"Building your booklet from '{args.manifest}'...")
    engine = BookletEngine(pages_to_render, args.output)
    engine.build()
    print(f"Success! Saved to {args.output}")

if __name__ == "__main__":
    main()

