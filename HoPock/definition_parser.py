from dataclasses import dataclass, field
import re


@dataclass
class DefinitionEntry:
    page_type: str
    options: dict[str, str] = field(default_factory=dict)
    text: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        rtn = f"{self.page_type} ({self.options})"
        if len(self.text) > 0:
            rtn += f"\n    {self.text}"
        return rtn
        
class DefinitionParser:
    """
    Parser for the pocket project configuration file.

    Examples:

        page1 fontsize=10 color=red

        page2 fontsize = 10 color = red

        page3 title="This is a title"

        page4 fontsize=10 \\
               color=red

        page5 {
            fontsize=10
            color=red
        }

        page6 {
            fontsize=10

            This is text.
            More text.
        }

    Page types and option names are case-insensitive and are returned
    in lowercase.

    Option values and text retain their original case.
    """

    # Valid option names.
    OPTION_NAME = re.compile(
        r"[A-Za-z_][A-Za-z0-9_.-]*"
    )

    def parse_file(self, filename):
        """
        Read and parse a configuration file.
        """

        with open(filename, "r", encoding="utf-8") as file:
            return self.parse_lines(file)

    def parse_lines(self, lines):
        """
        Parse configuration from an iterable of lines.
        """

        entries = []

        lines = iter(lines)

        for raw_line in lines:
            line = raw_line.strip()

            # Ignore blank lines and comments outside an entry.
            if not line or line.startswith("#"):
                continue

            entry = self._parse_entry(line, lines)

            if entry is not None:
                entries.append(entry)

        return entries

    def _parse_entry(self, first_line, lines):
        """
        Parse the first line of a configuration entry.
        """

        parts = first_line.split(None, 1)

        page_type = parts[0].lower()
        remainder = parts[1] if len(parts) > 1 else ""

        # Page type by itself.
        if not remainder:
            return DefinitionEntry(
                page_type=page_type
            )

        # Braced block.
        if remainder.startswith("{"):
            content = remainder[1:].lstrip()

            # Opening and closing braces on the same line.
            if "}" in content:
                content = content.split("}", 1)[0]

                return self._parse_inline_block(
                    page_type,
                    content
                )

            # Multi-line block.
            return self._parse_block(
                page_type,
                content,
                lines
            )

        # No braces -- options end at the end of the logical line.
        option_text = self._collect_continued_line(
            remainder,
            lines
        )

        return DefinitionEntry(
            page_type=page_type,
            options=self._parse_options(option_text)
        )

    def _parse_inline_block(self, page_type, content):
        """
        Parse a block where the opening and closing braces occur
        on the same line.
        """

        if not content.strip():
            return DefinitionEntry(
                page_type=page_type
            )

        if self._looks_like_option(content):
            return DefinitionEntry(
                page_type=page_type,
                options=self._parse_options(content)
            )

        return DefinitionEntry(
            page_type=page_type,
            text=[content]
        )

    def _parse_block(self, page_type, first_content, lines):
        """
        Parse a multi-line {...} block.

        The parser starts in option mode.

        A blank line switches to text mode.

        The first line that isn't an option also switches to text mode.

        Once text mode begins, all subsequent lines are text.
        """

        options = {}
        text = []

        text_mode = False

        # Content appearing on the same line as the opening brace.
        if first_content:
            if self._looks_like_option(first_content):

                option_text = self._collect_continued_line(
                    first_content,
                    lines
                )

                options.update(
                    self._parse_options(option_text)
                )

            else:
                text_mode = True
                text.append(first_content)

        for raw_line in lines:

            # Remove only newline characters.
            raw = raw_line.rstrip("\r\n")

            stripped = raw.strip()

            # Closing brace.
            if stripped == "}":
                break

            # Ignore comments while still parsing options.
            if not text_mode and stripped.startswith("#"):
                continue

            # Blank line switches to text mode.
            if not text_mode and not stripped:
                text_mode = True
                continue

            if not text_mode:

                if self._looks_like_option(raw):
                    option_text = self._collect_continued_line(
                        raw,
                        lines
                    )

                    options.update(
                        self._parse_options(option_text)
                    )

                    continue

                # First non-option line begins text.
                text_mode = True

            if text_mode:
                text.append(raw)

        return DefinitionEntry(
            page_type=page_type,
            options=options,
            text=text
        )

    def _collect_continued_line(self, first_line, lines):
        """
        Combine physical lines into one logical option line.

        A trailing backslash continues the line.

        Example:

            fontsize=10 \\
            color=red

        becomes:

            fontsize=10 color=red
        """

        parts = []
        current = first_line

        while True:

            # Remove trailing whitespace when checking for '\'.
            stripped = current.rstrip()

            if stripped.endswith("\\"):

                # Remove the continuation character.
                parts.append(
                    stripped[:-1].rstrip()
                )

                try:
                    current = next(lines)
                except StopIteration:
                    raise ValueError(
                        "Definitionuration line ends with '\\' "
                        "but no continuation line was found."
                    )

                current = current.rstrip("\r\n")

                # A blank continuation line is invalid.
                if not current.strip():
                    raise ValueError(
                        "Blank line found after a line-continuation "
                        "character '\\'."
                    )

            else:
                parts.append(current.strip())
                break

        return " ".join(parts)

    def _parse_options(self, text):
        """
        Parse an option string using a scanner.

        Supported forms:

            option=value
            option =value
            option= value
            option = value

        Quoted values may contain spaces:

            title="This is a title"

        Option names are converted to lowercase.
        Option values retain their original case.
        """

        options = {}

        position = 0
        length = len(text)

        while position < length:

            # Skip whitespace between options.
            while position < length and text[position].isspace():
                position += 1

            if position >= length:
                break

            # Read the option name.
            match = self.OPTION_NAME.match(
                text,
                position
            )

            if not match:
                raise ValueError(
                    f"Invalid option syntax near: "
                    f"{text[position:]!r}. "
                    f"Expected option=value."
                )

            key = match.group(0).lower()
            position = match.end()

            # Allow whitespace before '='.
            while position < length and text[position].isspace():
                position += 1

            # Require '='.
            if position >= length or text[position] != "=":
                raise ValueError(
                    f"Invalid option '{key}'. "
                    f"Expected '=' after option name."
                )

            position += 1

            # Allow whitespace after '='.
            while position < length and text[position].isspace():
                position += 1

            if position >= length:
                raise ValueError(
                    f"Option '{key}' has no value."
                )

            # Read quoted value.
            if text[position] in ('"', "'"):
                value, position = self._scan_quoted_value(
                    text,
                    position
                )

            # Read unquoted value.
            else:
                value, position = self._scan_unquoted_value(
                    text,
                    position
                )

            options[key] = value

        return options

    @staticmethod
    def _scan_quoted_value(text, position):
        """
        Scan a quoted option value.

        Supports both single and double quotes.

        The surrounding quotes are removed.

        A backslash can escape the quote character.
        """

        quote = text[position]
        position += 1

        value = []

        while position < len(text):

            char = text[position]

            # Closing quote.
            if char == quote:
                return "".join(value), position + 1

            # Escaped character.
            if char == "\\":
                if position + 1 >= len(text):
                    raise ValueError(
                        "Unterminated quoted option value."
                    )

                next_char = text[position + 1]

                if next_char == quote:
                    value.append(next_char)
                else:
                    # Preserve backslash for anything other than
                    # an escaped quote.
                    value.append("\\")
                    value.append(next_char)

                position += 2
                continue

            value.append(char)
            position += 1

        raise ValueError(
            "Unterminated quoted option value."
        )

    @staticmethod
    def _scan_unquoted_value(text, position):
        """
        Scan an unquoted option value.

        An unquoted value ends at whitespace.

        Therefore:

            option=value

        is valid, but:

            option=value with spaces

        is not valid. Use:

            option="value with spaces"
        """

        start = position

        while position < len(text):
            if text[position].isspace():
                break

            position += 1

        value = text[start:position]

        if not value:
            raise ValueError(
                "Option has an empty value."
            )

        return value, position

    def _looks_like_option(self, line):
        """
        Return True if the beginning of a line looks like:

            option=value

        or:

            option = value
        """

        position = 0
        length = len(line)

        # Skip leading whitespace.
        while position < length and line[position].isspace():
            position += 1

        match = self.OPTION_NAME.match(
            line,
            position
        )

        if not match:
            return False

        position = match.end()

        # Allow whitespace before '='.
        while position < length and line[position].isspace():
            position += 1

        return (
            position < length
            and line[position] == "="
        )