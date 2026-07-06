from abc import ABC, abstractmethod
import os
import sys
import unicodedata
from xml.sax.saxutils import escape
import re
from utils import parse_attributes
from style_registry import DEFAULT_PARAGRAPH_STYLE_NAME, DEFAULT_PARAGRAPH_STYLE_FOR_RECIPE

import re

"""
froff Processor commands
.style <name> reset -> reset the specified style to its default values
.style name attributes -> define and use the named style with the specified attributes
.font attributes - > sets the current font for the next paragraphs
.np -> insert a new page
.br -> insert a new page
.ce -> center the current line
.sp -> vertical space command

Not going to do these as the formatter is interpreting the line breaks incorrectly.
.ps -> fontsize command
.B [text] -> bold text
.I -> italic text


markdown Processor Commands
# Header 1
## H2
### H3

H4-H6 = H3 in formatting

Alternative
H1       H2
==       --

*italics*  OR _italics_
**bold**  OR __bold__
**_bold italic_**
~~strikethrough~~
1. List item (numbered, the numnber at front does not matter)
* unordered list item (bullet list)
+ unordered list item
- unordered list item
[link] ignore since this is print
''' start or end a code block, shift font to Courier, but ignore all other formatting for code and inline code

"""

NON_PRINTING_REPLACEMENTS = {
    # Original fraction and space mappings
    "\u00bd": "1/2",  # ½
    "\u00bc": "1/4",  # ¼
    "\u00be": "3/4",  # ¾
    "\u00b0": "",  # ° (degree sign stripped)
    "\u00a0": " ",  # Non-breaking space
    # Spanish Punctuation & Typography
    "\u00bf": "",  # ¿ (Inverted question mark - strip or replace with '')
    "\u00a1": "",  # ¡ (Inverted exclamation mark - strip or replace with '')
    "\u00ba": ".",  # º (Masculine ordinal indicator, e.g., 1º -> 1.)
    "\u00aa": ".",  # ª (Feminine ordinal indicator, e.g., 1ª -> 1.)
    # French Typographical Ligatures & Quotes
    "\u0152": "OE",  # Œ (Uppercase OE ligature)
    "\u0153": "oe",  # œ (Lowercase oe ligature)
    "\u00ab": '"',  # « (Left-pointing guillemet / French quotation mark)
    "\u00bb": '"',  # » (Right-pointing guillemet / French quotation mark)
}


def parse_attributes(text):
    return {}


_registry = {}


def register(name):
    def decorator(cls):
        _registry[name.lower()] = cls()
        return cls

    return decorator


def get(name):
    if not name:
        return None
    return _registry.get(str(name).lower())


class Processor(ABC):
    """
    Base class enforcing a standard text processing pipeline.
    Ensures human readability and effortless extension for Troff/Markdown styles.
    """

    def __init__(self):
        self.current_style = "body"
        self.style_modifiers = {}
        self.style_defs = {}
        self.output_items = []
        self._text_buffer = []

    def process(self, text: str, **kwargs) -> list:
        """Core execution pipeline framework."""
        self._reset_state(**kwargs)
        lines = text.splitlines()

        for raw_line in lines:
            # 1. Clean & Sanitize Text
            cleaned_line = self._sanitize_text(raw_line)

            # 2. Check and Handle Commands
            if self._is_command(cleaned_line):
                self._flush_buffer()  # Commands usually break current paragraph accumulation
                self._handle_command(cleaned_line)
                continue

            # 3. Apply Context-Specific Substitutions (HTML tags, text macros, etc.)
            transformed_line = self._apply_substitutions(cleaned_line)

            # 4. Process layout manipulation (line-by-line vs paragraph buffer)
            self._accumulate_or_build_paragraph(transformed_line)

        # End of File: flush any lingering multi-line buffers
        self._flush_buffer()
        return self._finalize_output()

    def _sanitize_text(self, text: str) -> str:
        """Cleans 7-bit ASCII non-printable characters and strips accents."""
        if not text:
            return ""
        line = str(text)
        for source, target in NON_PRINTING_REPLACEMENTS.items():
            line = line.replace(source, target)

        normalized = unicodedata.normalize("NFKD", line)
        return normalized.encode("ascii", "ignore").decode("ascii")

    def _is_command(self, line: str) -> bool:
        """Default behavior: assumes commands are lines starting with '.'"""
        return line.strip().startswith(".")

    def _parse_command(self, line: str) -> tuple[str, str]:
        """Helper to unpack a dot command into a (command_name, arguments) tuple."""
        tokens = line.strip().split(None, 1)
        cmd = tokens[0][1:].lower()
        args = tokens[1] if len(tokens) > 1 else ""
        return cmd, args

    def _make_paragraph_token(
        self, text: str, style_name: str, style_args: dict
    ) -> dict:
        """Factory method to ensure structured consistency of paragraph items."""
        return {
            "type": "paragraph",
            "text": text,
            "style": style_name,
            "style_args": style_args or {},
        }

    def _reset_state(self, **kwargs):
        """Prepares state hooks before reading a new file stream."""
        self.output_items = []
        self._text_buffer = []
        self.current_style = "body"
        self.style_modifiers = {}
        self.style_defs = {}

    @abstractmethod
    def _handle_command(self, line: str):
        """Subclasses define their unique command vocabularies here."""
        pass

    @abstractmethod
    def _apply_substitutions(self, line: str) -> str:
        """Subclasses perform inline conversions (like markdown tags or typos)."""
        return line

    @abstractmethod
    def _accumulate_or_build_paragraph(self, line: str):
        """Subclasses define whether they treat lines individually or stack them."""
        pass

    def _flush_buffer(self):
        """Hook for multi-line accumulators to write to output_items."""
        pass

    def _finalize_output(self) -> list:
        """Hook for structural modifications right before returning tokens."""
        return self.output_items


