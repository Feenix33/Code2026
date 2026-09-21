"""
runoff style text processor
"""
from processors.base import Processor
from collections import deque
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

from reportlab.platypus import Frame, Paragraph, Spacer #, PageBreak
from reportlab.platypus import ListFlowable

from processors.reportlab_style_gen import ReportLabStyleProvider
from utility import string_to_args

import logging
logger = logging.getLogger(__name__)
# from pprint import pprint
# import json
# from dataclasses import dataclass, asdict


"""
Note that this worked
         fifo.append(Paragraph(line, styles.get("body", spaceAfter=20)))

Implemented:
    .h1 string      Puts only the string in H1 style
    .h2 string      Puts only the string in H2 style
    .ft string      Modifies the body style with the arguements in string (font, leading)
    .ft             Resets current style to default body style

    List Style I
    .list opt       Start a list and pass the list arguments
    .le[nd]         End the list
    .li             List item
    .item           List item

    List Style II
    .bi string      Bullet list item
    .be[nd]         Bullet list end - adds a spacer

nroff/troff commands
    .ft B switches the font to Bold
    .ft I switches the font to Italic
    .ft R switches the font to Roman (regular text).

    .ft BI
    This entire line will be both bold and italic.
    .ft R

    \fB switches the following text to Bold.
    \fI switches the following text to Italic.
    \fR switches the following text to Roman.
    \fP returns the text to the Previous font style.
    This is \fBbold\fP and this is \fIitalic\fP text.

    Use .ps 12 to set the point size to 12 points.
    .ps 16       \" Set font size to 16 points
    .vs 18       \" Adjust vertical spacing to match the larger text

    .gcolor blue
    This text will be blue.
    .gcolor
    This text reverts back to the default color.

    .bu
    First bullet item.
    .bu
    Second bullet item.

    .np
    This automatically prints as 1.
    .np
    This automatically prints as 2.
    If there is a break and then another .np, the numbering will have automatically reset back to 1

    Alternative package:
    .AL                        \" Start Auto-numbered List block (starts at 1)
    .LI
    First item of List A.      \" Prints "1."
    .LI
    Second item of List A.     \" Prints "2."
    .LE                        \" End List A
"""


"""
start: The starting index or bullet symbol for the list (e.g., integer 1, string 'A', or custom symbol like '-')
style: A style object or named style configuration for the list
bulletType: The type of list markers. Common options include '1' (arabic numerals), 'a' or 'A' (letters), 'i' or 'I' (Roman numerals), or 'bullet' (standard symbols)
bulletColor: Color of the bullet or number (e.g., 'black', colors.red, or hex strings)
bulletFontName: Font family used for the bullet characters/numbers (defaults to 'Helvetica')
bulletFontSize: Font size for the bullets or numbering in points (defaults to 12)
bulletOffsetY: Vertical offset adjustment for the bullet position in points (+ve moves it up, -ve down)
bulletDedent: Controls how bullet indentations align; defaults to 'auto'
bulletDir: Text direction for bullets, such as 'ltr' (left-to-right)
bulletFormat: Optional callable or format string pattern to modify number/letter outputs (e.g., adding parentheses or custom prefixes)
**kwds: Additional layout properties like leftIndent, rightIndent, spaceBefore, and spaceAfter

"""
DEFAULT_BULLET_LISTFLOW_ARGUMENTS = \
    "start=None, " \
    "style=None, " \
    "bulletType='1', " \
    "bulletColor='black', " \
    "bulletFontName='Helvetica', "\
    "bulletFontSize=8, " \
    "bulletOffsetY=0, " \
    "bulletDedent='auto', " \
    "bulletDir='ltr', " \
    "bulletFormat=None" 


