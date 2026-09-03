"""
Get the reportlab styles generated on the fly
This is used by the processors
"""
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Frame, Paragraph, Spacer #, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

class ReportLabStyleProvider:

    def __init__(self, style):
        self.style = style
        self._styles = {}

    def get(self, name, **overrides):
        name = name.lower()

        key = (
            name,
            tuple(sorted(overrides.items()))
        )

        if key not in self._styles:
            self._styles[key] = self._create_style(
                name,
                overrides
            )

        return self._styles[key]

    def _create_style(self, name, overrides):

        text_style = getattr(self.style, name)

        font = text_style.font

        alignment_map = {
            "left": TA_LEFT,
            "center": TA_CENTER,
            "right": TA_RIGHT,
            "justify": TA_JUSTIFY,
        }

        properties = {
            "name": name,
            "fontName": font.name or "Helvetica",
            "fontSize": font.size or 8,
            "textColor": font.color or "black",
            "leading": text_style.leading or 10,
            "spaceAfter": text_style.space_after or 0,
            "spaceBefore": text_style.space_before or 0,
            "alignment": alignment_map.get((text_style.alignment or "left").lower(), TA_LEFT),
        }

        properties.update(overrides)

        return ParagraphStyle(**properties)
