from abc import ABC, abstractmethod
from xml.sax.saxutils import escape
import re
from utils import parse_attributes
"""
nroff Processor commands
.style <name> reset -> reset the specified style to its default values
.style name attributes -> define and use the named style with the specified attributes
.font attributes - > sets the current font for the next paragraphs
.np -> insert a new page

TODO:
.br -> insert a new page
.ce -> center the current line
.ps -> fontsize command
.B [text] -> bold text
.I -> italic text
.sp -> vertical space command

        elif line.startswith (".spacer"):
            self.addObject(Spacer(1, self.currentStyle.fontSize))
        elif line.startswith (".newpage") or line.startswith (".np"):
            self.addObject(PageBreak())
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

    def process(self, text: str):
        lines = text.splitlines()
        items = []
        current_style = 'body'
        current_style_args = {}
        # persistent style definitions for title/heading/body
        style_defs = {'title': {}, 'heading': {}, 'body': {}}

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith('.'):
                cmd, args_text = self._parse_command(line)
                print (f"DEBUG: nroff command: {cmd} with args: {args_text}")
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
                        print(f"WARNING: .style requires a name and parameters: '{raw_line}'")
                        continue
                    name = parts[0].lower()
                    params_text = parts[1] if len(parts) > 1 else ''
                    # support resetting styles:
                    #  .style reset            -> reset all styles to defaults
                    #  .style reset <name>     -> reset specific style to defaults
                    #  .style <name> reset     -> reset that named style to defaults
                    if name == 'reset':
                        target = params_text.split(None, 1)[0].lower() if params_text else None
                        if target:
                            print(f"DEBUG: Reset 1 target={target}")
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
                            print(f"DEBUG: Reset 2 name={name}")
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
                elif cmd == 'np' or cmd == 'bp': #CME added this
                    # explicit new page or break page command
                    items.append({'type': 'newpage'})
                    print ("DEBUG: Adding new page for command: {cmd} in cme ssection")
                else:
                    # unknown command: ignore
                    print(f"DEBUG: Unknown command: {cmd}")
                    continue
                continue
            # vvv CME I dont think these lines work
            if line.startswith('.np') or line.startswith('.bp'):
                # explicit new page or break page command
                items.append({'type': 'newpage'})
                print(f"DEBUG: Adding new page for line: {line}")
                # stop current page processing here (signal to renderer)
                continue
                # ^^^^ CME End of problem code area

            # build style args by combining persistent style defs and current overrides
            combined_args = dict(style_defs.get(current_style, {}))
            combined_args.update(current_style_args)
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