class RoffProcessor(Processor):

    #def process(self, text, rlstyles:ReportLabStyles, titletext=None, space_after=None, first_line=False, blanks=False, **kwargs):
    def process(self, text, styles:ReportLabStyleProvider, **kwargs):

        def _handle_acc():
            nonlocal acc, fifo, current_style
            if len(acc) > 0:
                paratext = " ".join(acc)
                fifo.append(Paragraph(paratext, current_style))
                acc = [] # clear out the accumulator

        def _text_modifier(mod: str, text:str):
            # add html markers around the text and return
            return "<"+ mod +">" +text+ "</"+ mod +">"

        def resolve_style(tag: str, style_name: str) -> Style:
            """Derives a style if overrides exist, otherwise returns the base style."""
            base_style = styles.get(style_name)
            override = style_overrides.get(tag)
            return styles.derive(base_style, override) if override else base_style


        # text is the data to process
        fifo = deque() # holds the reportlab objects 
        acc = [] # accumulator to join lines
        bullets = [] # accumulator for bullets
        bullet_opts = {} # bullet options
        current_style = styles.get("body")
        marker_overrides = {}
        style_overrides = {}

        # the lexer
        for line in text:
            line = line.rstrip()
            if not line:
                _handle_acc()
            elif line.startswith("#"): # skip the comment
                continue
            elif line.startswith("."):
                # logger.debug(f"roff command {line}")
                cmd, _, args = line.partition(' ')
                cmd = cmd[1:].lower()

                # Handle regular text if present
                match cmd:
                    # case "b":
                    #     acc.append(_text_modifier("b", args))
                    case "b" | "u" | "i" | "strike" | "strong":
                        acc.append(_text_modifier(cmd, args))

                    case "bi":
                        acc.append("<b><i>" + args + "</i></b>")

                    case "biu":
                        acc.append("<b><i><u>" + args + "</u></i></b>")

                    case "bu":
                        acc.append("<b><u>" + args + "</u></b>")

                    case "h1":
                        _handle_acc()
                        use_style = resolve_style("h1", "heading1")
                        fifo.append(Paragraph(args, use_style))

                    case "h2":
                        _handle_acc()
                        use_style = resolve_style("h2", "heading2")
                        fifo.append(Paragraph(args, use_style))

                    case "ft": # change current style
                        if len(args) == 0:
                            current_style = styles.get("body")
                        else:
                            myargs = string_to_args(args)
                            current_style = styles.derive(styles.get("body"), myargs)

                    # List Style I
                    case "list": # opt       Start a list and pass the list arguments
                        _handle_acc()
                        arg_str = DEFAULT_BULLET_LISTFLOW_ARGUMENTS
                        arg_str = arg_str + ", "  + args
                        bullet_opts = string_to_args(arg_str)
                        # bullet_opts["spaceAfter"] = 20

                    case "lend": # [nd]         End the list
                        rlobj = []
                        use_style = resolve_style("bullet", "bullet")
                        for b in bullets:
                            rlobj.append(Paragraph(b, use_style))
                            # print (f"----------> {bullet_opts}")
                        fifo.append(ListFlowable(rlobj, **bullet_opts))
                                    
                    case "li" | "item": # list item
                        bullets.append(args)

                    # List Style II
                    case "bi": # bullet item
                        # temp_style = styles.get("bullet")
                        _handle_acc()
                        use_style = resolve_style("bullet", "bullet")
                        mark = styles.get_marker("bullet", **marker_overrides)
                        fifo.append(Paragraph(args, use_style, bulletText=mark.text))  # "•"

                    case "bm": # change bullet marker
                        if len(args) == 0:
                            marker_overrides = {}
                        else:
                            marker_overrides = string_to_args(args)
                            logger.debug(f"Marker overrides = {args}")

                    case "be" | "ben" | "bend": # bullet list end
                        temp_style = styles.get("bullet")
                        fifo.append(Spacer(1, temp_style.leading))

                    case "vs": # vertical space
                        _handle_acc()
                        if len(args) == 0:
                            fifo.append(Spacer(1, current_style.leading))
                        else:
                            fifo.append(Spacer(1, int(args)))

                    case "style": # set style overrides
                        logger.debug(f"style {len(args)}: {args}")
                        style_id, _, mods = args.partition(' ')
                        style_overrides[style_id] = string_to_args(mods)
                        logger.debug(f"{style_id} overrides are {style_overrides[style_id]}")
                    case _:
                        logger.error(f"Unhandled command '{cmd}'")
            else:
                acc.append(line)

        _handle_acc()

        return fifo