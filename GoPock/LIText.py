"""
Lorem Ipsum Text generator
Created by Google Gemini prompts
"""
import argparse
import os
import random
import sys
import lorem


def get_lorem_words():
    """Generates a list of clean words from a lorem sentence."""
    # lorem.sentence() returns a string. We split it and clean trailing punctuation.
    raw_words = lorem.sentence().split()
    return [word.rstrip(",.") for word in raw_words if word]


def generate_text(args):
    output_lines = []

    # 1. Generate Title if requested
    if args.title and args.title > 0:
        title_words = []
        while len(title_words) < args.title:
            title_words.extend(get_lorem_words())

        # Slice to exact length and apply Title Case
        title_str = " ".join(title_words[: args.title]).title()
        output_lines.append(title_str)
        # Always add a gap after a title
        output_lines.append("")

    # 2. Generate Paragraphs
    for p_idx in range(1, args.paragraphs + 1):
        paragraph_sentences = []

        # Determine sentence count for this paragraph based on spread (-sd)
        s_count = args.sentences + random.randint(-args.s_spread, args.s_spread)
        s_count = max(1, s_count)

        for _ in range(s_count):
            # Determine word count for this sentence based on spread (-wd)
            w_count = args.words + random.randint(-args.w_spread, args.w_spread)
            w_count = max(1, w_count)

            # Gather enough clean words to satisfy the sentence length
            words = get_lorem_words()
            while len(words) < w_count:
                words.extend(get_lorem_words())

            # Format the sentence nicely (Capitalized first letter, ending with a period)
            sentence_str = " ".join(words[:w_count]).capitalize() + "."
            paragraph_sentences.append(sentence_str)

        # Join sentences to form the paragraph
        paragraph_text = " ".join(paragraph_sentences)

        # Apply paragraph numbering (-n)
        if args.number:
            paragraph_text = f"{p_idx}. {paragraph_text}"

        output_lines.append(paragraph_text)

        # Apply blank lines between paragraphs (-l)
        if args.line and p_idx < args.paragraphs:
            output_lines.append("")

    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate dummy text files using Lorem Ipsum."
    )

    # Positional argument with a default value
    parser.add_argument(
        "outputfile",
        nargs="?",
        default="output.txt",
        help="The file to create (default: output.txt)",
    )

    # Optional arguments
    parser.add_argument(
        "-p",
        "--paragraphs",
        type=int,
        default=3,
        help="Number of paragraphs to generate (default: 3)",
    )
    parser.add_argument(
        "-s",
        "--sentences",
        type=int,
        default=4,
        help="Base number of sentences per paragraph (default: 4)",
    )
    parser.add_argument(
        "-sd",
        "--s-spread",
        type=int,
        default=0,
        help="Plus/minus random spread for sentence count (default: 0)",
    )
    parser.add_argument(
        "-w",
        "--words",
        type=int,
        default=10,
        help="Base number of words per sentence (default: 10)",
    )
    parser.add_argument(
        "-wd",
        "--w-spread",
        type=int,
        default=0,
        help="Plus/minus random spread for word count (default: 0)",
    )
    parser.add_argument(
        "-n",
        "--number",
        action="store_true",
        help="Number each paragraph starting at 1",
    )
    parser.add_argument(
        "-l",
        "--line",
        action="store_true",
        help="Add a blank line between paragraphs",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=int,
        default=0,
        metavar="WORDS",
        help="Create a Title Case title with # words (default: 0/None)",
    )

    args = parser.parse_args()

    # Overwrite check
    if os.path.exists(args.outputfile):
        try:
            response = (
                input(f"File '{args.outputfile}' already exists. Overwrite? (y/n): ")
                .strip()
                .lower()
            )
            if response not in ["y", "yes"]:
                print("Operation cancelled. File not overwritten.")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(0)

    # Generate and write content
    try:
        content = generate_text(args)
        with open(args.outputfile, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        print(f"Successfully generated text in '{args.outputfile}'.")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
