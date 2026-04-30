"""
Text scrubbing function that replaces strings based on a lookup table.
"""


def scrub(line):
    """
    Replace all occurrences of strings in the line based on a data structure
    of string pairs. The first string in each pair is replaced with the second.
    
    Args:
        line (str): The text line to process
    
    Returns:
        str: The scrubbed text with all replacements made
    """
    # Data structure: list of tuples with (original_string, replacement_string)
    # Strings can contain spaces
    replacements = [
        ("old text", "new text"),
        ("find this", "replace with this"),
        ("example string", "substitution"),
        # Add more pairs as needed
    ]
    
    result = line
    for original, replacement in replacements:
        result = result.replace(original, replacement)
    
    return result


def main():
    """Test the scrub function."""
    test_line = "This is old text and find this in the example string here."
    print(f"Original: {test_line}")
    
    scrubbed = scrub(test_line)
    print(f"Scrubbed: {scrubbed}")


if __name__ == '__main__':
    main()
