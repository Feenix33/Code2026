from abc import ABC, abstractmethod
import os
import sys
import unicodedata
from xml.sax.saxutils import escape
import re
from utils import parse_attributes
from style_registry import DEFAULT_PARAGRAPH_STYLE_NAME, DEFAULT_PARAGRAPH_STYLE_FOR_RECIPE

NON_PRINTING_REPLACEMENTS = {
    '\u00BD': '1/2',
    '\u00BC': '1/4',
    '\u00BE': '3/4',
    '\u00B0': '',
    '\u00A0': ' ',
}
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
    @abstractmethod
    def process(self, text: str, *, source_path=None, page=None, book=None, use_abbreviations=None):
        pass

    def _clean_text(self, text):
        if text is None:
            return ''

        line = str(text)
        for source, target in NON_PRINTING_REPLACEMENTS.items():
            line = line.replace(source, target)

        normalized = unicodedata.normalize('NFKD', line)
        line = normalized.encode('ascii', 'ignore').decode('ascii')
        return line

"""
This is the fake nroff (froff) formatter
Similar to nroff but the <CR> in the input file signals a new paragraph
"""
@register('froff')
class FroffProcessor(Processor):
    def _parse_command(self, raw_line):
        tokens = raw_line.split(None, 1)
        cmd = tokens[0][1:].lower()
        args_text = tokens[1] if len(tokens) > 1 else ""
        return cmd, args_text

    def _make_paragraph(self, text, style_name, style_args):
        return {
            'type': 'paragraph',
            'text': text,
            'style': style_name,
            'style_args': style_args or {},
        }

    import re

    def _process_font_spacing(self, text_str):
        SPACE_MULTIPLIER = 1.2
        # 1. Handle empty strings or None values immediately
        if not text_str:
            return text_str

        # 2. Check for the presence of 'leading' anywhere in the string.
        # If it's already there, the requirements say we return the string as-is.
        if re.search(r"\bleading=\d+", text_str):
            return text_str

        # 3. Look for 'fontSize=x' where x is an integer or a decimal number.
        # \b ensures we match the exact boundary of the token.
        font_size_match = re.search(r"\bfontSize=(\d+(?:\.\d+)?)", text_str)

        # 4. If fontSize is found (and we already know leading isn't there),
        # calculate the new z value and append it.
        if font_size_match:
            x = float(font_size_match.group(1))
            # Calculate 1.2 * x and truncate to 2 decimal places
            # Using string formatting with splitting ensures strict truncation without rounding bugs
            raw_calc = SPACE_MULTIPLIER * x
            z = f"{raw_calc:.4f}"[:-2]  # Generates extra decimals, then hard-chops it

            # Strip trailing spaces from the original text before appending to keep it clean
            return f"{text_str.rstrip()} leading={z}"

        # 5. If fontSize wasn't found, return the string unchanged
        return text_str

    def _process_lines(self, lines, default_style='body'):
        items = []
        current_style = default_style
        current_style_args = {}
        style_defs = {}
        center_remaining = 0

        for raw_line in lines:
            line = raw_line.rstrip('\r\n')
            stripped_line = line.strip()

            if not stripped_line:
                continue

            if stripped_line.startswith('.'):
                cmd, args_text = self._parse_command(stripped_line)
                if cmd in ('title', 'heading', 'body'):
                    current_style = cmd
                    current_style_args = {}
                elif cmd == 'font':
                    args = parse_attributes(args_text)
                    current_style_args.update(args)
                elif cmd == 'style':
                    parts = args_text.split(None, 1)
                    if not parts:
                        continue

                    name = parts[0].lower()
                    params_text = parts[1] if len(parts) > 1 else ''
                    if len(params_text) > 1:
                        params_text = self._process_font_spacing(params_text)

                    if name == 'reset':
                        target = params_text.split(None, 1)[0].lower() if params_text else None
                        if target:
                            style_defs[target] = {}
                        else:
                            style_defs.clear()
                        continue

                    if params_text.strip().lower() == 'reset':
                        style_defs[name] = {}
                        items.append({'type': 'reset', 'style': name})
                        current_style = name
                        current_style_args = {}
                        continue

                    if not params_text:
                        style_defs.setdefault(name, {})
                        current_style = name
                        current_style_args = {}
                        continue

                    attrs = parse_attributes(params_text)
                    style_defs.setdefault(name, {})
                    style_defs[name].update(attrs)
                    current_style = name
                    current_style_args = {}
                elif cmd == 'ce':
                    count = 1
                    if args_text:
                        try:
                            count = int(args_text.strip())
                        except ValueError:
                            print(f"WARNING: invalid .ce count '{args_text}', defaulting to 1")
                            count = 1
                    center_remaining = max(1, count)
                elif cmd == 'sp':
                    count = 1
                    if args_text:
                        try:
                            count = int(args_text.strip())
                        except ValueError:
                            print(f"WARNING: invalid .sp count '{args_text}', defaulting to 1")
                            count = 1
                    combined_args = dict(style_defs.get(current_style, {}))
                    combined_args.update(current_style_args)
                    for _ in range(max(1, count)):
                        items.append({
                            'type': 'spacer',
                            'style': current_style,
                            'style_args': combined_args.copy(),
                        })
                elif cmd in ('np', 'bp', 'br'):
                    items.append({'type': 'newpage'})
                else:
                    continue
                continue

            if stripped_line.startswith('.np') or stripped_line.startswith('.bp'):
                items.append({'type': 'newpage'})
                continue

            combined_args = dict(style_defs.get(current_style, {}))
            combined_args.update(current_style_args)
            if center_remaining > 0:
                combined_args['align'] = 'center'
                center_remaining -= 1
            clean_line = self._clean_text(stripped_line)
            items.append(self._make_paragraph(clean_line, current_style, combined_args.copy()))

        return items

    def process(self, text: str, *, source_path=None, page=None, book=None, use_abbreviations=None):
        return self._process_lines(text.splitlines(), default_style=DEFAULT_PARAGRAPH_STYLE_NAME)