@register("froff")
class FroffProcessor(Processor):
    """Fake Nroff Formatter: Treats non-empty lines as individual paragraphs."""

    def _handle_command(self, line: str):
        cmd, args_text = self._parse_command(line)

        if cmd in ("title", "heading", "body"):
            self.current_style = cmd
            self.style_modifiers = {}

        elif cmd == "font":
            self.style_modifiers.update(parse_attributes(args_text))

        elif cmd == "sp":
            count = 1
            try:
                if args_text:
                    count = int(args_text.strip())
            except ValueError:
                count = 1

            combined_args = {
                **self.style_defs.get(self.current_style, {}),
                **self.style_modifiers,
            }
            for _ in range(max(1, count)):
                self.output_items.append(
                    {
                        "type": "spacer",
                        "style": self.current_style,
                        "style_args": combined_args.copy(),
                    }
                )

        elif cmd in ("np", "bp", "br"):
            self.output_items.append({"type": "newpage"})

    def _apply_substitutions(self, line: str) -> str:
        # Insert your `_process_font_spacing` logic or regex translations here
        return line

    def _accumulate_or_build_paragraph(self, line: str):
        stripped = line.strip()
        if not stripped:
            return

        combined_args = {
            **self.style_defs.get(self.current_style, {}),
            **self.style_modifiers,
        }
        token = self._make_paragraph_token(stripped, self.current_style, combined_args)
        self.output_items.append(token)


@register("recipe")
class RecipeProcessor(Processor):
    """Processes recipe card layouts seamlessly using structured pipeline steps."""

    DEFAULT_ABBREVIATIONS = {
        "cups": "c",
        "cup": "c",
        "teaspoons": "tsp",
        "teaspoon": "tsp",
        "tablespoons": "Tbl",
        "tablespoon": "Tbl",
        "ounces": "oz",
        "ounce": "oz",
        "pounds": "lb",
        "pound": "lb",
        "medium": "med",
        "large": "lg",
        "small": "sm",
        "minute": "min",
        "minutes": "min",
        "hour": "hr",
        "hours": "hr",
    }

    def _reset_state(self, **kwargs):
        super()._reset_state(**kwargs)
        self.current_style = "line"
        self.use_abbreviations = kwargs.get("use_abbreviations", False)

        # Streamlined handling of optional configuration title
        passed_title = kwargs.get("title")
        if passed_title:
            self.output_items.append(
                self._make_paragraph_token(passed_title, "title2", {})
            )
            self.output_items.append(
                {"type": "spacer", "style": "line", "style_args": {}}
            )

    def _handle_command(self, line: str):
        cmd, args_text = self._parse_command(line)
        if cmd == "sp":
            self.output_items.append(
                {"type": "spacer", "style": "line", "style_args": {}}
            )
        elif cmd in ("np", "bp", "br"):
            self.output_items.append({"type": "newpage"})

    def _apply_substitutions(self, line: str) -> str:
        if not self.use_abbreviations or not line:
            return line

        pattern = re.compile(
            r"\b("
            + "|".join(re.escape(k) for k in self.DEFAULT_ABBREVIATIONS)
            + r")\b",
            re.IGNORECASE,
        )
        return pattern.sub(
            lambda m: self.DEFAULT_ABBREVIATIONS[m.group(1).lower()], line
        )

    def _accumulate_or_build_paragraph(self, line: str):
        stripped = line.strip()
        if not stripped:
            self.output_items.append(
                {"type": "spacer", "style": "line", "style_args": {}}
            )
            return

        token = self._make_paragraph_token(stripped, "line", {})
        self.output_items.append(token)

###=================================================================================================================


