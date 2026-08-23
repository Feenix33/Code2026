from dataclasses import dataclass, field
import re
import shlex


@dataclass
class ConfigEntry:
    page_type: str
    options: dict[str, str] = field(default_factory=dict)
    text: list[str] = field(default_factory=list)


class ConfigParser:
    """
    Parse a pocket project configuration file.

    Supported forms:

        page_type option1=value option2=value

        page_type {
            option1=value
            option2=value
            Text goes here
            More text goes here
        }

    Page types and option names are case-insensitive and are returned
    in lowercase.

    Option values and text retain their original case.

    Option values containing spaces must be enclosed in double quotes:

        title="This is a title"

    Options may be continued onto additional physical lines using
    a backslash:

        page1 fontsize=10 \
        color=red

    The above is equivalent to:

        page1 fontsize=10 color=red
    """

    def parse_file(self, filename):
        """Read and parse a configuration file."""

        with open(filename, "r", encoding="utf-8") as file:
            return self.parse_lines(file)

    def parse_lines(self, lines):
        """Parse configuration from an iterable of lines."""

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
        """Parse the first line of an entry."""

        parts = first_line.split(None, 1)

        page_type = parts[0].lower()
        remainder = parts[1] if len(parts) > 1 else ""

        # No options or block.
        if not remainder:
            return ConfigEntry(page_type=page_type)

        # Braced block.
        if remainder.startswith("{"):
            content = remainder[1:].lstrip()

            # Entire block is on one line.
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

        # No braces -- options continue only if the line
        # uses the continuation character.
        option_text = self._collect_continued_line(
            remainder,
            lines
        )

        return ConfigEntry(
            page_type=page_type,
            options=self._parse_options(option_text)
        )

    def _parse_inline_block(self, page_type, content):
        """
        Parse a block where the opening and closing braces
        occur on the same line.
        """

        if not content.strip():
            return ConfigEntry(page_type=page_type)

        if self._looks_like_option(content):
            return ConfigEntry(
                page_type=page_type,
                options=self._parse_options(content)
            )

        return ConfigEntry(
            page_type=page_type,
            text=[content]
        )

    def _parse_block(self, page_type, first_content, lines):
        """
        Parse a multi-line {...} block.

        Initially, lines containing key=value are treated as options.

        Once a non-option line is encountered, the parser switches
        permanently to text mode.

        A blank line also switches to text mode.

        Option lines can use the continuation character '\\'.
        """

        options = {}
        text = []

        text_mode = False

        # Handle anything appearing after the opening {.
        if first_content:
            if self._looks_like_option(first_content):
                option_text, continuation = self._collect_continued_line(
                    first_content,
                    lines,
                    return_continuation=True
                )

                options.update(
                    self._parse_options(option_text)
                )

                # If continuation was requested, _collect_continued_line
                # has already consumed the necessary lines.
            else:
                text_mode = True
                text.append(first_content)

        for raw_line in lines:

            # Remove only newline characters.
            # This preserves text otherwise.
            raw = raw_line.rstrip("\r\n")

            stripped = raw.strip()

            # Closing brace.
            if stripped == "}":
                break

            # Comments are ignored while still reading options.
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

                # First non-option line starts text.
                text_mode = True

            if text_mode:
                text.append(raw)

        return ConfigEntry(
            page_type=page_type,
            options=options,
            text=text
        )

    @staticmethod
    def _collect_continued_line(
        first_line,
        lines,
        return_continuation=False
    ):
        """
        Collect a logical line that may span multiple physical lines.

        A line ending in '\\' continues onto the next physical line.

        For example:

            fontsize=10 \\
            color=red

        becomes:

            fontsize=10 color=red

        The continuation character itself is removed.
        """

        parts = []
        current = first_line

        while True:

            stripped = current.rstrip()

            if stripped.endswith("\\"):
                parts.append(stripped[:-1].rstrip())

                try:
                    current = next(lines)
                except StopIteration:
                    raise ValueError(
                        "Configuration line ends with '\\' "
                        "but no continuation line was found."
                    )

                current = current.rstrip("\r\n")

                # A blank continuation line is probably an error.
                if not current.strip():
                    raise ValueError(
                        "Blank line found after a line-continuation "
                        "character '\\'."
                    )

            else:
                parts.append(current.strip())
                break

        result = " ".join(parts)

        if return_continuation:
            return result, len(parts) > 1

        return result

    @staticmethod
    def _looks_like_option(line):
        """
        Return True if a line begins with something that looks
        like an option name followed by '='.
        """

        return re.match(
            r"^\s*[A-Za-z_][A-Za-z0-9_.-]*\s*=",
            line
        ) is not None

    @staticmethod
    def _parse_options(text):
        """
        Parse options from a string.

        Whitespace around '=' is optional.

        Examples:

            fontsize=12
            fontsize =12
            fontsize= 12
            fontsize = 12
            title="This Is A Title"
            title = "This Is A Title"

        Option names are converted to lowercase.
        Option values retain their original case.
        """

        if not text.strip():
            return {}

        options = {}

        # Match option name followed by '=' and capture the value.
        #
        # The value continues until the next option name followed by '='.
        option_pattern = re.compile(
            r"""
            ([A-Za-z_][A-Za-z0-9_.-]*)   # option name
            \s*=\s*                       # equals sign
            (
                "(?:\\.|[^"])*"           # quoted value
                |
                '(?:\\.|[^'])*'            # or single-quoted value
                |
                .*?                       # or unquoted value
            )
            (?=
                \s+[A-Za-z_][A-Za-z0-9_.-]*\s*=  # next option
                |
                $
            )
            """,
            re.VERBOSE
        )

        matches = option_pattern.finditer(text)

        consumed = 0

        for match in matches:
            key = match.group(1).lower()
            value = match.group(2).strip()

            if not key:
                raise ValueError(
                    f"Invalid option syntax: {match.group(0)!r}"
                )

            # Remove matching quotes from the value.
            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in ('"', "'")
            ):
                value = value[1:-1]

            options[key] = value

            consumed = match.end()

        # Make sure we consumed the entire input.
        if text[consumed:].strip():
            raise ValueError(
                f"Invalid option syntax near: "
                f"{text[consumed:].strip()!r}. "
                f"Expected option=value."
            )

        return options