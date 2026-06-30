from abc import ABC, abstractmethod
import sys
from xml.sax.saxutils import escape
import re
from utils import parse_attributes
"""
nroff Processor commands
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
    def process(self, text: str):
        pass


@register('nroff')
class NroffProcessor(Processor):
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

    def process(self, text: str):
        lines = text.splitlines()
        items = []
        current_style = 'body'
        current_style_args = {}
        # persistent style definitions for title/heading/body
        style_defs = {'title': {}, 'heading': {}, 'body': {}}

        center_remaining = 0

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith('.'):
                cmd, args_text = self._parse_command(line)
                # print (f"DEBUG: nroff command: {cmd} with args: {args_text}")
                if cmd in ('title', 'heading', 'body'):
                    current_style = cmd
                    current_style_args = {}
                elif cmd == 'font':
                    # font modifies only the next paragraphs until changed
                    args = parse_attributes(args_text)
                    current_style_args.update(args)
                elif cmd == 'style':
                    # .style name params -> redefine persistent style for rest of doc
                    parts = args_text.split(None, 1)
                    if not parts:
                        # print(f"WARNING: .style requires a name and parameters: '{raw_line}'")
                        continue
                    name = parts[0].lower()
                    params_text = parts[1] if len(parts) > 1 else ''
                    # import sys
                    # print(f"DEBUG {sys._getframe().f_code.co_name}({params_text}) parts={parts}, {type(parts)}")
                    if len(params_text) > 1:
                        params_text = self._process_font_spacing(params_text)
                        # print(f"++++  parts={parts}, {type(params_text)}")

                    # support resetting styles:
                    #  .style reset            -> reset all styles to defaults
                    #  .style reset <name>     -> reset specific style to defaults
                    #  .style <name> reset     -> reset that named style to defaults
                    if name == 'reset':
                        target = params_text.split(None, 1)[0].lower() if params_text else None
                        if target:
                            # print(f"DEBUG: Reset 1 target={target}")
                            if target in style_defs:
                                style_defs[target] = {}
                            else:
                                print(f"WARNING: unknown style name '{target}' in .style reset")
                        else:
                            for k in style_defs:
                                style_defs[k] = {}

                        continue

                    # allow '.style <name> reset' syntax as well
                    if params_text.strip().lower() == 'reset':
                        if name in style_defs:
                            style_defs[name] = {}
                            # print(f"DEBUG: Reset 2 name={name}")
                            items.append({'type': 'reset', 'style':name})
                            current_style_args = {}
                        else:
                            print(f"WARNING: unknown style name '{name}' in .style command")
                        continue

                    if name not in style_defs:
                        print(f"WARNING: unknown style name '{name}' in .style command")
                        continue
                    attrs = parse_attributes(params_text)
                    style_defs[name].update(attrs)
                    # Also make this the current active style so the next paragraph
                    # uses the named style (with any persistent attributes).
                    current_style = name
                    current_style_args = {}
                elif cmd == 'ce': # Center the next line
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
                elif cmd == 'np' or cmd == 'bp': #CME added this
                    # explicit new page or break page command
                    items.append({'type': 'newpage'})
                    # print ("DEBUG: Adding new page for command: {cmd} in cme ssection")
                else:
                    # unknown command: ignore
                    # print(f"DEBUG: Unknown command: {cmd}")
                    continue
                continue
            # vvv CME I dont think these lines work
            if line.startswith('.np') or line.startswith('.bp'):
                # explicit new page or break page command
                items.append({'type': 'newpage'})
                # print(f"DEBUG: Adding new page for line: {line}")
                # stop current page processing here (signal to renderer)
                continue
                # ^^^^ CME End of problem code area

            # build style args by combining persistent style defs and current overrides
            combined_args = dict(style_defs.get(current_style, {}))
            combined_args.update(current_style_args)
            if center_remaining > 0:
                combined_args['align'] = 'center'
                center_remaining -= 1
            items.append(self._make_paragraph(line, current_style, combined_args.copy()))

        return items


@register('markdown')
class MarkdownProcessor(Processor):
    def process(self, text: str) -> str:
        s = escape(text)
        s = re.sub(r'^# (.+)$', r'<b>\1</b><br/>', s, flags=re.M)
        s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
        s = re.sub(r'\*(.+?)\*', r'<i>\1</i>', s)
        s = s.replace('\n', '<br/>')
        return s


@register('recipe')
class RecipeProcessor(Processor):
    def process(self, text: str) -> str:
        s = escape(text)
        s = re.sub(r'(?m)^\* (.+)$', r'<b>\1</b><br/>', s)
        s = s.replace('\n', '<br/>')
        return s