@register("troff")
class TroffProcessor(Processor):
    """
    Simplistic Troff/Groff document parser supporting multi-line accumulation,
    standard inline font changes, layout macros, and custom style registration.
    """

    def _reset_state(self, **kwargs):
        super()._reset_state(**kwargs)
        self.current_style = "body"

        # State machine tracking for active inline font style modifiers
        self._current_font_modifier = "R"  # R=Roman, B=Bold, I=Italic, BI=Bold+Italic

        # Keep track of center block text lines count
        self._center_remaining = 0

    def _handle_command(self, line: str):
        """Processes a subset of simplified layout macros and custom configurations."""
        cmd, args_text = self._parse_command(line)
        args = args_text.split()

        # --- Ignored Structural Commands (Requested placeholders) ---
        if cmd in ("ts", "te", "th", "tc", "tl", "hd", "fo"):
            # Tables, Table of contents, Headers, and Footers are safely omitted
            return

        # --- Document Structure Macros ---
        elif cmd in ("pp", "p", "lp"):
            # Paragraph breaks: .pp (Paragraph) or .lp (Left-aligned block)
            # Implies flushing any structural text blocks gathered so far
            self.current_style = "body"

        elif cmd == "sp":
            # Space macro: inserts default spacing or fixed lines
            count = 1
            if args:
                try:
                    count = int(args[0])
                except ValueError:
                    count = 1

            for _ in range(max(1, count)):
                self.output_items.append(
                    {
                        "type": "spacer",
                        "style": self.current_style,
                        "style_args": self.style_modifiers.copy(),
                    }
                )

        elif cmd in ("np", "bp", "br"):
            # Page breaks
            self.output_items.append({"type": "newpage"})

        elif cmd == "ce":
            # Centering macro: .ce N centers subsequent lines
            self._center_remaining = 1
            if args:
                try:
                    self._center_remaining = max(1, int(args[0]))
                except ValueError:
                    self._center_remaining = 1

        # --- Font Layout Changes ---
        elif cmd == "ft":
            # Font macro: .ft B, .ft I, .ft BI, .ft R
            if args:
                font_type = args[0].upper()
                if font_type in ("R", "B", "I", "BI"):
                    self._current_font_modifier = font_type

        # --- Inline Images Processing ---
        elif cmd == "pspic":
            # Traditional PostScript image placement macro syntax: .pspic filename.png
            if args:
                image_filename = args[0]
                self.output_items.append({"type": "image", "file": image_filename})

        # --- Custom Dynamic Style Commands ---
        elif cmd == "style":
            # Custom integration: .style heading2
            # Overrides self.current_style across all subsequent multi-line paragraphs
            if args:
                requested_style = args[0].lower()
                self.current_style = requested_style

    def _apply_substitutions(self, line: str) -> str:
        """
        Translates classic inline Troff escape strings into valid, balanced HTML tags.
        Example: \\fIitalicized\\fR -> <i>italicized</i>
        """
        if not line:
            return line

        # 1. Block-level fallback formatting (if .ft macro was used)
        if self._current_font_modifier == "B":
            line = f"<b>{line}</b>"
        elif self._current_font_modifier == "I":
            line = f"<i>{line}</i>"
        elif self._current_font_modifier == "BI":
            line = f"<b><i>{line}</i></b>"

        # 2. Parse inline Troff escape tokens chronologically to maintain balanced HTML
        tokens = re.split(r"(\\fB|\\fI|\\f\(BI|\\fR)", line)
        processed_segments = []
        open_tags = []

        for token in tokens:
            if token == r"\fB":
                processed_segments.append("<b>")
                open_tags.append("</b>")
            elif token == r"\fI":
                processed_segments.append("<i>")
                open_tags.append("</i>")
            elif token == r"\f(BI":
                processed_segments.append("<b><i>")
                open_tags.append("</i></b>")
            elif token == r"\fR":
                # Pop and close only the tags that are currently open
                if open_tags:
                    processed_segments.append(open_tags.pop())
            else:
                # Regular text segment
                processed_segments.append(token)

        # Safety flush: Close any tags left open at the end of the line string
        while open_tags:
            processed_segments.append(open_tags.pop())

        return "".join(processed_segments)

    def _accumulate_or_build_paragraph(self, line: str):
        """Accumulates continuous multi-line input strings into layout tokens."""
        stripped = line.strip()

        # Empty lines break paragraph structures in Troff processing engines
        if not stripped:
            self._flush_buffer()
            return

        self._text_buffer.append(stripped)

        # If a line centering constraint is active, flush immediately to ensure layout separation
        if self._center_remaining > 0:
            self._flush_buffer()

    def _flush_buffer(self):
        """Assembles accumulated lines into single unified output tokens."""
        if not self._text_buffer:
            return

        combined_text = " ".join(self._text_buffer)

        # Construct active runtime styling metadata arguments
        combined_args = self.style_modifiers.copy()
        if self._center_remaining > 0:
            combined_args["align"] = "center"
            self._center_remaining -= 1

        token = self._make_paragraph_token(
            combined_text, self.current_style, combined_args
        )
        self.output_items.append(token)

        # Clear local buffer array for next document paragraph sequence
        self._text_buffer.clear()
