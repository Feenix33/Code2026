"""
ReportLab Primitive Commands DSL to PDF Converter
=================================================

This program implements a custom domain-specific language (DSL) interpreter
that reads line-by-line text commands from a text file and maps them directly 
to low-level ReportLab Canvas methods (Chapters 1-4 of the ReportLab User Guide).

Features Implemented:
---------------------
1. Command Line Interface:
   - Command-line argument parsing with default input and output files.
   - Dynamic output filename generation based on input name if output is omitted.
   - Extension stripping and forcing '.pdf' (e.g., 'test.08.05.A.gg' -> 'test.08.05.A.pdf').
   - Built-in `--help` / `-h` flag with detailed usage instructions.

2. Document & Page Control:
   - Target Document: Standard Letter-sized PDF (612 x 792 points).
   - `showPage()`: Flushes current page graphics and initiates a new page buffer.

3. Line Styles & Color Controls:
   - `setLineWidth(width)`: Configures stroke line width in points.
   - `setDash([on, off])`: Controls line dash patterns (or resets to solid line).
   - `strokeColor(color)` / `fillColor(color)`: Accepts named ReportLab colors 
     (e.g., 'red', 'blue') or Hex color values (e.g., '#2C3E50' or #2C3E50).

4. Vector Paths & Geometry Primitives:
   - Primitive shapes: `line(x1, y1, x2, y2)`, `rect(x, y, w, h, stroke, fill)`, 
     and `circle(x, y, r, stroke, fill)`.
   - Freeform vector paths: State-managed `beginPath()`, `moveTo(x, y)`, `lineTo(x, y)`, 
     `closePath()`, and `drawPath(stroke, fill)`.

5. Typography & Text Alignment:
   - `setFont(name, size)`: Configures PDF font face and size.
   - Positioned string rendering: `drawString(x, y, text)` (left-aligned), 
     `drawCentredString(x, y, text)` (center-aligned), and `drawRightString(x, y, text)` (right-aligned).


Leter size = (612, 792)
"""

