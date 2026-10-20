"""
markdown processor
Simplistic markdown processor
Handled commands:
# Heading1
## Heading2 - HeadingN
* bullet list
+ bullet list
1 numbered list
''' code block
> Indent block

*italics* _italics_
**bold** __bold__
**_bold italic_**
~~strikethrough~~

Notes:
The heading command goes to the end of the line
Regular text keeps pulling lines until there are two CR. If there is one, then they text lines are part of the same paragraph
Code block symbol at the beginning and end of a line, each CR is a 'paragraph'
Potential alternative is [links] could be rendered underlined
Appears that combining text into a paragraph also is for bullets. To end a bullet need the next bullet or two CR (i.e. blank line)
Multiple blank line CRs are joined in the output. Blank line rendered as space between paras
"""
from processors.base import Processor
from collections import deque
from reportlab.platypus import Frame, Paragraph, XPreformatted, ListFlowable, Spacer #, PageBreak
from processors.reportlab_style_gen import ReportLabStyleProvider
import mistune
from mistune.renderers.markdown import MarkdownRenderer
from models.styles import Marker
from utility import string_to_args
import re

import logging
logger = logging.getLogger(__name__)

## ================================================================================================================

class MarkdownProcessor(Processor):

    def process(self, text, styles:ReportLabStyleProvider, titletext=None, **kwargs):
        # fifo = deque()
        logger.debug ("Markdown II ENGAGED")

        renderer = MyMarkdownRenderer(styles=styles)
        markdown = mistune.create_markdown(renderer=renderer, plugins=['table'])
        markdown('\n'.join(text))

        return deque(renderer.queue)

## ================================================================================================================

