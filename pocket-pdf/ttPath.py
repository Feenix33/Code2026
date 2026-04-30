"""
Function to read and print a file to the console.
"""


def print_file(filepath):
    """
    Read a file and print its contents to the console.
    
    Args:
        filepath (str): The path and filename of the file to print
    
    Returns:
        None
    """
    try:
        with open(filepath, 'r', encoding='latin-1') as f:
            content = f.read()
            print(content)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except IOError as e:
        print(f"Error reading file '{filepath}': {e}")


def main():
    """Test the print_file function."""
    # Hardcoded path and filename
    filepath = 'Food/CornBread.txt'
    
    print(f"Reading file: {filepath}\n")
    print_file(filepath)


if __name__ == '__main__':
    main()