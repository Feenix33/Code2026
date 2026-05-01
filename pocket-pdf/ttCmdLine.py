import sys
import os


def ProcessArguments(args):
    """
    Parse command line arguments and return input and output filenames.
    
    Args:
        args: list of command line arguments (typically sys.argv[1:])
        
    Returns:
        tuple: (inFilename, outFilename)
        
    Behavior:
        - Default: inFilename="input.txt", outFilename="output.pdf"
        - Supports positional arguments: program input.txt output.pdf
        - Supports flags: program -i input.txt -o output.pdf
        - Output filename must end in .pdf
        - If output not specified, uses input filename with truncated extension + .pdf
    """
    inFilename = "input.txt"
    outFilename = None
    output_explicitly_set = False
    
    i = 0
    while i < len(args):
        if args[i] == "-i" and i + 1 < len(args):
            # Flag: -i for input filename
            inFilename = args[i + 1]
            i += 2
        elif args[i] == "-o" and i + 1 < len(args):
            # Flag: -o for output filename
            outFilename = args[i + 1]
            output_explicitly_set = True
            i += 2
        elif not args[i].startswith("-"):
            # Positional arguments
            if inFilename == "input.txt" and not output_explicitly_set:
                # First positional arg is input
                inFilename = args[i]
            elif outFilename is None:
                # Second positional arg is output
                outFilename = args[i]
                output_explicitly_set = True
            i += 1
        else:
            # Unknown flag, skip
            i += 1
    
    # If no output filename specified, derive it from input filename or use default
    if outFilename is None:
        # If input wasn't changed from default, use default output
        if inFilename == "input.txt":
            outFilename = "output.pdf"
        else:
            # Remove extension from input and add .pdf
            name_without_ext = os.path.splitext(inFilename)[0]
            outFilename = name_without_ext + ".pdf"
    else:
        # Ensure output filename ends with .pdf
        if not outFilename.lower().endswith(".pdf"):
            outFilename += ".pdf"
    
    return inFilename, outFilename


def main():
    # Pass command line arguments to ProcessArguments
    inFilename, outFilename = ProcessArguments(sys.argv[1:])
    print(f"Input file: {inFilename}")
    print(f"Output file: {outFilename}")


if __name__ == "__main__":
    main()