import sys
import re
import os
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def sanitize_line(line):
    """
    Strips inline comments (anything following '#') unless enclosed within quotes.
    Also trims whitespace.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return ""

    in_quotes = False
    quote_char = None
    clean_chars = []

    for char in line:
        if char in ('"', "'"):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
            clean_chars.append(char)
        elif char == '#' and not in_quotes:
            break  # Strip inline comment
        else:
            clean_chars.append(char)

    return "".join(clean_chars).strip()


def parse_color(color_str):
    """
    Converts a DSL color string into a valid ReportLab Color object.
    Supports Hex strings ("#2C3E50" or #2C3E50) and built-in names ("red").
    """
    color_str = color_str.strip().strip('"').strip("'")
    if color_str.startswith("#"):
        return colors.HexColor(color_str)
    if hasattr(colors, color_str):
        return getattr(colors, color_str)
    raise ValueError(f"Unknown color specifier: {color_str}")


def parse_args_string(args_str):
    """
    Extracts function arguments from a raw string while respecting quotes.
    """
    if not args_str.strip():
        return []
    pattern = r'(?:[^\s,"]|"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\')+'
    return re.findall(pattern, args_str)


def parse_and_execute_line(c, state, line):
    """
    Parses a single DSL command string and invokes the corresponding ReportLab canvas call.
    """
    line = sanitize_line(line)
    if not line:
        return

    if "(" in line and line.endswith(")"):
        cmd = line[:line.find("(")].strip()
        raw_args = line[line.find("(")+1:-1].strip()
    else:
        cmd = line
        raw_args = ""

    args = [a.strip() for a in parse_args_string(raw_args)]

    # Page Control
    if cmd == "showPage":
        c.showPage()

    # Line Styles
    elif cmd == "setLineWidth":
        c.setLineWidth(float(args[0]))

    elif cmd == "setDash":
        if len(args) == 0:
            c.setDash()
        elif len(args) == 2:
            c.setDash(float(args[0]), float(args[1]))

    # Colors
    elif cmd == "strokeColor":
        c.setStrokeColor(parse_color(args[0]))

    elif cmd == "fillColor":
        c.setFillColor(parse_color(args[0]))

    # Path Vector Operations
    elif cmd == "beginPath":
        state["active_path"] = c.beginPath()

    elif cmd == "moveTo":
        x, y = float(args[0]), float(args[1])
        if state["active_path"]:
            state["active_path"].moveTo(x, y)
        else:
            c.moveTo(x, y)

    elif cmd == "lineTo":
        x, y = float(args[0]), float(args[1])
        if state["active_path"]:
            state["active_path"].lineTo(x, y)
        else:
            c.lineTo(x, y)

    elif cmd == "closePath":
        if state["active_path"]:
            state["active_path"].close()

    elif cmd == "drawPath":
        stroke = int(args[0]) if len(args) > 0 else 1
        fill = int(args[1]) if len(args) > 1 else 0
        if state["active_path"]:
            c.drawPath(state["active_path"], stroke=stroke, fill=fill)
            state["active_path"] = None
        else:
            raise ValueError("drawPath called without an active beginPath()")

    # Primitive Shapes
    elif cmd == "line":
        x1, y1, x2, y2 = [float(a) for a in args[:4]]
        c.line(x1, y1, x2, y2)

    elif cmd == "rect":
        x, y, w, h = [float(a) for a in args[:4]]
        stroke = int(args[4]) if len(args) > 4 else 1
        fill = int(args[5]) if len(args) > 5 else 0
        c.rect(x, y, w, h, stroke=stroke, fill=fill)

    elif cmd == "circle":
        x, y, r = [float(a) for a in args[:3]]
        stroke = int(args[3]) if len(args) > 3 else 1
        fill = int(args[4]) if len(args) > 4 else 0
        c.circle(x, y, r, stroke=stroke, fill=fill)

    # Typography & Alignment
    elif cmd == "setFont":
        font_name = args[0].strip('"').strip("'")
        size = float(args[1])
        c.setFont(font_name, size)

    elif cmd in ("drawString", "drawCentredString", "drawRightString"):
        x = float(args[0])
        y = float(args[1])
        text = args[2].strip('"').strip("'")

        if cmd == "drawString":
            c.drawString(x, y, text)
        elif cmd == "drawCentredString":
            c.drawCentredString(x, y, text)
        elif cmd == "drawRightString":
            c.drawRightString(x, y, text)

    else:
        raise ValueError(f"Unrecognized command: {cmd}")


def convert_txt_to_pdf(input_txt_path, output_pdf_path):
    """
    Main processing loop. Reads DSL text file line-by-line and outputs PDF.
    """
    c = canvas.Canvas(output_pdf_path, pagesize=letter)
    state = {"active_path": None}

    try:
        with open(input_txt_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                try:
                    parse_and_execute_line(c, state, line)
                except Exception as e:
                    print(f"Error on line {line_num}: {e}")
    except FileNotFoundError:
        print(f"Error: Input file '{input_txt_path}' not found.")
        sys.exit(1)

    c.save()
    print(f"PDF successfully created: {output_pdf_path}")


def create_sample_file_if_missing(input_file):
    """
    Generates a default test script if the input file does not exist.
    """
    sample_dsl = """# === PAGE 1 ===
setFont("Helvetica-Bold", 16)
drawString(50, 750, "Page 1: Paths & Line Styles")

# Dashed thick line
setLineWidth(3)
setDash(6, 3)
strokeColor("#E74C3C")
line(50, 700, 550, 700)

# Reset dash pattern to solid line
setDash()
setLineWidth(1.5)
strokeColor("#2980B9")
fillColor("#3498DB")

# Custom Polygon Path (Triangle)
beginPath()
moveTo(100, 500)
lineTo(200, 600)
lineTo(300, 500)
closePath()
drawPath(1, 1)

# Advance to next page
showPage()

# === PAGE 2 ===
setFont("Helvetica-Bold", 16)
drawString(50, 750, "Page 2: Second Page Content")

fillColor("#2ECC71")
rect(50, 650, 500, 50, 0, 1)

fillColor("#FFFFFF")
setFont("Helvetica", 12)
drawCentredString(300, 670, "Multi-page rendering complete!")
"""
    try:
        with open(input_file, "x", encoding="utf-8") as f:
            f.write(sample_dsl)
            print(f"Created sample input file: '{input_file}'")
    except FileExistsError:
        pass


def resolve_output_filename(input_file, output_file):
    """
    Determines output filename:
    1. If output_file is omitted, strips input extension and appends '.pdf'.
    2. If output_file is specified without '.pdf' extension, appends '.pdf'.
    """
    if not output_file:
        base_name, _ = os.path.splitext(input_file)
        return f"{base_name}.pdf"
    
    if not output_file.lower().endswith(".pdf"):
        return f"{output_file}.pdf"
        
    return output_file


def build_cli_parser():
    """
    Configures and returns the command-line argument parser with help text.
    """
    parser = argparse.ArgumentParser(
        prog="reportlab_dsl_converter",
        description="Converts text files containing low-level ReportLab primitive commands into a Letter-sized PDF document.",
        epilog="""
Supported DSL Commands:
  showPage()
  setLineWidth(width)
  setDash(on_len, off_len) / setDash()
  strokeColor(color_name_or_hex)
  fillColor(color_name_or_hex)
  line(x1, y1, x2, y2)
  rect(x, y, w, h, [stroke], [fill])
  circle(x, y, r, [stroke], [fill])
  beginPath() / moveTo(x, y) / lineTo(x, y) / closePath() / drawPath([stroke], [fill])
  setFont("FontName", size)
  drawString(x, y, "text")
  drawCentredString(x, y, "text")
  drawRightString(x, y, "text")
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "input_file",
        nargs="?",
        default="commands.txt",
        help="Path to the input text file containing primitive DSL commands (default: 'commands.txt')"
    )

    parser.add_argument(
        "output_file",
        nargs="?",
        default=None,
        help="Path for generated PDF. Omit to reuse input filename with '.pdf' extension."
    )

    return parser


def main():
    parser = build_cli_parser()
    args = parser.parse_args()

    input_file = args.input_file
    output_file = resolve_output_filename(input_file, args.output_file)

    if input_file == "commands.txt":
        create_sample_file_if_missing(input_file)

    convert_txt_to_pdf(input_file, output_file)


if __name__ == "__main__":
    main()
