from dataclasses import dataclass, field
import shlex
import re


@dataclass
class ConfigEntry:
    page_type: str
    options: dict[str, str] = field(default_factory=dict)
    text: list[str] = field(default_factory=list)


class ConfigParser:
    """
    Parses a simple page configuration file.

    Supported forms:

        page_type option1=value option2=value

        page_type {
            option1=value
            option2=value
        }

    Special page types may also contain arbitrary text.
    """

    def __init__(self, special_types=None):
        self.special_types = set(special_types or [])

    def parse_file(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            return self.parse_lines(f)

    def parse_lines(self, lines):
        entries = []

        lines = iter(lines)

        for raw_line in lines:
            line = raw_line.strip()

            # Ignore comments and blank lines outside entries
            if not line or line.startswith("#"):
                continue

            entry = self._parse_entry(line, lines)

            if entry is not None:
                entries.append(entry)

        return entries

    def _parse_entry(self, first_line, lines):
        """
        Parse one page entry.
        """

        # Find the page type
        parts = first_line.split(None, 1)
        page_type = parts[0]

        remainder = parts[1] if len(parts) > 1 else ""

        # Is this a braced block?
        if remainder.startswith("{"):
            content = remainder[1:].lstrip()

            # Everything is on one line
            if "}" in content:
                content = content.split("}", 1)[0]

                if page_type in self.special_types:
                    return self._parse_special_inline(
                        page_type, content
                    )

                return ConfigEntry(
                    page_type=page_type,
                    options=self._parse_options(content)
                )

            # Multi-line block
            return self._parse_block(page_type, content, lines)

        # No braces -- options end at the end of this line
        return ConfigEntry(
            page_type=page_type,
            options=self._parse_options(remainder)
        )

    def _parse_block(self, page_type, first_content, lines):
        """
        Parse a {...} block.
        """

        if page_type in self.special_types:
            return self._parse_special_block(
                page_type,
                first_content,
                lines
            )

        # Normal page type -- everything inside braces is options
        option_lines = []

        if first_content:
            option_lines.append(first_content)

        for raw_line in lines:
            line = raw_line.strip()

            if line.startswith("#"):
                continue

            if "}" in line:
                before_close = line.split("}", 1)[0]

                if before_close:
                    option_lines.append(before_close)

                break

            if line:
                option_lines.append(line)

        option_text = " ".join(option_lines)

        return ConfigEntry(
            page_type=page_type,
            options=self._parse_options(option_text)
        )

    def _parse_special_block(self, page_type, first_content, lines):
        """
        Parse a special block containing both options and text.

        Option lines must contain key=value.
        Once a non-option line is encountered, remaining lines
        are treated as text.
        """

        options = {}
        text = []

        text_mode = False

        if first_content:
            if self._looks_like_option(first_content):
                options.update(self._parse_options(first_content))
            else:
                text_mode = True
                text.append(first_content)

        for raw_line in lines:
            raw = raw_line.rstrip("\r\n")

            # Closing brace
            if raw.strip() == "}":
                break

            # Comments while still parsing options
            if not text_mode and raw.strip().startswith("#"):
                continue

            # Blank line switches to text mode
            if not text_mode and not raw.strip():
                text_mode = True
                continue

            if not text_mode:
                if self._looks_like_option(raw):
                    options.update(self._parse_options(raw))
                    continue

                # First non-option line starts the text
                text_mode = True

            if text_mode:
                text.append(raw)

        return ConfigEntry(
            page_type=page_type,
            options=options,
            text=text
        )

    def _parse_special_inline(self, page_type, content):
        """
        Handle:

            special_type { option=value text... }

        This is mainly useful if the entire block is on one line.
        """

        if self._looks_like_option(content):
            return ConfigEntry(
                page_type=page_type,
                options=self._parse_options(content)
            )

        return ConfigEntry(
            page_type=page_type,
            text=[content]
        )

    @staticmethod
    def _looks_like_option(line):
        """
        Determine whether a line looks like:

            key=value
        """

        return re.match(
            r"^\s*[A-Za-z_][A-Za-z0-9_.-]*\s*=",
            line
        ) is not None

    @staticmethod
    def _parse_options(text):
        """
        Parse:

            option1=value option2="text with spaces"

        into a dictionary.
        """

        if not text.strip():
            return {}

        tokens = shlex.split(text)

        options = {}

        for token in tokens:
            if "=" not in token:
                raise ValueError(
                    f"Expected option=value, got: {token!r}"
                )

            key, value = token.split("=", 1)
            options[key.strip()] = value

        return options