class MyMarkdownRenderer(MarkdownRenderer):
    """Custom renderer that intercepts Markdown blocks into a flat queue.
    Inheriting from MarkdownRenderer automatically processes nested inline styles 
    (bold, italics, code) into formatted strings.
    """

    def __init__(self, styles:ReportLabStyleProvider):
        super().__init__()
        self.queue = []
        self.styles = styles

    def heading(self, token: dict, state: mistune.BlockState) -> str:
        text = self.render_children(token, state)
        level = token['attrs']['level']
        if level == 1:
            para_style = self.styles.get("heading1")
        else:
            para_style = self.styles.get("heading2")
        self.queue.append(Paragraph(text, para_style))
        return ""

    def paragraph(self, token: dict, state: mistune.BlockState) -> str:
        text = self.render_children(token, state)
        para_style = self.styles.get("body")
        self.queue.append(Paragraph(text, para_style))
        return ""

    def strong(self, token: dict, state: mistune.BlockState) -> str:
        # 1. Process nested items inside the bold tags (e.g. text, italics, or code)
        text = self.render_children(token, state)
        
        # 2. Return the string wrapped in ReportLab's HTML-style paragraph tags 
        # so that ReportLab's Paragraph handles the font styling inline.
        return f"<b>{text}</b>"

    def emphasis(self, token: dict, state: mistune.BlockState) -> str:
        # 1. Process nested items inside the italic tags
        text = self.render_children(token, state)
        
        # 2. Return the string wrapped in ReportLab's italic tag
        return f"<i>{text}</i>"

    def list(self, token: dict, state: mistune.BlockState) -> str:
        """Handle both ordered and unordered lists."""

        ordered = token['attrs'].get('ordered', False)
        style = "numbered_list" if ordered else "bullet_list"
        bullets = []

        for item_token in token.get('children', []):
            # Each child is a list_item.
            item_parts = []

            for child in item_token.get('children', []):
                # Extract the contents of block_text or paragraph.
                if child['type'] in ('block_text', 'paragraph'):
                    item_text = self.render_tokens(
                        child.get('children', []), state
                    )
                    if item_text:
                        item_parts.append(item_text)

            item_text = " ".join(item_parts).strip()

            if item_text:
                # self.queue.append((style, item_text))
                bullets.append(item_text)
                # logger.debug(f"AST list item [{item_text}]")

        # put the list generation here
        rlobj = []
        # sty_bullet.bulletType = "1"
        sty_bullet = self.styles.get("bullet")
        if style == "numbered_list":
            bullet_opts = {"bulletType":"1", 'bulletFontSize': sty_bullet.fontSize}
        else:
            bullet_opts = {"bulletType":'bullet',  'bulletFontSize': sty_bullet.fontSize}
        for b in bullets:
            rlobj.append(Paragraph(b, sty_bullet))
        self.queue.append(ListFlowable(rlobj, **bullet_opts))
        self.queue.append(Spacer(1, sty_bullet.leading))
        return ""

    def block_quote(self, token: dict, state: mistune.BlockState) -> str:
        text = "<br/><br/>".join(
            self.render_tokens(child.get("children", []), state)
            for child in token.get("children", [])
            if child.get("type") in ("paragraph", "block_text")
        )
        para_style = self.styles.derive(self.styles.get("body"), {"font.color": "purple", "left_indent":10})
        self.queue.append(Paragraph(text, para_style))
        # logger.debug(f"BLOCK QUOTE ENGAGE {text}.")
        return ""

    def block_code(self, token: dict, state: mistune.BlockState) -> str:
        code = token.get('raw', '')
        self._append_preformatted(code)
        # self.queue.append(("code_block", code.strip()))
        return ""

    def _append_preformatted(self, text: str) -> None:
        sty_code = self.styles.derive(self.styles.get("body"),{"font.name": "Courier", "space.after": 0})
        self.queue.append(XPreformatted(text, sty_code))

    def table(self, token: dict, state: mistune.BlockState) -> str:
        rows = []
        alignments = []
        for section in token.get("children", []):
            if section.get("type") == "table_head":
                cells = section.get("children", [])
                alignments = [
                    cell.get("attrs", {}).get("align")
                    for cell in cells
                ]
                rows.append(cells)
            elif section.get("type") == "table_body":
                rows.extend(
                    row.get("children", [])
                    for row in section.get("children", [])
                )

        if not rows:
            return ""

        rendered_rows = [
            [
                self.render_tokens(cell.get("children", []), state)
                for cell in row
            ]
            for row in rows
        ]
        column_count = max(len(row) for row in rendered_rows)
        widths = [
            max(
                (
                    len(re.sub(r"</?(?:b|i)>", "", row[index]))
                    for row in rendered_rows
                    if index < len(row)
                ),
                default=0,
            )
            for index in range(column_count)
        ]

        def format_row(row: list[str]) -> str:
            cells = []
            for index, width in enumerate(widths):
                value = row[index] if index < len(row) else ""
                visible_width = len(re.sub(r"</?(?:b|i)>", "", value))
                alignment = alignments[index] if index < len(alignments) else None
                padding = width - visible_width
                if alignment == "right":
                    left_padding, right_padding = padding, 0
                elif alignment == "center":
                    left_padding = padding // 2
                    right_padding = padding - left_padding
                else:
                    left_padding, right_padding = 0, padding
                cells.append(
                    f" {' ' * left_padding}{value}{' ' * right_padding} "
                )
            return "|" + "|".join(cells) + "|"

        table_lines = [format_row(rendered_rows[0])]
        table_lines.append(
            "|" + "|".join("-" * (width + 2) for width in widths) + "|"
        )
        table_lines.extend(format_row(row) for row in rendered_rows[1:])
        self._append_preformatted("\n".join(table_lines))
        return ""

    # --- CATCH-ALL FOR UNHANDLED TYPES ---
    def __getattr__(self, name: str):
        """Silently catch and skip any unhandled markdown tokens (e.g. tables, thematic breaks)."""
        def skip_handler(token: dict, state: mistune.BlockState):
            return ""
        return skip_handler