_registry['nroff'] = _registry['froff']

@register('markdown')
class MarkdownProcessor(Processor):
    def process(self, text: str, *, source_path=None, page=None, book=None, use_abbreviations=None) -> str:
        s = escape(text)
        s = re.sub(r'^# (.+)$', r'<b>\1</b><br/>', s, flags=re.M)
        s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
        s = re.sub(r'\*(.+?)\*', r'<i>\1</i>', s)
        s = s.replace('\n', '<br/>')
        return s


@register('recipe')
class RecipeProcessor(Processor):
    DEFAULT_RECIPE_ABBREVIATIONS = {
        'cups': 'c',
        'cup': 'c',
        'teaspoons': 'tsp',
        'teaspoon': 'tsp',
        'tablespoons': 'Tbl',
        'tablespoon': 'Tbl',
        'preheat': '',
        'ounces': 'oz',
        'ounce': 'oz',
        'small': 'sml',
        'medium': 'med',
        'large': 'lg',
        'pound': 'lb',
        'minute': 'min',
        'minutes': 'min',
        'hour': 'hr',
        'seconds': 'sec',
    }

    def _parse_command(self, raw_line):
        tokens = raw_line.split(None, 1)
        cmd = tokens[0][1:].lower()
        args_text = tokens[1] if len(tokens) > 1 else ""
        return cmd, args_text

    def _make_paragraph(self, text, style_name, style_args):
        return {
            'type': 'paragraph',
            'text': self._clean_text(text),
            'style': style_name,
            'style_args': style_args or {},
        }

    def _apply_abbreviations(self, line, abbreviations):
        if not abbreviations:
            return line

        pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in abbreviations) + r")\b", re.IGNORECASE)

        def replace(match):
            return abbreviations[match.group(1).lower()]

        return pattern.sub(replace, line)

    def _process_lines(self, lines, default_style='line', source_path=None, use_abbreviations=False):
        items = []
        current_style = default_style
        current_style_args = {}
        style_defs = {}
        abbreviations = dict(self.DEFAULT_RECIPE_ABBREVIATIONS)

        title_emitted = False
        title_source_name = os.path.splitext(os.path.basename(source_path))[0] if source_path else 'Recipe'
        center_remaining = 0

        for raw_line in lines:
            line = raw_line.rstrip('\r\n')
            stripped_line = line.strip()

            if stripped_line.startswith('.'):
                cmd, args_text = self._parse_command(stripped_line)
                if cmd in ('title', 'heading', 'body'):
                    current_style = cmd
                    current_style_args = {}
                elif cmd == 'font':
                    args = parse_attributes(args_text)
                    current_style_args.update(args)
                elif cmd == 'style':
                    parts = args_text.split(None, 1)
                    if not parts:
                        continue

                    name = parts[0].lower()
                    params_text = parts[1] if len(parts) > 1 else ''
                    if len(params_text) > 1:
                        params_text = self._process_font_spacing(params_text)

                    if name == 'reset':
                        target = params_text.split(None, 1)[0].lower() if params_text else None
                        if target:
                            style_defs[target] = {}
                        else:
                            style_defs.clear()
                        continue

                    if params_text.strip().lower() == 'reset':
                        style_defs[name] = {}
                        items.append({'type': 'reset', 'style': name})
                        current_style = name
                        current_style_args = {}
                        continue

                    if not params_text:
                        style_defs.setdefault(name, {})
                        current_style = name
                        current_style_args = {}
                        continue

                    attrs = parse_attributes(params_text)
                    style_defs.setdefault(name, {})
                    style_defs[name].update(attrs)
                    current_style = name
                    current_style_args = {}
                elif cmd == 'abbrev':
                    if args_text.strip().lower() == 'reset':
                        abbreviations = dict(self.DEFAULT_RECIPE_ABBREVIATIONS)
                        continue
                    abbreviations.update(parse_attributes(args_text))
                elif cmd == 'ce':
                    count = 1
                    if args_text:
                        try:
                            count = int(args_text.strip())
                        except ValueError:
                            print(f"WARNING: invalid .ce count '{args_text}', defaulting to 1")
                            count = 1
                    center_remaining = max(1, count)
                elif cmd == 'sp':
                    count = 1
                    if args_text:
                        try:
                            count = int(args_text.strip())
                        except ValueError:
                            print(f"WARNING: invalid .sp count '{args_text}', defaulting to 1")
                            count = 1
                    combined_args = dict(style_defs.get(current_style, {}))
                    combined_args.update(current_style_args)
                    for _ in range(max(1, count)):
                        items.append({
                            'type': 'spacer',
                            'style': current_style,
                            'style_args': combined_args.copy(),
                        })
                elif cmd in ('np', 'bp', 'br'):
                    items.append({'type': 'newpage'})
                else:
                    continue
                continue

            if stripped_line.startswith('.np') or stripped_line.startswith('.bp'):
                items.append({'type': 'newpage'})
                continue

            if not title_emitted:
                if stripped_line and stripped_line[0].isalpha():
                    title_text = self._clean_text(stripped_line)
                    if use_abbreviations:
                        title_text = self._apply_abbreviations(title_text, abbreviations)
                    items.append(self._make_paragraph(title_text, 'title2', {}))
                    items.append({'type': 'spacer', 'style': 'line', 'style_args': {}})
                    title_emitted = True
                    continue

                title_text = title_source_name
                items.append(self._make_paragraph(title_text, 'title2', {}))
                items.append({'type': 'spacer', 'style': 'line', 'style_args': {}})
                title_emitted = True

                if stripped_line:
                    cleaned_line = self._clean_text(stripped_line)
                    if use_abbreviations:
                        cleaned_line = self._apply_abbreviations(cleaned_line, abbreviations)
                    combined_args = dict(style_defs.get(current_style, {}))
                    combined_args.update(current_style_args)
                    if center_remaining > 0:
                        combined_args['align'] = 'center'
                        center_remaining -= 1
                    items.append(self._make_paragraph(cleaned_line, 'line', combined_args.copy()))
                continue

            if not stripped_line:
                items.append({'type': 'spacer', 'style': 'line', 'style_args': {}})
                continue

            cleaned_line = self._clean_text(stripped_line)
            if use_abbreviations:
                cleaned_line = self._apply_abbreviations(cleaned_line, abbreviations)
            combined_args = dict(style_defs.get(current_style, {}))
            combined_args.update(current_style_args)
            if center_remaining > 0:
                combined_args['align'] = 'center'
                center_remaining -= 1
            items.append(self._make_paragraph(cleaned_line, 'line', combined_args.copy()))

        return items

    def process(self, text: str, *, source_path=None, page=None, book=None, use_abbreviations=None):
        if use_abbreviations is None and book is not None:
            use_abbreviations = getattr(book.config, 'useRecipeAbbreviations', False)
        if use_abbreviations is None:
            use_abbreviations = False
        return self._process_lines(
            text.splitlines(),
            default_style=DEFAULT_PARAGRAPH_STYLE_FOR_RECIPE,
            source_path=source_path,
            use_abbreviations=use_abbreviations,
        )
