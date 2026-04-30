"""
Generate Lorem Ipsum text and write to a file.
Uses the lorem library to generate configurable paragraphs.
"""

import lorem

# Configuration variables
NUM_PARAGRAPHS = 10           # Number of paragraphs to generate
OUTPUT_FILENAME = "input.txt"  # Output file name


def generate_lorem_text(num_paragraphs):
    """
    Generate lorem ipsum text with specified number of paragraphs.
    
    Args:
        num_paragraphs (int): Number of paragraphs to generate
        words_per_paragraph (int): Approximate number of words per paragraph
    
    Returns:
        str: Generated lorem ipsum text
    """
    paragraphs = []
    for i in range(num_paragraphs):
        # Generate a paragraph of text
        paragraph = lorem.paragraph()
        # Add paragraph number to the beginning
        numbered_paragraph = f"{i+1}. {paragraph}"
        paragraphs.append(numbered_paragraph)
    
    return "\n".join(paragraphs)


def write_to_file(text, filename):
    """
    Write text to a file.
    
    Args:
        text (str): Text to write
        filename (str): Output filename
    """
    try:
        with open(filename, 'w') as f:
            f.write(text)
        print(f"Successfully wrote {len(text)} characters to '{filename}'")
    except IOError as e:
        print(f"Error writing to file '{filename}': {e}")


def main():
    """Main function to generate and save lorem ipsum text."""
    print(f"Generating {NUM_PARAGRAPHS} paragraphs of Lorem Ipsum...")
    
    # Generate the text
    lorem_text = generate_lorem_text(NUM_PARAGRAPHS)
    write_to_file(lorem_text, OUTPUT_FILENAME)
    print(f"Output saved to: {OUTPUT_FILENAME}")

if __name__ == '__main__':
    main()

