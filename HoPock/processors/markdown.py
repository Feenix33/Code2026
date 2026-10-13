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
from reportlab.platypus import Frame, Paragraph, Spacer #, PageBreak
from processors.reportlab_style_gen import ReportLabStyleProvider
import mistune
from mistune.renderers.markdown import MarkdownRenderer

import logging
logger = logging.getLogger(__name__)

class QueueRenderer(MarkdownRenderer):
    """Custom renderer that intercepts Markdown blocks into a flat queue.
    
    Inheriting from MarkdownRenderer automatically processes nested inline styles 
    (bold, italics, code) into formatted strings.
    """

    def __init__(self):
        super().__init__()
        self.queue = []

    # --- BLOCK HANDLERS ---
    def heading(self, token: dict, state: mistune.BlockState) -> str:
        text = self.render_children(token, state)
        level = token['attrs']['level']
        self.queue.append((f"h{level}", text))
        return ""

    def paragraph(self, token: dict, state: mistune.BlockState) -> str:
        text = self.render_children(token, state)
        self.queue.append(("paragraph", text))
        return ""

    def list(self, token: dict, state: mistune.BlockState) -> str:
        ordered = token['attrs'].get('ordered', False)
        style = "numbered_list" if ordered else "bullet_list"
        
        # Iterate over individual list items in children
        for item_token in token.get('children', []):
            item_text = self.render_children(item_token, state).strip()
            if item_text:
                self.queue.append((style, item_text))
        return ""

    def block_quote(self, token: dict, state: mistune.BlockState) -> str:
        text = self.render_children(token, state)
        self.queue.append(("blockquote", text.strip()))
        return ""

    def block_code(self, token: dict, state: mistune.BlockState) -> str:
        code = token.get('raw', '')
        self.queue.append(("code_block", code.strip()))
        return ""

    # --- CATCH-ALL FOR UNHANDLED TYPES ---
    def __getattr__(self, name: str):
        """Silently catch and skip any unhandled markdown tokens (e.g. tables, thematic breaks)."""
        def skip_handler(token: dict, state: mistune.BlockState):
            return ""
        return skip_handler

## ================================================================================================================

class MarkdownProcessor(Processor):

    def process(self, text, styles:ReportLabStyleProvider, titletext=None, **kwargs):
        fifo = deque()
        logger.debug ("Markdown processor ENGAGED")

        sty_body = styles.get("body")
        sty_heading1 = styles.get("heading1")
        sty_heading2 = styles.get("heading2")
        # sty_bullet = styles.get("bullet")

        sty_code = styles.derive(styles.get("body"),{"font.name": "Courier", "space.after": 0})

        marker = styles.get_marker("bullet")
        sty_bullet = styles.derive(
            styles.get("body"),
                {"space.after": 0, "font.color":"blue"}
            )
        
        marker = styles.get_marker("bullet")
        sty_numbered = styles.derive(
            styles.get("body"),
                {"space.after": 0, "font.color":"green"}
            )    


        renderer = QueueRenderer()
        markdown = mistune.create_markdown(renderer=renderer, plugins=['table'])
        markdown('\n'.join(text))

        for style, ptext in renderer.queue:
            match style:
                case 'h1':
                    style = sty_heading1
                case 'h2':
                    style = sty_heading2
                case 'bullet_list':
                    style = sty_bullet
                    logger.debug(f"Bullet: {ptext}")
                case 'numbered_list':
                    style = sty_numbered
                    logger.debug(f"Bullet: {ptext}")
                case 'code_block':
                    style = sty_code
                    logger.debug(f"Code block")
                case _: # default
                  style = sty_body
            fifo.append(Paragraph(ptext, style))
 
        return fifo

        # if titletext and len(titletext) > 0:
        #     fifo.append(Paragraph(titletext, styles.get("Title")))

        # for line in text:
        #     command = line.split(" ", 1)[0]
        #     remainder = line.split(" ", 1)[1]
        #     if command == "#":
        #         style = sty_heading1
        #         line = remainder
        #     elif command.startswith("##"):
        #         style = sty_heading2
        #         line = remainder
        #     else:
        #         style = sty_body
        #     fifo.append(Paragraph(line, style))
        # return fifo